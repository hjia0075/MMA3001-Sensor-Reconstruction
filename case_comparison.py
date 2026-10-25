"""Export a specific masked outage, its predictions and observed-reference errors.

Default example is development window 0 for a 60-minute outage: selected by
the existing seeded benchmark, not chosen by lowest prediction error.
Run ``python case_comparison.py`` after the benchmark.
"""
import argparse
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

from reconstruction import METHODS, ROOT, reconstruct

os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".cache/matplotlib"))


def comparison_tables(t, y, i, j):
    """Return context and hidden-point tables plus method error metrics.

    Hide indices [i,j); fit using exactly four known nodes on either side.
    Known readings remain unchanged in the completed series. Signed error is
    prediction minus original. Reference values never enter interpolator input.
    """
    t, y = np.asarray(t, float), np.asarray(y, float)
    if i < 4 or j+4 > len(t) or j <= i:
        raise ValueError("Need a nonempty hidden window and four context nodes each side")
    if len(t) != len(y) or not np.isfinite(y).all() or np.any(np.diff(t) <= 0):
        raise ValueError("Require finite values, matching arrays, and increasing times")
    indices = np.r_[np.arange(i-4, i), np.arange(j, j+4)]
    q = t[i:j]-t[i-1]
    all_t, all_y = t[i-4:j+4], y[i-4:j+4]
    hidden = np.zeros(len(all_t), bool)
    hidden[4:4+j-i] = True
    context = pd.DataFrame({"timestamp_utc": pd.to_datetime(all_t, unit="s", utc=True),
                            "is_hidden": hidden, "original_value": all_y,
                            "input_after_mask": np.where(hidden, np.nan, all_y)})
    context["timestamp_melbourne"] = context.timestamp_utc.dt.tz_convert("Australia/Melbourne")
    metrics = []
    for method in METHODS:
        pred = reconstruct(t[indices]-t[i-1], y[indices], q, method)
        completed = all_y.copy(); completed[hidden] = pred
        error = pred-y[i:j]
        context[f"{method}_prediction"] = completed
        context[f"{method}_signed_error"] = np.where(hidden, completed-all_y, np.nan)
        context[f"{method}_absolute_error"] = np.where(hidden, abs(completed-all_y), np.nan)
        metrics.append({"method": method, "hidden_points": j-i,
                        "mae": float(np.mean(abs(error))),
                        "rmse": float(np.sqrt(np.mean(error**2))),
                        "max_absolute_error": float(np.max(abs(error))),
                        "mean_signed_error": float(np.mean(error))})
    return context, context[hidden].copy(), pd.DataFrame(metrics)


