#!/usr/bin/env python3

import os
import duckdb
from sklearn.model_selection import train_test_split
import pandas as pd

def data_preparation(db_file, split_dir):
    """
    Splits the data on internal and external validation sets
    """

    # List to store the output messages in order to print them later
    output = []

    # Connect to the DuckDB database
    conn = duckdb.connect(database=db_file, read_only=True)

    df = conn.execute("SELECT * FROM feature_generation").df()

    conn.close()

    # 80/20 Split
    train_df, extval_df = train_test_split(df, test_size=0.2, random_state=123)

    output.append(f"Dataset split performed.")

    # Create the data preparation directory if it doesn't exist
    if not os.path.exists(split_dir):
        os.makedirs(split_dir)

    split_duckdb_path = os.path.join(split_dir, 'split.duckdb')

    # Connect to the new sandbox database
    con = duckdb.connect(database=split_duckdb_path)

    con.execute("DROP TABLE IF EXISTS train")
    con.execute("DROP TABLE IF EXISTS extval")

    con.execute("CREATE TABLE train AS SELECT * FROM train_df")
    con.execute("CREATE TABLE extval AS SELECT * FROM extval_df")

    con.close()

    print(f"DuckDB split database successfully saved in: {split_duckdb_path}")

    return output


if __name__ == "__main__":

    duckdb_file_path = input("Path to DuckDB feature generation database (input): ")
    split_dir = input("Output directory (data split): ")

    out = data_preparation(duckdb_file_path, split_dir)
    for message in out:
        print(message)
