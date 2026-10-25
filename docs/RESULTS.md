# Initial experimental results

These are exploratory results from one temperature sensor, not a final written report.
Usable study coverage: 5,871 temperature observations from May 1 to June 13, 2024 UTC.
The nominal date filter extends through December, but does not create missing coverage.
Median interval: 600 seconds; 95th percentile interval: 1,200 seconds.

## Validation and test MAE

Each cell is the mean of 30 window MAEs, in deg C. Methods share the same masks.

| Method | Validation 30 min | Validation 60 min | Test 30 min | Test 60 min |
|---|---:|---:|---:|---:|
| forward_fill | 0.0681 | 0.1560 | 0.1400 | 0.2928 |
| linear | 0.0529 | 0.1010 | 0.0795 | 0.1450 |
| cubic | 0.0971 | 0.1333 | 0.0960 | 0.1606 |
| pchip | 0.0537 | 0.0898 | 0.0708 | 0.1269 |

Linear interpolation has the lowest validation MAE at 30 minutes, narrowly ahead of PCHIP.
PCHIP has the lowest validation MAE at 60 minutes and lower mean test MAE at both lengths.
These numerical rankings do not establish statistical significance or universal superiority.
Cubic smoothness alone does not guarantee more accurate reconstruction.

## Specific case

The included development 60-minute window 0 hides six readings on May 21, 2024.
Its recorded values are 24.0, 24.0, 24.0, 24.0, 23.8 and 23.8 deg C.
Forward fill has MAE 0.0667 deg C, linear 0.1835, natural cubic 0.2121 and PCHIP 0.1835.
Forward fill works well here because the hidden series remains nearly constant before
falling late in the gap. This is not a contradictory overall ranking: one case is
not the mean across many windows. The case is selected by saved seeded window index,
not by minimum model error.

## Limits and remaining work

No eligible 120-minute masks exist under the current continuity/context criteria.
Do not assign an error to that duration or treat absence of evidence as successful repair.
No sensor calibration, real outage causation, actual heat-load estimate or multiroom
generalisation has been established. The initial test scores have already been viewed.
The added context-length analysis is in SENSITIVITY.md. Final student review
and justification remain necessary.
Existing figures and CSVs support the initial study; a final report must interpret them.
Runtime measurements are machine-specific and can change on every rerun.
