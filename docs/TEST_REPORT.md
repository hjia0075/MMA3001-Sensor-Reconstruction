# Verification report

Local verification date: October 26, 2026 (Australia/Hobart).

Result: 21 tests, 0 failures,
0 errors, 0 skipped.
The machine-readable report is `results/tests.xml`.

## Coverage

- Analytical linear-function recovery for linear, natural cubic and PCHIP.
- Reproduction of observations at interpolation nodes.
- Correct forward-hold semantics; no use of a future reading for hold.
- Rejection of duplicate/unordered times, nonfinite input and extrapolation.
- PCHIP range on monotone input and original-continuity mask checks.
- Per-channel missing values and conflicting duplicate exclusion.
- Predictions unaffected by changes to hidden reference values.
- Known values unchanged and signed error definition verified.
- Repository-relative input resolution independent of current working directory.
- Absolute input override preserved.

Run from the repository root:

```sh
python -m pytest --junitxml=results/tests.xml
```

Tests use synthetic temporary inputs and need no private course dataset.
They verify implementation, not the physical accuracy of sensor readings.
A separate real-data pipeline run verifies data ingestion and end-to-end output.
No GitHub-hosted test run or cloud Colab interface execution is claimed.

Additional tests verify common 2/4/8-node mask availability, continuous masked
cores and isolation of hidden reference values for every context/method.
