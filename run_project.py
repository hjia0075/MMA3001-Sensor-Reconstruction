"""Run the portable environmental sensor reconstruction pipeline.

Use ``python run_project.py`` after placing the authorised CSV in data/raw,
or ``python run_project.py --input /path/to/environmental.csv``.
"""
import argparse
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".cache/matplotlib"))

from reconstruction import prepare, benchmark
from case_comparison import export_case


def resolve_input_path(value: str, root: Path = ROOT) -> Path:
    """Resolve an expanded absolute path or a repository-relative data path.

    Args:
        value: Input filename, with optional user-home expansion.
        root: Base directory used for relative filenames.

    Returns:
        Absolute input path; existence is checked by the pipeline.
    """
    path = Path(value).expanduser()
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def main() -> None:
    """Read portable configuration, validate input and produce results.

    A command-line input overrides MMA3001_INPUT_CSV, which overrides the
    configured filename. The shared configuration is never overwritten.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", help="Override the environmental CSV path")
    args = parser.parse_args()
    config = json.loads((ROOT / "project_config.json").read_text(encoding="utf-8"))
    value = args.input or os.environ.get("MMA3001_INPUT_CSV") or config["input_csv"]
    source = resolve_input_path(value)
    if not source.is_file():
        parser.error("Input CSV not found. Put the authorised environmental CSV in data/raw "
                     "or provide --input /path/to/file.csv. See data/raw/README.md.")
    if config["variable"] != "Temperature":
        parser.error("This submission pipeline is scoped to Temperature.")
    durations = config["gap_minutes"]
    if config["windows_per_group"] < 1 or not durations or any(v <= 0 for v in durations):
        parser.error("Use positive gap durations and windows_per_group.")
    processed, results = ROOT / "data/processed", ROOT / "results/temperature"
    print("[1/3] Decode and clean actual observations.", flush=True)
    prepare(source, processed, config["start_utc"], config["end_utc_exclusive"])
    print("[2/3] Compare methods on identical artificial outages.", flush=True)
    benchmark(processed / "observations.csv", results, config["variable"], durations,
              config["windows_per_group"], config["seed"])
    print("[3/3] Export the first available development example.", flush=True)
    import pandas as pd
    masks = pd.read_csv(results / "mask_coverage.csv")
    available = masks[(masks.split == "development") & (masks.selected_windows > 0)]
    if available.empty:
        print("No development example is available; inspect mask_coverage.csv.")
    else:
        gap = 60 if 60 in available.gap_minutes.values else int(available.gap_minutes.iloc[0])
        export_case(minutes=gap)
    print(f"Finished. Results: {results}")
    print("Unsupported gap lengths have zero selected windows in mask_coverage.csv.")


if __name__ == "__main__":
    main()
