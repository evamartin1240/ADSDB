#!/usr/bin/env python3

import yaml
import numpy as np
import pickle
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error, max_error
from scipy.stats import pearsonr
import matplotlib.pyplot as plt

def plot_y_test_y_pred(y_test, y_pred):

    plt.figure(figsize=(8, 6))
    plt.scatter(y_test, y_pred, color='blue', alpha=0.6)

    # Line for perfect predictions
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], color='red', linestyle='--', lw=2)

    plt.xlabel('Real Followers')
    plt.ylabel('Predicted Followers')
    plt.title('Real vs Predicted Followers')

    return plt.gcf()



def calculate_extval_metrics(y_true, y_pred):
    metrics = {
        "RMSE": np.sqrt(mean_squared_error(y_true, y_pred)),
        "Correlation": pearsonr(y_true, y_pred)[0],
        "R²": r2_score(y_true, y_pred),
        "MAE": mean_absolute_error(y_true, y_pred),
        "MaxError": max_error(y_true, y_pred),
    }
    return metrics


def external_validation(db_file, model):
    """
    Generalized function for performing external validation with the provided model.
    """

    conn = duckdb.connect(database=db_file)

    extval_df = conn.execute("SELECT * FROM extval").df()

    # features and target for external validation
    X_extval = extval_df.drop(columns=['followers', 'artist'])  # Features
    y_extval = np.log1p(extval_df['followers'])  # Target

    # Perform external validation with the model provided
    y_extval_pred = best_model.predict(X_extval)  # Predict on the external validation set

    metrics = calculate_extval_metrics(y_extval, y_extval_pred) # Get the metrics of the prediction

    # Create a scatterplot
    figures.append(plot_y_test_y_pred(y_extval, y_extval_pred))

    return metrics, figures

def external_validation_wrapper(db_file, metrics_dir, model_dir, figure_dir):
    """
    Wrapper to execute external_validation() on multiple models
    """

    for model_name in ["LinearRegression", "GradientBoostingRegressor", "RandomForestRegressor"]:

        messages = []

        messages.append(f"Performing external validation with {model_name}...")

        # Load the model
        model_fullpath = os.path.join(model_dir, f'{model_name}_model.pk1')
        with open(model_dir, "rb") as file:
            model = pickle.load(file)

        [metrics, figures] = external_validation(db_file, model)
