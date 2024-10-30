#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Activate the Python virtual environment
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
)

# Check for --skip-ingestion flag
if [[ "$1" == "--skip-ingestion" ]]; then
    # Remove the first two files if the flag is present
    python_files=("${python_files[@]:2}")
fi

# Function to display CPU and memory usage
function show_system_usage {
    echo -e "\n--- System Usage ---"
    echo "CPU Usage:"
    top -bn1 | grep "Cpu(s)" | \
       sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | \
       awk '{print 100 - $1"% CPU used"}'
    echo "Memory Usage:"
    free -h | awk '/^Mem:/ {print $3 " used out of " $2}'
}

# Run each Python script and display system usage after each one
for file in "${python_files[@]}"; do
    echo -e "\nRunning $file..."
    python "$file"
    show_system_usage
    sleep 2  # Optional delay between scripts
done

# Deactivate the virtual environment
deactivate
