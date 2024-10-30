@echo off
setlocal

call ./venv/Scripts/activate.bat

:: List of Python files to run
set "python_files=./scripts/data_ingestion/spotify_data_ingestion.py ./scripts/data_ingestion/ticketmaster_data_ingestion.py ./scripts/landing/raw2temporal.py ./scripts/landing/temporal2persistent.py ./scripts/formatted/landing2formatted.py ./scripts/trusted/formatted2trusted.py ./scripts/trusted/generic_data_quality/deduplication.py ./scripts/trusted/generic_data_quality/consistent_formatting.py ./scripts/trusted/generic_data_quality/misspellings.py ./scripts/exploitation/trusted2exploitation.py"

:: Check for --skip-ingestion flag
if "%~1"=="--skip-ingestion" (
    set "python_files=./scripts/landing/raw2temporal.py ./scripts/landing/temporal2persistent.py ./scripts/formatted/landing2formatted.py ./scripts/trusted/formatted2trusted.py ./scripts/trusted/generic_data_quality/deduplication.py ./scripts/trusted/generic_data_quality/consistent_formatting.py ./scripts/trusted/generic_data_quality/misspellings.py ./scripts/exploitation/trusted2exploitation.py"
)

:: New command line with system metrics
start cmd /k "tasklist"

:: Run each Python script
for %%f in (%python_files%) do (
    echo Running %%f...
    python %%f
)

:: Deactivate the virtual environment
deactivate
endlocal
