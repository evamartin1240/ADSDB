#!/usr/bin/env python3
#
#
import os
import duckdb

def data_preparation(db_file, engineering_dir):
    """
    Prepares the data for modelling with dataset-specific corrections
    """

    # List to store the output messages in order to print them later
    output = []

    # Connect to the DuckDB database
    conn = duckdb.connect(database=db_file, read_only=True)

    df = conn.execute("SELECT * FROM sandbox").df()

    conn.close()

    df['avg_min_price'].fillna(df['avg_min_price'].mean(), inplace=True)
    df['avg_max_price'].fillna(df['avg_max_price'].mean(), inplace=True)

    output.append(f"Price data imputed.")

    # Create the data preparation directory if it doesn't exist
    if not os.path.exists(engineering_dir):
        os.makedirs(engineering_dir)

    # Path for the new sandbox database
    preparation_duckdb_path = os.path.join(engineering_dir, 'data_preparation.duckdb')

    # Connect to the new sandbox database
    con_preparation = duckdb.connect(database=preparation_duckdb_path)

    con_preparation.execute("CREATE TABLE data_preparation AS SELECT * FROM df")

    con_preparation.close()

    print(f"DuckDB data preparation database successfully saved in: {preparation_duckdb_path}")

    return output


if __name__ == "__main__":

    duckdb_file_path = input("Path to DuckDB sandbox (input): ")
    engineering_dir = input("Output directory (feature engineering): ")

    out = data_preparation(duckdb_file_path, engineering_dir)
    for message in out:
        print(message)
