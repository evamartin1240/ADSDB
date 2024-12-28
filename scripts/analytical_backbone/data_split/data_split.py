#!/usr/bin/env python3

import os
import duckdb
from sklearn.model_selection import train_test_split
import pandas as pd

def data_split(db_file, split_dir, keyword):
    """
    Splits the data on internal and external validation sets
    """

    # List to store the output messages in order to print them later
    output = []

    # Connect to the DuckDB database
    conn = duckdb.connect(database=db_file, read_only=True)

    df = conn.execute("SELECT * FROM feature_generation").df()

    conn.close()

    print(df["genres"].value_counts())

    # 80/20 Split
    train_df, extval_df = train_test_split(df, test_size=0.2, random_state=123)

    output.append(f"Dataset split performed.")

    # Create the data preparation directory if it doesn't exist
    if not os.path.exists(split_dir):
        os.makedirs(split_dir)

    filename = "_".join([keyword, "split.duckdb"])

    split_duckdb_path = os.path.join(split_dir, filename)

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

    duckdb_file_path = "/home/maru/ADSDB/data/analytical_backbone/data_augmentation/augmentation.duckdb"
    split_dir = "/home/maru/ADSDB/data/analytical_backbone/data_split/"
    keyword = "augmented"

#    duckdb_file_path = input("Path to DuckDB feature generation database (input): ")
#    split_dir = input("Output directory (data split): ")
#    keyword = input("Give a keyword to prepend to the output: ")

    out = data_split(duckdb_file_path, split_dir, keyword)
    for message in out:
        print(message)
