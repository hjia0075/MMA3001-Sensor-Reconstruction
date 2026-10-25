# Methods, input/output contract and evaluation

## Engineering application

Retrospectively repair building-temperature time series for later monitoring
and analysis. Communication loss is a motivating scenario; the dataset does
not identify the cause of each actual gap. The experiment does not estimate
heat load, actual energy savings, sensor calibration or drift.

## Inputs and outputs

Source CSV: `sensorid` and JSON variables containing measurement times (Unix
seconds), values and metadata. Primary response: Temperature in deg C. Records
must have finite values and valid timestamps. Duplicate identical values for
one sensor/variable/time collapse into one observation. Conflicting keys are
excluded rather than averaged. Individually missing values are skipped.
Temperature -20 to 60 deg C and CO2 0 to 20000 ppm are broad screening assumptions.
They are not universal physical bounds. No arbitrary rate clipping is applied.

Cleaned columns: sensor_id, variable, time_s, value, timestamp_utc. Output
predictions retain the response unit. Interpolation rejects nonfinite arrays,
duplicate/unordered times, mismatched arrays and extrapolation. Values outside
the study interval are excluded. The end date is exclusive, and all filtering
uses UTC; case tables also include Australia/Melbourne local time.

## Numerical methods

Forward fill uses the last available reading. Linear interpolation joins the
bracketing points. CubicSpline uses natural boundary conditions (zero second
derivatives at the outer context endpoints). PCHIP uses local shape-preserving
cubic pieces. Each method sees the same four known points on each side;
forward fill and linear interpolation intrinsically need less of that context.
Relative seconds avoid unnecessarily large Unix-time coordinates.

## Masking and data partitions

For each sensor, split the observed calendar span 60/20/20 into development,
validation and test. Each artificial outage hides original observations in
[start, start + duration). Require at least three hidden observations, four
known nodes on each side and original adjacent intervals <=1.5 times the
sensor/split median cadence. Context never crosses partition boundaries.

Choose up to 30 seeded windows per sensor/split/duration. Within each such
group, masks including context do not overlap; overlap across different
durations is possible, so duration groups are not independent samples.
Each method receives the same masks. Mask scores are conditional on selecting
well-observed sections, not arbitrary naturally missing sections.

## Metric definitions

For window w with n hidden readings, let e_i = prediction_i - reference_i.

| Summary column | Calculation | Unit/interpretation |
|---|---|---|
| split | Chronological partition | development, validation, test |
| gap_minutes | Mask interval length | minutes |
| method | Numerical method name | category |
| windows | Number of scored windows | count |
| mean_mae | Mean of window mean(abs(e_i)) | deg C; lower is closer |
| median_mae | Median of window MAEs | deg C; typical window |
| mean_window_rmse | Mean of window sqrt(mean(e_i squared)) | deg C; emphasises large errors |
| median_runtime_ms | Median across windows of median of five timed runs | ms; build plus evaluation, excludes I/O |
| mean_integral_error | Mean abs(reconstructed integral - reference integral) | deg C h; trapezoidal rule |
| mean_endpoint_range_exceedance | Mean fraction of hidden predictions outside bracketing endpoint range | fraction, not physical error rate |

Window means are equally weighted, not pooled over all points. Integral
evaluation spans the last known point before the mask through the first known
point after it; it may exceed nominal outage duration. Integral cancellation
can hide pointwise errors. Endpoint exceedance is a shape diagnostic because
real temperatures may also turn outside the endpoint range. Timing is
machine-specific and should not be overinterpreted at submillisecond scales.

## Verification and boundaries of evidence

Tests check analytical linear recovery, exact-node reproduction, hold semantics,
invalid inputs, PCHIP monotonic range, continuity selection, missing channel
handling, conflicting observations, hidden-reference isolation and portable paths.
Recorded observations remain noisy references, not physical ground truth.

The initial test results were already viewed. Later choices should use
development/validation; new test-driven choices cannot be called independent
confirmation. A dedicated 2/4/8-context sensitivity study is now supplied; see SENSITIVITY.md
for its distinct paired-mask protocol. It does not use test data.
