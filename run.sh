#!/bin/bash

set -e



source ./venv/bin/activate



# List of Python files to run
python_files=(
    "./scripts/data_ingestion/spotify_data_ingestion.py"
    "./scripts/data_ingestion/ticketmaster_data_ingestion.py"
    "./scripts/landing/raw2temporal.py"
    "./scripts/landing/temporal2persistent.py"
    "./scripts/formatted/landing2formatted.py"
    "./scripts/trusted/formatted2trusted.py"
    "./scripts/trusted/generic_data_quality/deduplication.py"
    "./scripts/trusted/generic_data_quality/consistent_formatting.py"
    "./scripts/trusted/generic_data_quality/misspellings.py"
    "./scripts/exploitation/trusted2exploitation.py"
    "./scripts/analytical_backbone/sandbox/sandbox.py"
    "./scripts/analytical_backbone/feature_engineering/feature_generation.py"
    "./scripts/analytical_backbone/feature_engineering/data_preparation.py"
    "./scripts/analytical_backbone/model_generation/model_generation.py"

)



if [[ "$1" == "--skip-ingestion" ]]; then
    # Remove the first two files if --skip-ingestion
    python_files=("${python_files[@]:2}")
fi

if [[ "$1" == "--analysis-only" ]]; then
    # Remove the first ten files if --analysis-only
    python_files=("${python_files[@]:10}")
fi




# Open a new terminal instance with top
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS Terminal
    osascript -e 'tell application "Terminal" to do script "top"'
else
    # Linux Terminals
    if command -v gnome-terminal &> /dev/null; then
        gnome-terminal -- bash -c "top; exec bash" &
    elif command -v konsole &> /dev/null; then
        konsole -e bash -c "top; exec bash" &
    elif command -v xfce4-terminal &> /dev/null; then
        xfce4-terminal -e bash -c "top; exec bash" &
    elif command -v xterm &> /dev/null; then
        xterm -e "top; bash" &
    else
        echo "No suitable terminal found to run top."
        exit 1
    fi
fi



for file in "${python_files[@]}"; do
    echo -e "\nRunning $file..."
    python "$file"
done

deactivate
