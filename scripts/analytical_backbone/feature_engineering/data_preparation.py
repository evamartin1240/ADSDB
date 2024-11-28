#!/usr/bin/env python3
#

import duckdb

def data_preparation(db_file):
    """
    Prepares the data for modelling with dataset-specific corrections
    """

    # List to store the output messages in order to print them later
    output = []

    # Connect to the DuckDB database
    conn = duckdb.connect(database=db_file, read_only=False)

    df = conn.execute("SELECT * FROM sandbox").df()

    df['avg_min_price'].fillna(df['avg_min_price'].mean(), inplace=True)
    df['avg_max_price'].fillna(df['avg_max_price'].mean(), inplace=True)

    output.append(f"Price data imputed.")

    conn.execute(f"DROP TABLE IF EXISTS sandbox")
    conn.execute(f"CREATE TABLE sandbox AS SELECT * FROM df")

    # Close the connection
    conn.close()

    return output


if __name__ == "__main__":

    duckdb_file_path = input("Path to DuckDB sandbox (input): ")

    out = data_preparation(duckdb_file_path)
    for message in out:
        print(message)
