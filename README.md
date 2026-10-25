# Missing Environmental Sensor Data Reconstruction

MMA3001 Numerical Methods and Machine Learning individual project.

This project compares forward fill, linear interpolation, natural cubic splines
and PCHIP for offline reconstruction of missing building-temperature records.
It evaluates artificially hidden observations against their original readings.

**Status:** English computational package with real-data benchmark evidence,
paired context sensitivity, 21 passing verification tests and HTML API documentation.
The written report is supplied separately. Student review, personal AI reflection,
GitHub publication and presentation remain required.

## Research question and scope

How do reconstruction accuracy, shape and runtime change with 30-minute and
60-minute contiguous outages? The initial study uses four known observations
on either side. Future context is available, so this is retrospective repair,
not real-time forecasting. No machine-learning training is required.

The initial study-date filter is May-December 2024 UTC. Actual usable temperature
coverage is one sensor, May 1-June 13, with 5,871 readings and median cadence
600 seconds. No eligible 120-minute windows satisfy the continuity/context rules.
An unsupported duration is not assigned a fabricated error.

## Quick start

Use Python 3.12. The exact environment for the latest run is recorded in
`requirements-lock.txt`; `requirements.txt` provides supported version ranges. From this repository directory on macOS/Linux:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python run_project.py --input /path/to/5EnvSensor_MayToDec2024_180kRows.csv
```

On Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python run_project.py --input "C:\path\to\5EnvSensor_MayToDec2024_180kRows.csv"
```

Alternatively, put the authorised CSV at the relative path in
`project_config.json` and run `python run_project.py`. The environment variable
`MMA3001_INPUT_CSV` is another input override. No data is bundled or uploaded by
the runner. Permission to obtain the course dataset is required for real-data
reproduction; tests run without it. See [data/raw/README.md](data/raw/README.md).

## Other entry points

```sh
python reconstruction.py prepare --input /path/to/environmental.csv
python reconstruction.py benchmark
python case_comparison.py --minutes 60 --split development --window-id 0
python sensitivity_analysis.py
python -m pytest --junitxml=results/tests.xml
python -m pdoc reconstruction case_comparison run_project -o docs/html
```

For VS Code, open this folder, select the newly created `.venv` interpreter,
open `run_project.py` and choose Run Python File. Data must be placed at the
configured path first. The Python scripts are the entry points included in this
repository. Colab and editor-specific settings are not required.

## Outputs and interpretation

- `data/processed/audit.json`: cleaning counts and measurement-date range.
- `data/processed/coverage.csv`: available readings and cadence by variable.
- `results/temperature/summary.csv`: window-level error/runtime aggregation.
- `results/temperature/pointwise_predictions.csv`: each hidden reference,
  prediction and signed/absolute error.
- `results/temperature/details/`: specific-case tables and figures.
- `results/tests.xml`: machine-readable verification report.
- `docs/html/index.html`: generated source-code documentation.

MAE/RMSE use deg C, runtime uses milliseconds, and temperature integral error
uses deg C h. Errors close to zero indicate close reconstruction; they are not
absolute predicted temperatures. Read [docs/METHODS.md](docs/METHODS.md) and
[docs/RESULTS.md](docs/RESULTS.md) for interpretation and limitations.

## Reproducibility and evaluation

Use seed 3001 and the supplied configuration. Development/validation/test are
chronological 60/20/20 calendar-span partitions; known context cannot cross a
boundary. Masks share the same observed input across methods. No filled grid
values are used as ground truth. Runtime varies with the machine and load.

The original test results have already been examined. Parameter changes must
use development/validation evidence; any test-guided iteration is exploratory
unless independently evaluated. This repository does not claim a new untouched
holdout. The additional sensitivity study uses paired development/validation
masks with separate, explicitly documented context continuity rules.

## Documentation

- [docs/METHODS.md](docs/METHODS.md): methods, assumptions and metric definitions.
- [docs/SENSITIVITY.md](docs/SENSITIVITY.md): paired 2/4/8-node context analysis.
- [docs/RESULTS.md](docs/RESULTS.md): findings and limitations.
- [docs/TEST_REPORT.md](docs/TEST_REPORT.md): verification coverage and results.
- [docs/AI_USE.md](docs/AI_USE.md): substantial AI contribution and review needs.
- [docs/REFERENCES.md](docs/REFERENCES.md): course and method sources.

The MIT license covers authored software/documentation only. It does not grant
rights to the course dataset, course materials or derived measurement records.
Included real-data results remain subject to the data owner's restrictions;
confirm permission before making a public repository. No remote publication
has been performed.
