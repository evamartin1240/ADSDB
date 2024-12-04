#!/usr/bin/env python3
#

import duckdb
import os
import pandas
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import pickle


def plot_y_test_y_pred(y_test, y_pred):

    plt.figure(figsize=(8, 6))
    plt.scatter(y_test, y_pred, color='blue', alpha=0.6)

    # Line for perfect predictions
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], color='red', linestyle='--', lw=2)

    plt.xlabel('Real Followers')
    plt.ylabel('Predicted Followers')
    plt.title('Real vs Predicted Followers')

    plt.show()




def model_generation(db_file, model_dir):
    # List to store the output messages in order to print them later
    output = []

    # Connect to the DuckDB database
    conn = duckdb.connect(database=db_file)

    df = conn.execute("SELECT * FROM feature_generation").df()

    # Prepare the features and target
    X = df.drop(columns=['followers', 'artist'])  # Features (popularity, genres, avg_min_price, avg_max_price)
    y = df['followers']  # Target (followers)

    # Split the data into training and testing sets (75%/25% split)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

    # Initialize the RandomForestRegressor
    from sklearn.ensemble import RandomForestRegressor
    rf = RandomForestRegressor(n_estimators=100, random_state=42)

    # Train the model
    log_y_train = np.log1p(y_train) # log1p to handle zeroes
    rf.fit(X_train, y_train)

    # Predict on the test set
    y_pred = rf.predict(X_test)

    # Log-scale
    log_y_test = np.log1p(y_test)
    log_y_pred = np.log1p(y_pred)

    # Make a scatterplot to show the predictions
    plot_y_test_y_pred(log_y_test, log_y_pred)

    # Calculate RMSE
    rmse = np.sqrt(mean_squared_error(log_y_test, log_y_pred))

    output.append(f"Root Mean Squared Error for the external validation is {rmse}")

    # Save the model to a file
    model_fullpath = os.path.join(model_dir, 'random_forest_model.pk1')
    with open(model_fullpath, 'wb') as file:
        pickle.dump(rf, file)

    output.append(f"Random Forest model written to successfully written to {model_fullpath}")

    return output



if __name__ == "__main__":
    duckdb_file_path = input("Path to DuckDB feature generation database (input): ")
    model_dir = input("Path to model directory (output): ")

    #duckdb_file_path = "/home/maru/upc-mds/ADSDB/data/analytical_backbone/sandbox/sandbox.duckdb"

    out = model_generation(duckdb_file_path, model_dir)
    for message in out:
        print(message)
