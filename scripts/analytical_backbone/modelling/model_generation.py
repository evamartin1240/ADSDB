#!/usr/bin/env python3
#

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.linear_model import LinearRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import mean_squared_error
import numpy as np
import pickle
import os
import duckdb
import matplotlib.pyplot as plt
import yaml

models_to_use = ["LinearRegression", "GradientBoostingRegressor", "RandomForestRegressor"]

def model_generation(db_file, model_dir, regressor, param_grid, n_splits=5, n_iter=50):
    """
    Generalized function to perform model training and hyperparameter tuning.

    - db_file: The DuckDB database file.
    - model_dir: Directory where the model will be saved.
    - regressor: The regression model (RandomForestRegressor, LinearRegression).
    - param_grid: Dictionary of hyperparameters for the chosen regressor (obtained from params.yaml).
    - n_splits: Number of folds for cross-validation (default is 5).
    - n_iter: Number of iterations for RandomizedSearchCV (default is 50).
    """

    output = []

    conn = duckdb.connect(database=db_file)

    train_df = conn.execute("SELECT * FROM train").df()

    # features and target for training
    X_train = train_df.drop(columns=['followers', 'artist'])  # Features
    y_train = np.log1p(train_df['followers'])  # Target

    # Initialize RandomizedSearchCV for cross-validation
    random_search = RandomizedSearchCV(
        estimator=regressor,
        param_distributions=param_grid,
        n_iter=n_iter,
        cv=n_splits,
        scoring='neg_root_mean_squared_error',  # Error measure (RMSE)
        n_jobs=-1,  # Use all available CPU cores for parallelization
        random_state=42,
        verbose=1
    )

    # Perform the randomized search on log-transformed target
    random_search.fit(X_train, y_train)

    # Get the best model and hyperparameters
    best_model = random_search.best_estimator_
    best_params = random_search.best_params_

    output.append(f"Best parameters from cross-validation: {best_params}")

    return output, best_model

def load_param_grid(model_name, param_file):
    """Load parameter grid for a specific model from params.yaml."""
    with open(param_file, 'r') as f:
        param_grids = yaml.safe_load(f)
    param_grid = param_grids.get(model_name, {})

    if "var_smoothing" in param_grid:
        param_grid["var_smoothing"] = [float(item) for item in param_grid["var_smoothing"]]

    return param_grid

def get_model_instance(model_name):
    """Return an instance of the corresponding model."""
    if model_name == "RandomForestRegressor":
        return RandomForestRegressor(random_state=123)
    elif model_name == "GradientBoostingRegressor":
        return GradientBoostingRegressor(random_state=123)
    elif model_name == "SVR":
        return SVR()
    elif model_name == "LinearRegression":
        return LinearRegression()
    elif model_name == "GaussianNB":
        return GaussianNB()
    else:
        raise ValueError(f"Unsupported model: {model_name}")

def model_generation_wrapper(db_file, model_dir, params_path, keyword, n_splits=5, n_iter=50):
    """
    Wrapper function to execute different regression models using RandomizedSearchCV

    Parameters:
    - db_file: Path to the DuckDB database file
    - model_dir: Directory to save the optimized model
    - model_name: Name of the regression model (e.g., "RandomForestRegressor")
    - n_splits: Number of splits for cross-validation
    - n_iter: Number of random combinations for RandomizedSearchCV
    - param_file: YAML file containing parameter grids
    """
    for model_name in models_to_use:

        messages = []

        messages.append(f"Fitting a {model_name}...")

        # Load the parameter grid for the chosen model
        param_grid = load_param_grid(model_name, params_path)

        # Get the model instance
        model = get_model_instance(model_name)

        # Call the original model generation function
        [out_messages, modelobj] = model_generation(db_file, model_dir, model, param_grid)

        messages.extend(out_messages)

        # Save the optimized model to a file
        model_fullpath = os.path.join(model_dir, f'{keyword}_{model_name}_model.pk1')
        with open(model_fullpath, 'wb') as file:
            pickle.dump(modelobj, file)

        messages.append(f"Optimized model successfully written to {model_fullpath}")

        for message in messages:
            print(message)


if __name__ == "__main__":
    duckdb_file_path = input("Path to DuckDB split database (input): ")
    params_path = input("Path to params.yaml (model parameters): ")
    model_dir = input("Path to model directory (output): ")
    keyword = input("Give a keyword to name outputs: ")

    out = model_generation_wrapper(
        db_file=duckdb_file_path,
        model_dir=model_dir,
        params_path=params_path,
        keyword=keyword
        )

