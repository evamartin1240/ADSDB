#!/usr/bin/env python3

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

def generate_embeddings_and_predict(genres, model = 'all-MiniLM-L6-v2', n_clusters = 6):
    model = SentenceTransformer(model)

    embeddings = model.encode(genres)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42)

    # Fit embeddings to K-Means
    labels = kmeans.fit_predict(embeddings)

    # Print cluster labels
    for genre, label in zip(unique_genres, labels):
        print(f"Genre: {genre}, Cluster: {label}")

    return labels, embeddings


def transform_ids(L):
    """
    Transform a list with integers and sublists into a list with integers
    and unique IDs for normalized sublists.
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

if __name__ == "__main__":

    conn = duckdb.connect("/home/maru/ADSDB/data/analytical_backbone/sandbox/sandbox.duckdb")

    df = conn.execute("SELECT * FROM sandbox").df()

    conn.close()

    genres = df.loc[:,"genres"].tolist()

    # Flatten the arrays and create a set of all unique strings
    unique_genres = set()
    for row in genres:
        unique_genres.update(row) # row[0] contains the array from the column

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

    # Map the list
    transformed_new_genres = transform_ids(new_genres)

    #plot_clusters(unique_genres, embeddings, labels, n_components=2)



    df["genres"] = transformed_new_genres

    ### ---- ALL UP UNTIL THIS POINT BELONGS IN analytical_backbone/feature_engineering
    ###
    ### Then, we must perform labelling -- in our case I think we can assign manual labels to each of the clusters (currently just numbers)
    ###
    ### Finally data preparation (outliers, missing values, etc)
    ###
    ### Now I will skip directly to model generation
    ###


    # Assuming 'df' is your pandas dataframe

    # Prepare the features and target
    X = df.drop(columns=['followers', 'artist'])  # Features (popularity, genres, avg_min_price, avg_max_price)
    y = df['followers']  # Target (followers)

    # Fill missing values for avg_min_price and avg_max_price with their mean (you can adjust this strategy)
    X['avg_min_price'].fillna(X['avg_min_price'].mean(), inplace=True)
    X['avg_max_price'].fillna(X['avg_max_price'].mean(), inplace=True)

    # Split the data into training and testing sets (75%/25% split)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

    # Initialize the RandomForestRegressor
    from sklearn.ensemble import RandomForestRegressor
    rf = RandomForestRegressor(n_estimators=100, random_state=42)

    # Train the model
    log_y_train = np.log1p(y_train)  # log1p is log(x + 1), handles 0s gracefully
    rf.fit(X_train, y_train)

    # Predict on the test set
    y_pred = rf.predict(X_test)

    # Create the scatterplot of real vs predicted values
    plt.figure(figsize=(8, 6))

    # Apply log scaling (make sure to add a small value to avoid log(0))
    log_y_test = np.log1p(y_test)  # log1p is log(x + 1), handles 0s gracefully
    log_y_pred = np.log1p(y_pred)

    # Scatter plot with log scaled values
    plt.scatter(log_y_test, log_y_pred, color='blue', alpha=0.6)

    # Add a line for perfect predictions (y = x)
    plt.plot([log_y_test.min(), log_y_test.max()], [log_y_test.min(), log_y_test.max()], color='red', linestyle='--', lw=2)

    # Label the axes
    plt.xlabel('Real Followers')
    plt.ylabel('Predicted Followers')
    plt.title('Real vs Predicted Followers')

    # Show the plot
    plt.show()

    # Calculate RMSEP (Root Mean Squared Error of Prediction)
    rmse = np.sqrt(mean_squared_error(log_y_test, log_y_pred))

    print(f'RMSEP: {rmse}')
