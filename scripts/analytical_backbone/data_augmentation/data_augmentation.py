#!/usr/bin/env python3
#
import duckdb
from imblearn.over_sampling import SMOTE
import pandas as pd
import os
import matplotlib.pyplot as plt
import streamlit as st
import numpy as np

def plot_genre_pie_chart(df):
    if 'genres' not in df.columns:
        raise ValueError("The input df does not contain a 'genres' column.")

    genre_counts = df['genres'].value_counts()

    fig = plt.figure(figsize=(8, 8))
    genre_counts.plot(kind='pie', autopct='%1.1f%%', startangle=90, cmap='Set3')
    plt.title('Distribution of Genres')
    plt.ylabel('')  # Hide the y-label

    return fig

def create_sampling_strategy(df, ratio = 0.25):

    genre_counts = df['genres'].value_counts()

    genre_counts_df = genre_counts.reset_index()
    genre_counts_df.columns = ['cluster', 'count']

    maxnum = genre_counts_df['count'].max()

    genre_counts_df['adjusted_count'] = genre_counts_df['count'] + (maxnum - genre_counts_df['count']) * ratio


    adjusted_dict = {
        row['cluster'] : int(np.floor(row['adjusted_count']))
        for _, row in genre_counts_df.iterrows()
    }

    return adjusted_dict


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

    sampling_strategy = create_sampling_strategy(df)

    fig = plot_genre_pie_chart(df)

    fig.suptitle("Before SMOTE")

    plt.show()
    st.pyplot(fig)

    conn.close()

    print(df['genres'].value_counts())

    # Ensure numeric columns for SMOTE
    numeric_cols = ['popularity', 'followers', 'avg_min_price', 'avg_max_price']
    non_numeric_cols = ['artist', 'genres']

    # Prepare features (X) and target (y) for SMOTE
    X = df[numeric_cols]
    y = df['genres']

    # Perform SMOTE
    smote = SMOTE(random_state=123, sampling_strategy = sampling_strategy)
    X_resampled, y_resampled = smote.fit_resample(X, y)

    # Create a DataFrame from the resampled data
    df_resampled = pd.DataFrame(X_resampled, columns=numeric_cols)
    df_resampled['genres'] = y_resampled

    fig = plot_genre_pie_chart(df_resampled)

    fig.suptitle("After SMOTE")

    plt.show()
    st.pyplot(fig)

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

    duckdb_file_path = input("Path to DuckDB feature generation database (input): ")
    augmentation_dir = input("Output directory (Data Augmentation): ")

    out = data_augmentation(duckdb_file_path, augmentation_dir)
    for message in out:
        print(message)
