import pandas as pd
import json
import os
import duckdb

"""
Persistent landing zone to formatted zone
Take all the files in the system (persistent landing zone) and unify the formats from JSON to DuckDB database.
"""

def convert_json_to_duckdb(json_file_path, con):
    """ Function to convert .json to DuckDB.
    """
    # Load the JSON data
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)

    # Convert the JSON data to a pandas DataFrame
    df = pd.json_normalize(data)

    # Print the shape of the DataFrame
    print(f"Loaded DataFrame shape from {json_file_path}: {df.shape}")

    # Register the DataFrame in DuckDB
    con.register("temp_df", df)

    # Save the DataFrame into a DuckDB table (name the table after the JSON file, without extension)
    table_name = os.path.basename(json_file_path).replace('.json', '')
    con.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM temp_df")


    # Print confirmation of table creation
    print(f'Table {table_name} created in DuckDB database with shape: {df.shape}')

def landing2formatted(persdir_in, formdir_out):
    """ Function to iterate over .json files in the persistent directory,
        convert them to DuckDB, and save them in the formatted directory.
    """

    if not os.path.exists(formdir_out):  # If the formatted directory doesn't exist, create it
        os.makedirs(formdir_out)

    # Define the DuckDB file path
    duckdb_file_path = os.path.join(formdir_out, 'formatted.duckdb')

    # Connect to DuckDB (create or open the .duckdb file)
    con = duckdb.connect(database=duckdb_file_path)

    # Iterate over all the files in the persistent directory to change the format from JSON to DuckDB
    for root, dirs, files in os.walk(persdir_in):
        for file in files:
            if file.endswith('.json'):  # Only process .json files
                json_file_path = os.path.join(root, file)
                convert_json_to_duckdb(json_file_path, con)

    # Close the DuckDB connection
    con.close()

    print(f'DuckDB database created: {duckdb_file_path}')


if __name__ == "__main__":
    persdir_in = input("Persistent landing directory path (input): ")
    formdir_out = input("Formatted landing directory path (output): ")
    landing2formatted(persdir_in, formdir_out)