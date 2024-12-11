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

    df_train = conn.execute("SELECT * FROM train").df()
    df_extval = conn.execute("SELECT * FROM extval").df()

    # Prepare the features and target
    X_train = df_train.drop(columns=['followers', 'artist'])  # Features (popularity, genres, avg_min_price, avg_max_price)
    y_train = df_train['followers']  # Target (followers)

    X_test = df_extval.drop(columns=['followers', 'artist'])  # Features (popularity, genres, avg_min_price, avg_max_price)
    y_test = df_extval['followers']  # Target (followers)


    # Split the data into training and testing sets (75%/25% split)
    #X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

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

def model_generation(db_file, model_dir, n_splits=5, n_iter=50):
    # List to store the output messages in order to print them later
    output = []

    # Connect to the DuckDB database
    conn = duckdb.connect(database=db_file)

    # Load data from "train" and "extval" tables
    train_df = conn.execute("SELECT * FROM train").df()
    extval_df = conn.execute("SELECT * FROM extval").df()

    # Prepare the features and target for training
    X_train = train_df.drop(columns=['followers', 'artist'])  # Features
    y_train = np.log1p(train_df['followers'])  # Target

    # Prepare the features and target for external validation
    X_extval = extval_df.drop(columns=['followers', 'artist'])  # Features
    y_extval = np.log1p(extval_df['followers'])  # Target

    # Define the parameter grid for optimization
    param_grid = {
        'n_estimators': [50, 100, 200, 500, 1000],
        'max_depth': [None, 10, 20, 30, 40, 50],
        'min_samples_split': [2, 5, 10, 20],
        'min_samples_leaf': [1, 2, 4, 8],
        'max_features': [None, 'sqrt', 'log2'],
        'bootstrap': [True, False],
    }

    # Initialize RandomForestRegressor
    from sklearn.ensemble import RandomForestRegressor
    rf = RandomForestRegressor(random_state=42)

    # Initialize RandomizedSearchCV with parallelization and cross-validation
    from sklearn.model_selection import RandomizedSearchCV
    random_search = RandomizedSearchCV(
        estimator=rf,
        param_distributions=param_grid,
        n_iter=n_iter,  # Number of random combinations to try
        cv=n_splits,
        scoring='neg_root_mean_squared_error',  # RMSE (negative because higher is better for scorers)
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

    # Perform external validation with the optimized model
    y_extval_pred = best_model.predict(X_extval)  # Reverse log transformation
    extval_rmse = np.sqrt(mean_squared_error(y_extval, y_extval_pred))
    output.append(f"RMSE for external validation: {extval_rmse}")

    # Create a scatterplot
    plot_y_test_y_pred(y_extval, y_extval_pred)

    # Save the optimized model to a file
    model_fullpath = os.path.join(model_dir, 'optimized_random_forest_model.pk1')
    with open(model_fullpath, 'wb') as file:
        pickle.dump(best_model, file)

    output.append(f"Optimized Random Forest model successfully written to {model_fullpath}")

    return output



def model_generation(db_file, model_dir, regressor, param_grid, n_splits=5, n_iter=50):
    """
    Generalized function to perform model training, hyperparameter tuning, and external validation.

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
    extval_df = conn.execute("SELECT * FROM extval").df()

    # features and target for training
    X_train = train_df.drop(columns=['followers', 'artist'])  # Features
    y_train = np.log1p(train_df['followers'])  # Target

    # features and target for external validation
    X_extval = extval_df.drop(columns=['followers', 'artist'])  # Features
    y_extval = np.log1p(extval_df['followers'])  # Target

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

    # Perform external validation with the optimized model
    y_extval_pred = best_model.predict(X_extval)  # Predict on the external validation set
    extval_rmse = np.sqrt(mean_squared_error(y_extval, y_extval_pred))
    output.append(f"RMSE for external validation: {extval_rmse}")

    # Create a scatterplot
    plot_y_test_y_pred(y_extval, y_extval_pred)

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

def model_generation_wrapper(db_file, model_dir, params_path, n_splits=5, n_iter=50):
    """
    Wrapper function to execute different regression models using RandomizedSearchCV
    and external validation.
 bn
    Parameters:
    - db_file: Path to the DuckDB database file
    - model_dir: Directory to save the optimized model
    - model_name: Name of the regression model (e.g., "RandomForestRegressor")
    - n_splits: Number of splits for cross-validation
    - n_iter: Number of random combinations for RandomizedSearchCV
    - param_file: YAML file containing parameter grids
    """
    for model_name in ["LinearRegression", "GradientBoostingRegressor", "RandomForestRegressor"]:

        messages = []

        messages.append(f"Fitting a {model_name}...")

        # Load the parameter grid for the chosen model
        param_grid = load_param_grid(model_name, params_path)

        # Get the model instance
        model = get_model_instance(model_name)

        # Call the original model generation function
        #return model_generation(db_file, model_dir, n_splits, n_iter, model, param_grid)
        [out_messages, modelobj] = model_generation(db_file, model_dir, model, param_grid)

        messages.extend(out_messages)

        # Save the optimized model to a file
        model_fullpath = os.path.join(model_dir, f'{model_name}_model.pk1')
        with open(model_fullpath, 'wb') as file:
            pickle.dump(modelobj, file)

        messages.append(f"Optimized model successfully written to {model_fullpath}")

        for message in messages:
            print(message)


if __name__ == "__main__":
    duckdb_file_path = input("Path to DuckDB split database (input): ")
    params_path = input("Path to params.yaml (model parameters): ")
    model_dir = input("Path to model directory (output): ")

    out = model_generation_wrapper(
        db_file=duckdb_file_path,
        model_dir=model_dir,
        params_path=params_path
        )

