@echo off
setlocal

call ./venv/Scripts/activate.bat

echo 1
@echo off
setlocal

call ./venv/Scripts/activate.bat

echo 1

:: Check for flags and jump to the appropriate section
if "%~1"=="--skip-ingestion" goto skip_ingestion
if "%~1"=="--analysis-only" goto analysis_only

:: Default execution block
set python_files=^
./scripts/data_ingestion/spotify_data_ingestion.py ^
./scripts/data_ingestion/ticketmaster_data_ingestion.py ^
./scripts/landing/raw2temporal.py ^
./scripts/landing/temporal2persistent.py ^
./scripts/formatted/landing2formatted.py ^
./scripts/trusted/formatted2trusted.py ^
./scripts/trusted/generic_data_quality/deduplication.py ^
./scripts/trusted/generic_data_quality/consistent_formatting.py ^
./scripts/trusted/generic_data_quality/misspellings.py ^
./scripts/exploitation/trusted2exploitation.py ^
./scripts/analytical_backbone/sandbox/sandbox.py ^
./scripts/analytical_backbone/feature_engineering/data_preparation.py ^
./scripts/analytical_backbone/feature_engineering/feature_generation.py ^
./scripts/analytical_backbone/data_split/data_split.py ^
./scripts/analytical_backbone/modelling/model_generation.py ^
./scripts/analytical_backbone/modelling/external_validation.py ^
./scripts/analytical_backbone/data_augmentation/data_augmentation.py ^
./scripts/analytical_backbone/data_split/data_split.py ^
./scripts/analytical_backbone/modelling/model_generation.py ^
./scripts/analytical_backbone/modelling/external_validation.py
goto run_scripts

:skip_ingestion
echo 2
set python_files=^
./scripts/landing/raw2temporal.py ^
./scripts/landing/temporal2persistent.py ^
./scripts/formatted/landing2formatted.py ^
./scripts/trusted/formatted2trusted.py ^
./scripts/trusted/generic_data_quality/deduplication.py ^
./scripts/trusted/generic_data_quality/consistent_formatting.py ^
./scripts/trusted/generic_data_quality/misspellings.py ^
./scripts/exploitation/trusted2exploitation.py ^
./scripts/analytical_backbone/sandbox/sandbox.py ^
./scripts/analytical_backbone/feature_engineering/data_preparation.py ^
./scripts/analytical_backbone/feature_engineering/feature_generation.py ^
./scripts/analytical_backbone/data_split/data_split.py ^
./scripts/analytical_backbone/modelling/model_generation.py ^
./scripts/analytical_backbone/modelling/external_validation.py ^
./scripts/analytical_backbone/data_augmentation/data_augmentation.py ^
./scripts/analytical_backbone/data_split/data_split.py ^
./scripts/analytical_backbone/modelling/model_generation.py ^
./scripts/analytical_backbone/modelling/external_validation.py
goto run_scripts

:analysis_only
echo 3
set python_files=^
./scripts/analytical_backbone/sandbox/sandbox.py ^
./scripts/analytical_backbone/feature_engineering/data_preparation.py ^
./scripts/analytical_backbone/feature_engineering/feature_generation.py ^
./scripts/analytical_backbone/data_split/data_split.py ^
./scripts/analytical_backbone/modelling/model_generation.py ^
./scripts/analytical_backbone/modelling/external_validation.py ^
./scripts/analytical_backbone/data_augmentation/data_augmentation.py ^
./scripts/analytical_backbone/data_split/data_split.py ^
./scripts/analytical_backbone/modelling/model_generation.py ^
./scripts/analytical_backbone/modelling/external_validation.py

:run_scripts
:: Run each Python script
for %%f in (%python_files%) do (
    echo Running %%f...
    python %%f
)

:: Deactivate the virtual environment
deactivate
endlocal

