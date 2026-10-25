"""Verification on analytical curves and invalid input boundaries."""
import numpy as np
import pytest
from reconstruction import reconstruct, candidate_windows, prepare


@pytest.mark.parametrize("method", ["linear", "cubic", "pchip"])
def test_linear_curve_recovered(method):
    x = np.array([0, 1, 5, 6.])
    q = np.array([2, 3, 4.])
    np.testing.assert_allclose(reconstruct(x, 2*x+7, q, method), 2*q+7)


def test_hold_uses_previous_not_future_value():
    np.testing.assert_equal(reconstruct([0, 4], [3, 9], [1, 3, 4], "forward_fill"), [3, 3, 9])


@pytest.mark.parametrize("method", ["forward_fill", "linear", "cubic", "pchip"])
def test_nodes_recovered(method):
    x = [0, 2, 3, 7]
    y = [8, 1, 5, 3]
    np.testing.assert_allclose(reconstruct(x, y, x, method), y)


@pytest.mark.parametrize("x,y,q", [([0,0],[1,2],[0]), ([0,1],[1,2],[2]),
                                      ([0,1],[1,np.nan],[.5]), ([1,0],[1,2],[.5])])
def test_invalid_input_rejected(x,y,q):
    with pytest.raises(ValueError):
        reconstruct(x,y,q,"linear")


def test_pchip_no_overshoot_on_monotone_nodes():
    pred = reconstruct([0,1,4,5], [1,2,2.1,9], np.linspace(1,4,100), "pchip")
    assert pred.min() >= 2 and pred.max() <= 2.1


def test_windows_reject_existing_outage_and_keep_context():
    t = np.r_[np.arange(15)*60, 5000+np.arange(15)*60]
    windows = candidate_windows(t, 300)
    assert windows
    for i,j in windows:
        assert j-i >= 3
        assert np.max(np.diff(t[i-4:j+4])) <= 90
        assert i >= 4 and j+4 <= len(t)


def test_prepare_preserves_values_after_missing_channel_and_excludes_conflict(tmp_path):
    import json
    import pandas as pd
    rows = []
    for temperature in [20, 20, 21]:
        payload = [{"variable": {"name": "Formaldehyde", "unit": "ug/m3"},
                    "values": [{"time": 1714521600}]},
                   {"variable": {"name": "Temperature", "unit": "deg C"},
                    "values": [{"time": 1714521600, "value": temperature},
                               {"time": 1714522200, "value": 22}]}]
        rows.append({"sensorid": "123", "jsondata": json.dumps(payload)})
    source = tmp_path / "raw.csv"
    pd.DataFrame(rows).to_csv(source, index=False)
    prepare(source, tmp_path / "out", "2024-05-01", "2025-01-01")
    clean = pd.read_csv(tmp_path / "out/observations.csv")
    assert clean.value.tolist() == [22]
    audit = json.loads((tmp_path / "out/audit.json").read_text())
    assert audit["missing_value_points"] == 3
    assert audit["conflicting_keys_excluded"] == 1
    assert audit["malformed_payloads"] == 0
