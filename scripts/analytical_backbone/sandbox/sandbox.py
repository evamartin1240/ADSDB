#!/usr/bin/env python3

import duckdb
import os

def exploitation2sandbox(duckdb_file_path, sandbox_dir):
    """
    Function to select a subset from the exploitation zone to analyze further
    down the analytical backbone
    """
    # Connect to the DuckDB database
    conn = duckdb.connect(duckdb_file_path)

    sandbox_df = conn.execute("SELECT a.artist, st.popularity, st.followers, a.genres, p.avg_min_price, p.avg_max_price FROM artists_stats st, artists a, avg_price p WHERE st.artist = a.artist AND a.artist = p.artist").df()

    conn.close()

    # Create the sandbox directory if it doesn't exist
    if not os.path.exists(sandbox_dir):
        os.makedirs(sandbox_dir)

    # Path for the new sandbox database
    sandbox_duckdb_path = os.path.join(sandbox_dir, 'sandbox.duckdb')

    # Connect to the new sandbox database
    con_sandbox = duckdb.connect(database=sandbox_duckdb_path)

    con_sandbox.execute("CREATE TABLE sandbox AS SELECT * FROM sandbox_df")

    con_sandbox.close()

    print(f"DuckDB sandbox database successfully saved in: {sandbox_duckdb_path}")





if __name__ == "__main__":
    #duckdb_file_path = input("Input DuckDB database (exploitation): ")
    duckdb_file_path = "/home/maru/ADSDB/data/exploitation/exploitation.duckdb"
    sandbox_dir = "/home/maru/ADSDB/data/sandbox"
    exploitation2sandbox(duckdb_file_path, sandbox_dir)
