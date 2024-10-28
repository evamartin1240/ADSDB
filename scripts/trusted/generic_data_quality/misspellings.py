import pandas as pd
from collections import Counter
import duckdb
import re

"""# Misspellings correction
Find and fix misspellings or variations in the genre column to make sure same genres have a consistent label.
"""

def clean_and_split_genres(df):
    """ Correctly split `genres` column.
    """
    def split_genres(entry):
        if entry == "NA":
            return []
        return re.findall(r"'(.*?)'", entry)

    df['genres'] = df['genres'].apply(split_genres)

    return df


""" Manual corrections
"""

corrections = {
    'urban latino': 'urbano latino',
    'latin urban': 'urbano latino',
    'dance-pop': 'dance pop',
    'turkish singer-songwriter': 'singer-songwriter',
    'irish singer-songwriter': 'singer-songwriter',
    'alt hip-hop': 'alternative hip hop',
    'hiphop': 'hip hop',
    'italian trap': 'trap italiano',
    'latin reggaeton': 'reggaeton',
    'spanish rock': 'rock en espanol',
    'contemporary jazz': 'jazz',
    'k-pop boy group': 'k-pop'
}

def correct_genres(df):
    # Apply the corrections
    def apply_corrections(genres_list):
      return [corrections.get(genre, genre) for genre in genres_list]

    # Apply corrections to the 'genres' column
    df['genres'] = df['genres'].apply(apply_corrections)

    return df


def misspellings(db_file):
    conn = duckdb.connect(database=db_file, read_only=False)
    df = conn.execute(f"SELECT * FROM {'spotify'}").df()

    df = clean_and_split_genres(df)
    df = correct_genres(df)

    conn.execute(f"DROP TABLE IF EXISTS {'spotify'}")
    conn.execute(f"CREATE TABLE {'spotify'} AS SELECT * FROM df")

    conn.close()

if __name__ == "__main__":
    duckdb_file_path = input("Input DuckDB database (trusted): ")
    misspellings(duckdb_file_path)   