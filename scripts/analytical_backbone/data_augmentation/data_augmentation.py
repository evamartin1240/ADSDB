#!/usr/bin/env python3
#
import duckdb
from imblearn.over_sampling import SMOTE
import pandas as pd
import os
import matplotlib.pyplot as plt

def plot_genre_pie_chart(df):
    if 'genres' not in df.columns:
        raise ValueError("The input df does not contain a 'genres' column.")

    genre_counts = df['genres'].value_counts()

    plt.figure(figsize=(8, 8))
    genre_counts.plot(kind='pie', autopct='%1.1f%%', startangle=90, cmap='Set3')
    plt.title('Distribution of Genres')
    plt.ylabel('')  # Hide the y-label
    plt.show()


def data_augmentation(db_file, augmentation_dir):
    """
    Performs SMOTE on the data.
    """
    # List to store the output messages in order to print them later
    output = []

    # Connect to the DuckDB database
    conn = duckdb.connect(database=db_file, read_only=True)

    # Load the data
    df = conn.execute("SELECT * FROM feature_generation").df()

    plot_genre_pie_chart(df)

    conn.close()

    print(df['genres'].value_counts())

    # Ensure numeric columns for SMOTE
    numeric_cols = ['popularity', 'followers', 'avg_min_price', 'avg_max_price']
    non_numeric_cols = ['artist', 'genres']

    # Prepare features (X) and target (y) for SMOTE
    X = df[numeric_cols]
    y = df['genres']

    sampling_strategy = {
            0: 100,  # For genre 0, keep 100 samples after augmentation
            1: 211,  # For genre 1, keep it as is
            2: 75,   # For genre 2, keep 75 samples after augmentation
            3: 190,  # For genre 3, keep 190 samples after augmentation
            4: 90,   # For genre 4, keep 90 samples after augmentation
            5: 50    # For genre 5, keep 50 samples after augmentation
        }

    # Perform SMOTE
    smote = SMOTE(random_state=123, sampling_strategy = sampling_strategy)
    X_resampled, y_resampled = smote.fit_resample(X, y)

    # Create a DataFrame from the resampled data
    df_resampled = pd.DataFrame(X_resampled, columns=numeric_cols)
    df_resampled['genres'] = y_resampled

    plot_genre_pie_chart(df_resampled)

    # Generate unique identifiers for augmented 'artist' values
    original_artist_count = len(df)
    augmented_count = len(X_resampled) - original_artist_count
    augmented_artist_ids = [f"AUGMENTED_{i}" for i in range(augmented_count)]
    df_resampled['artist'] = df['artist'].tolist() + augmented_artist_ids

    # Combine the original and augmented data
    df_augmented = pd.concat([df, df_resampled.iloc[len(df):]], ignore_index=True)

    print(df_augmented['genres'].value_counts())

    # Append the count of augmented samples to the output
    output.append(f"Number of samples augmented: {augmented_count}")

    # Save the augmented data to DuckDB
    augmentation_duckdb_path = os.path.join(augmentation_dir, 'augmentation.duckdb')

    con = duckdb.connect(database=augmentation_duckdb_path)

    con.execute("DROP TABLE IF EXISTS feature_generation")
    con.execute("CREATE TABLE feature_generation AS SELECT * FROM df_augmented")

    con.close()

    print(f"DuckDB augmented database successfully saved in: {augmentation_duckdb_path}")

    return output


if __name__ == "__main__":

    duckdb_file_path = "/home/maru/ADSDB/data/analytical_backbone/feature_engineering/feature_generation.duckdb"
    augmentation_dir = "/home/maru/ADSDB/data/analytical_backbone/data_augmentation/"

#    duckdb_file_path = input("Path to DuckDB feature generation database (input): ")
#    augmentation_dir = input("Output directory (Data Augmentation): ")

    out = data_augmentation(duckdb_file_path, augmentation_dir)
    for message in out:
        print(message)
