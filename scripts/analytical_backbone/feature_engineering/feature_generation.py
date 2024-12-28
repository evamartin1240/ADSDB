#!/usr/bin/env python3

import os
import duckdb
import pandas
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from mpl_toolkits.mplot3d import Axes3D
from sklearn.model_selection import train_test_split
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from collections import Counter
import streamlit as st


def plot_clusters(genres, embeddings, cluster_labels, n_components=2):
    """
    Visualizes word embeddings with cluster labels in 2D or 3D.
    """

    if n_components not in [2, 3]:
        raise ValueError("n_components must be 2 or 3 for visualization.")

    # Dimensionality reduction
    reducer = PCA(n_components=n_components)
    reduced_embeddings = reducer.fit_transform(embeddings)

    # Plotting
    fig = plt.figure(figsize=(12, 8))

    if n_components == 2:
        plt.scatter(reduced_embeddings[:, 0], reduced_embeddings[:, 1],
                    c=cluster_labels, cmap='tab10', alpha=0.7)

        for i, genre in enumerate(genres):
            plt.text(reduced_embeddings[i, 0], reduced_embeddings[i, 1], genre, fontsize=8, alpha=0.6)

        plt.title("Clusters of word embeddings")
        plt.xlabel("Dimension 1")
        plt.ylabel("Dimension 2")
        plt.grid(True)

    elif n_components == 3:
        ax = fig.add_subplot(111, projection='3d')
        scatter = ax.scatter(reduced_embeddings[:, 0], reduced_embeddings[:, 1], reduced_embeddings[:, 2],
                             c=cluster_labels, cmap='tab10', alpha=0.7)

        for i, genre in enumerate(genres):
            ax.text(reduced_embeddings[i, 0], reduced_embeddings[i, 1], reduced_embeddings[i, 2],
                    genre, fontsize=8, alpha=0.6)

        ax.set_title("Clusters of word embeddings")
        ax.set_xlabel("Dimension 1")
        ax.set_ylabel("Dimension 2")
        ax.set_zlabel("Dimension 3")

    plt.show()
    st.pyplot(fig)

def generate_embeddings_and_predict(genres, model = 'all-MiniLM-L6-v2', n_clusters = 6):
    """
    Generate word embeddings for a list of genres using the model provided
    and cluster them with K-means
    """
    model = SentenceTransformer(model)

    embeddings = model.encode(genres)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42)

    # Fit embeddings to K-Means
    labels = kmeans.fit_predict(embeddings)

    # Print cluster labels
    for genre, label in zip(genres, labels):
        print(f"Genre: {genre}, Cluster: {label}")

    return labels, embeddings


def transform_ids(L):
    """
    Transform a list with integers and sublists into a list with unique IDs
    """

    sublist_to_id = {}  # Dictionary to map sublists to unique IDs
    id_counter = 1      # Counter for unique IDs

    def get_or_create_id(sublist):
        """Assign or retrieve the unique ID for a normalized sublist."""
        normalized = tuple(sorted(sublist))  # Normalize the sublist (sort and make tuple)
        if normalized not in sublist_to_id:
            nonlocal id_counter
            sublist_to_id[normalized] = id_counter
            id_counter += 1
        return sublist_to_id[normalized]

    # Transform the input list
    transformed = [
        get_or_create_id(item) if isinstance(item, list) else item
        for item in L
    ]

    return transformed

def transform_ids(data):
    """
    If an artist contains more than 1 genre cluster, assign to it the most common genre.
    """
    result = []
    for item in data:
        if isinstance(item, list):
            if item:  # If the list is not empty...
                most_common = Counter(item).most_common(1)[0][0] # Take the most common genre cluster (mode)
                result.append(most_common)
            else:  # If the list is empty
                result.append(None)
        else:
            result.append(item)
    return result

def cluster_genres(genres):

    # Flatten the arrays and create a set of all unique strings
    unique_genres = set()
    for row in genres:
        unique_genres.update(row)

    unique_genres = list(unique_genres)

    labels, embeddings = generate_embeddings_and_predict(unique_genres)

    genres_dict = {unique_genres[i]: labels[i] for i in range(len(unique_genres))}

    new_genres = []
    for genre_L in genres:
        new_genre_L = set()
        for genre in genre_L:
            new_genre_L.add(genres_dict[genre])
        new_genre_L = list(new_genre_L)
        new_genres.append(new_genre_L)

    # Amend the artists that have multiple genre clusters
    transformed_new_genres = transform_ids(new_genres)

    plot_clusters(unique_genres, embeddings, labels, n_components=2)

    return transformed_new_genres




def feature_generation(db_file, engineering_dir):
    """

    """
    # List to store the output messages in order to print them later
    output = []

    # Connect to the DuckDB database
    conn = duckdb.connect(database=db_file, read_only=False)

    df = conn.execute("SELECT * FROM data_preparation").df()

    conn.close()

    genres = df.loc[:,"genres"].tolist()

    clustered_genres = cluster_genres(genres)

    df["genres"] = clustered_genres

    output.append(f"There are {len(set(clustered_genres))} genres in the sandbox after clustering.")

    # Path for the new sandbox database
    generation_duckdb_path = os.path.join(engineering_dir, 'feature_generation.duckdb')

    # Connect to the new sandbox database
    con_generation= duckdb.connect(database=generation_duckdb_path)

    con_generation.execute("DROP TABLE IF EXISTS feature_generation")
    con_generation.execute("CREATE TABLE feature_generation AS SELECT * FROM df")

    con_generation.close()

    print(f"DuckDB feature generation database successfully saved in: {generation_duckdb_path}")

    return output



if __name__ == "__main__":
    duckdb_file_path = input("Path to DuckDB data preparation database (input): ")
    engineering_dir = input("Output directory (feature engineering): ")
    #duckdb_file_path = "/home/maru/upc-mds/ADSDB/data/analytical_backbone/sandbox/sandbox.duckdb"

    out = feature_generation(duckdb_file_path, engineering_dir)
    for message in out:
        print(message)