def export_case(minutes=60, split="development", window_id=0, sensor=None):
    """Reconstruct a saved benchmark mask; export CSVs, PNGs and a case note.

    This is an offline experiment on artificially hidden observations. Real
    missing values lack an original reference for direct error calculation.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    config = json.loads((ROOT / "project_config.json").read_text())
    base = ROOT / "results/temperature"
    records = pd.read_csv(base / "window_metrics.csv", dtype={"sensor_id": str})
    rows = records[(records.split == split) & (records.gap_minutes == minutes) &
                   (records.window_id == window_id) & (records.method == "linear")]
    if sensor is not None:
        rows = rows[rows.sensor_id == str(sensor)]
    if rows.empty:
        raise ValueError("Requested window unavailable. Inspect mask_coverage.csv/window_metrics.csv")
    row = rows.iloc[0]
    data = pd.read_csv(ROOT / "data/processed/observations.csv", dtype={"sensor_id": str})
    data = data[(data.sensor_id == row.sensor_id) &
                (data.variable == config["variable"])].sort_values("time_s")
    t, y = data.time_s.to_numpy(), data.value.to_numpy()
    start = pd.Timestamp(row.start_utc).timestamp()
    i = int(np.searchsorted(t, start)); j = int(np.searchsorted(t, start+minutes*60))
    if i == len(t) or t[i] != start or j-i != int(row.hidden_points):
        raise ValueError("Saved mask does not match current cleaned observations; rerun benchmark")
    context, points, metrics = comparison_tables(t, y, i, j)
    # Cross-check that this specific reconstruction matches the saved benchmark.
    for method in METHODS:
        saved = records[(records.sensor_id == row.sensor_id) & (records.split == split) &
                        (records.gap_minutes == minutes) & (records.window_id == window_id) &
                        (records.method == method)].iloc[0]
        actual = metrics[metrics.method == method].iloc[0]
        if not np.isclose(saved.mae, actual.mae, atol=1e-10):
            raise ValueError("Detailed case and saved benchmark disagree")
    output = base / "details" / f"{split}_{minutes}min_window{window_id}_{row.sensor_id}"
    output.mkdir(parents=True, exist_ok=True)
    context.to_csv(output / "full_context.csv", index=False)
    points.to_csv(output / "missing_point_comparison.csv", index=False)
    metrics.to_csv(output / "method_metrics.csv", index=False)
    names = {"forward_fill": "Forward fill", "linear": "Linear", "cubic": "Natural cubic", "pchip": "PCHIP"}
    colors = {"forward_fill": "#0072B2", "linear": "#E69F00", "cubic": "#009E73", "pchip": "#CC79A7"}
    unit = "deg C" if config["variable"] == "Temperature" else "source units"
    origin = context.timestamp_utc.iloc[0]
    x = (context.timestamp_utc-origin).dt.total_seconds()/60
    xp = (points.timestamp_utc-origin).dt.total_seconds()/60
    left, right = (start-t[i-4])/60, (start+minutes*60-t[i-4])/60
    fig, axes = plt.subplots(3, 1, figsize=(11, 10), sharex=True)
    axes[0].plot(x, context.original_value, "k.-", label="Original observations (reference)")
    axes[0].plot(x, context.input_after_mask, "o-", color="#0072B2", label="Available input after masking")
    for method in METHODS:
        axes[1].plot(xp, points[f"{method}_prediction"], ".--", color=colors[method], label=names[method])
        axes[2].plot(xp, points[f"{method}_signed_error"], "o-", color=colors[method], label=names[method])
    axes[1].plot(x, context.original_value, "k.-", label="Original observations (reference)")
    axes[2].axhline(0, color="black", lw=1)
    axes[0].set_title(f"Sensor {row.sensor_id}: {minutes}-minute masked outage\nStart: {row.start_utc} (UTC)")
    for ax in axes:
        ax.axvspan(left, right, alpha=.12, color="grey")
        ax.grid(alpha=.2); ax.legend(fontsize=9, loc="best")
    axes[0].set_ylabel(f"Input/reference ({unit})")
    axes[1].set_ylabel(f"Reconstructed value ({unit})")
    axes[2].set_ylabel(f"Prediction - original ({unit})")
    axes[2].set_xlabel("Minutes from first displayed context observation")
    fig.tight_layout(); fig.savefig(output / "reconstruction_and_error.png", dpi=180); plt.close(fig)
    # Separate panels make overlapping predictions easy to inspect.
    fig, axes = plt.subplots(2, 2, figsize=(11, 7), sharex=True, sharey=True)
    for ax, method in zip(axes.flat, METHODS):
        ax.plot(x, context.original_value, "k.-", label="Original")
        ax.plot(x, context[f"{method}_prediction"], "o--", color=colors[method], label="Completed series")
        ax.axvspan(left, right, alpha=.12, color="grey")
        score = metrics[metrics.method == method].iloc[0]
        ax.set_title(f"{names[method]} | MAE={score.mae:.4f} {unit}")
        ax.grid(alpha=.2); ax.legend(fontsize=9)
        ax.set_xlabel("Minutes from first displayed observation"); ax.set_ylabel(unit)
    fig.tight_layout(); fig.savefig(output / "methods_separately.png", dpi=180); plt.close(fig)
    (output / "case_info.json").write_text(json.dumps({"sensor_id": row.sensor_id,
        "variable": config["variable"], "split": split, "window_id": window_id,
        "start_utc": row.start_utc, "end_exclusive_utc": str(pd.to_datetime(start+minutes*60, unit="s", utc=True)),
        "gap_minutes": minutes, "hidden_points": j-i, "context_nodes_each_side": 4,
        "selection": "First saved window for requested split/duration/sensor; not error-ranked",
        "error_definition": "prediction minus original observed reading",
        "interpretation": "Artificially masked original observations, offline reconstruction"}, indent=2))
    print(f"\nDetailed example saved to: {output}")
    print(points[["timestamp_utc", "original_value"] + [f"{m}_prediction" for m in METHODS]].to_string(index=False))
    print(metrics.to_string(index=False))
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--minutes", type=int, default=60)
    parser.add_argument("--split", choices=["development", "validation", "test"], default="development")
    parser.add_argument("--window-id", type=int, default=0)
    parser.add_argument("--sensor")
    args = parser.parse_args()
    export_case(args.minutes, args.split, args.window_id, args.sensor)


if __name__ == "__main__":
    main()
