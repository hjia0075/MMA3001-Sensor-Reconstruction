# Input data

Obtain `5EnvSensor_MayToDec2024_180kRows.csv` from the authorised MMA3001 teaching
team dataset distribution. It is not included or downloaded automatically.
No public dataset URL or redistribution permission has been established.

Place the file here, or use `python run_project.py --input /path/to/file.csv`.
The reader requires `sensorid` and `jsondata` columns; each JSON variable
contains its name, unit and time/value observations. Times are Unix seconds.
The original source includes dates outside its filename's apparent range.

Raw data and the full generated `data/processed/observations.csv` are ignored
by Git. The original CSV is never overwritten. Retain local access to it for
reproduction. Occupancy CSV and the location spreadsheet are not required.
