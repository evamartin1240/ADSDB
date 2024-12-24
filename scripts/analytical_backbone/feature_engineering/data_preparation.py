#!/usr/bin/env python3
#
#
import os
import duckdb
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def outlier_handling(df):
    pass

def visualize_outliers(df, columns = ['avg_min_price', 'avg_max_price']):
    """
    Plots boxplots for the columns specified to detect outliers
    """
    columns_to_visualize = columns

    # Check for missing columns
    valid_columns = [col for col in columns_to_visualize if col in df.columns]
    missing_columns = set(columns_to_visualize) - set(valid_columns)
    if missing_columns:
        print(f"Warning: The following columns are missing and will be skipped: {missing_columns}")

    # Create a boxplot for valid columns
    if valid_columns:
        plt.figure(figsize=(12, 6))
        sns.boxplot(data=df[valid_columns], orient='h')
        plt.title('Boxplot of Selected Columns')
        plt.xlabel('Values')
        plt.ylabel('Columns')

        plt.grid(axis='x')

        x_min, x_max = 0, plt.xlim()[1]
        plt.xlim(x_min, x_max)

        plt.xticks(ticks=np.arange(x_min, x_max, step=(x_max - x_min) / 10))  # 10 ticks across the range

        plt.show()
    else:
        print("No valid columns found for visualization.")


def outliers_iqr(df, columns = ['avg_min_price', 'avg_max_price']):
    """
    Detects the severe outliers (3 times the IQR) for the input columns.
    """

    # Ensure the specified columns column exist in the df
    for col in columns:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found in dataframe.")

    df_cleaned = df.copy()

    # Track outliers
    outlier_artists = set()

    for col in columns:
        Q1 = df_cleaned[col].quantile(0.25)
        Q3 = df_cleaned[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 3 * IQR
        upper_bound = Q3 + 3 * IQR

        # Find rows that are outliers
        outliers = df_cleaned[(df_cleaned[col] < lower_bound) | (df_cleaned[col] > upper_bound)]

        # Add the artists of the outliers to the removed_artists set
        outlier_artists.update(outliers["artist"].unique())
        
    # Print how many artists were removed and their names
    if outlier_artists:
        print(f"{len(outlier_artists)} artists were detected as outliers.")
        print(f"Outlier Artists: {', '.join(outlier_artists)}")
    else:
        print("No artists were detected as outliers.")

    return df_cleaned


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

    # Impute price with its mean
    df['avg_min_price'].fillna(df['avg_min_price'].mean(), inplace=True)
    df['avg_max_price'].fillna(df['avg_max_price'].mean(), inplace=True)

    output.append(f"Price data imputed.")

    df_tmp = outliers_iqr(df)

    df = df[df['genres'].apply(lambda x: len(x) > 0)] # remove the artists that do not have any genre

    output.append(f"Removed artists with no genre.")

    visualize_outliers(df)

    visualize_outliers(df, columns=["followers"])

    # Create the data preparation directory if it doesn't exist
    if not os.path.exists(engineering_dir):
        os.makedirs(engineering_dir)

    # Path for the new sandbox database
    preparation_duckdb_path = os.path.join(engineering_dir, 'data_preparation.duckdb')

    # Connect to the new sandbox database
    con_preparation = duckdb.connect(database=preparation_duckdb_path)

    con_preparation.execute("DROP TABLE IF EXISTS data_preparation")
    con_preparation.execute("CREATE TABLE data_preparation AS SELECT * FROM df")

    con_preparation.close()

    print(f"DuckDB data preparation database successfully saved in: {preparation_duckdb_path}")

    return output


if __name__ == "__main__":

    #duckdb_file_path = input("Path to DuckDB sandbox (input): ")
    #engineering_dir = input("Output directory (feature engineering): ")

    duckdb_file_path = "/home/maru/upc-mds/ADSDB/data/analytical_backbone/sandbox/sandbox.duckdb"
    engineering_dir = "/home/maru/upc-mds/ADSDB/data/analytical_backbone/feature_engineering/"

    out = data_preparation(duckdb_file_path, engineering_dir)
    for message in out:
        print(message)
