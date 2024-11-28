#!/usr/bin/env python3

def labelling():
    pass




if __name__ == "__main__":
    duckdb_file_path = input("Path to DuckDB sandbox (input): ")

    out = labelling(duckdb_file_path)
    for message in out:
        print(message)
