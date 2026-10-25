"""Compare 2, 4 and 8 context nodes on paired development/validation masks.

The masked interval and its immediate bracketing intervals must be continuous
within 1.5 median cadences. Wider observed context may contain intervals up to
3 median cadences. This explicitly differs from the initial benchmark's strict
whole-context rule; results from the two mask pools are not directly paired.
"""
import json
import os
from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd

from reconstruction import ROOT, METHODS, reconstruct

os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".cache/matplotlib"))
CONTEXTS = (2, 4, 8)


def paired_candidates(t, duration_s, maximum_context=8):
    """Return masks that support every context length without hidden-data use.

    Selection depends only on timestamps. At least three recorded values are
    hidden. The returned [i,j) indices leave maximum_context nodes each side.
    """
    t = np.asarray(t, dtype=float)
    if len(t) < 2*maximum_context + 3:
        return []
    if np.any(np.diff(t) <= 0) or not np.isfinite(t).all():
        raise ValueError("Times must be finite and strictly increasing")
    cadence = np.median(np.diff(t))
    candidates = []
    for i in range(maximum_context, len(t)-maximum_context):
        j = int(np.searchsorted(t, t[i]+duration_s))
        if j-i < 3 or j+maximum_context > len(t):
            continue
        core = np.diff(t[i-1:j+1])
        whole = np.diff(t[i-maximum_context:j+maximum_context])
        if np.max(core) <= 1.5*cadence and np.max(whole) <= 3*cadence:
            candidates.append((i,j))
    return candidates


def context_predictions(t, y, i, j, context, method):
    """Predict hidden observations using context nodes only, preserving truth isolation."""
    if context not in CONTEXTS or i < context or j+context > len(t):
        raise ValueError("Unsupported context or insufficient known observations")
    indices = np.r_[np.arange(i-context,i), np.arange(j,j+context)]
    return reconstruct(t[indices]-t[i-1], y[indices], t[i:j]-t[i-1], method)


def main():
    """Run paired context sensitivity with fixed settings and export metrics/plot."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    data = pd.read_csv(ROOT/'data/processed/observations.csv', dtype={"sensor_id":str})
    data = data[data.variable == "Temperature"]
    rng = np.random.default_rng(3002)
    rows, coverage = [], []
    for sid,g in data.groupby('sensor_id'):
        g = g.sort_values('time_s');a,b = g.time_s.iloc[0],g.time_s.iloc[-1]
        edges=[a,a+.6*(b-a),a+.8*(b-a)]
        for split,left,right in zip(['development','validation'],edges[:-1],edges[1:]):
            part=g[(g.time_s>=left)&(g.time_s<right)]
            t,y=part.time_s.to_numpy(),part.value.to_numpy()
            for minutes in [30,60]:
                candidates=paired_candidates(t,minutes*60)
                selected=[];used=set()
                for k in rng.permutation(len(candidates)):
                    i,j=candidates[k];footprint=set(range(i-8,j+8))
                    if footprint.isdisjoint(used):
                        selected.append((i,j));used.update(footprint)
                    if len(selected)==30:break
                coverage.append(dict(sensor_id=sid,split=split,gap_minutes=minutes,
                                     candidate_windows=len(candidates),selected_windows=len(selected)))
                for window,(i,j) in enumerate(selected):
                    for context in CONTEXTS:
                        for method in METHODS:
                            times=[]
                            for _ in range(5):
                                start=perf_counter();pred=context_predictions(t,y,i,j,context,method)
                                times.append(perf_counter()-start)
                            error=pred-y[i:j]
                            rows.append(dict(sensor_id=sid,split=split,gap_minutes=minutes,
                                window_id=window,start_utc=str(pd.to_datetime(t[i],unit='s',utc=True)),
                                context_nodes_each_side=context,method=method,hidden_points=j-i,
                                mae=float(np.mean(abs(error))),rmse=float(np.sqrt(np.mean(error**2))),
                                runtime_ms=float(np.median(times)*1000)))
    output=ROOT/'results/sensitivity';output.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(coverage).to_csv(output/'mask_coverage.csv',index=False)
    records=pd.DataFrame(rows)
    if records.empty:raise ValueError("No common eligible sensitivity masks")
    records.to_csv(output/'window_metrics.csv',index=False)
    summary=records.groupby(['split','gap_minutes','context_nodes_each_side','method']).agg(
        windows=('mae','size'),mean_mae=('mae','mean'),mean_window_rmse=('rmse','mean'),
        median_runtime_ms=('runtime_ms','median')).reset_index()
    summary.to_csv(output/'summary.csv',index=False)
    settings=dict(context_nodes_each_side=list(CONTEXTS),seed=3002,gap_minutes=[30,60],
        maximum_windows=30,core_continuity_factor=1.5,observed_context_continuity_factor=3,
        partitions=['development','validation'],runtime_repeats=5,
        test_data_used=False,paired_masks=True)
    (output/'experiment_config.json').write_text(json.dumps(settings,indent=2)+'\n')
    fig,axes=plt.subplots(1,2,figsize=(10,3.6),sharey=True)
    for ax,minutes in zip(axes,[30,60]):
        for method in METHODS:
            s=summary[(summary.split=='validation')&(summary.gap_minutes==minutes)&(summary.method==method)]
            ax.plot(s.context_nodes_each_side,s.mean_mae,'o-',label=method)
        ax.set(title=f'{minutes}-minute outage',xlabel='Known nodes on each side',xticks=list(CONTEXTS))
        ax.grid(alpha=.2)
    axes[0].set_ylabel('Validation mean window MAE (deg C)');axes[1].legend(fontsize=8)
    fig.tight_layout();fig.savefig(output/'context_comparison.png',dpi=180);plt.close(fig)
    print(summary[summary.split=='validation'].to_string(index=False))
    print('Sensitivity masks:',pd.DataFrame(coverage).to_string(index=False))


if __name__=='__main__':main()
