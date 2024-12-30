#!/usr/bin/env python3

import yaml
import numpy as np
import pickle
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error, max_error
from scipy.stats import pearsonr
import os
import duckdb
import pandas as pd
from pprint import pprint
import streamlit as st

from plots import plot_y_test_y_pred, plot_residuals, plot_model_metrics

models_to_use = ["LinearRegression", "GradientBoostingRegressor", "RandomForestRegressor"]

def convert_to_python_types(metrics):
    """
    Converts the contents of the metrics dict to Python types so they are human-readable in the yaml
    """
    return {key: float(value) if isinstance(value, (np.floating, np.integer)) else value
            for key, value in metrics.items()}

def calculate_extval_metrics(y_true, y_pred):
    metrics = {
        "RMSE": np.sqrt(mean_squared_error(y_true, y_pred)),
        "Correlation": pearsonr(y_true, y_pred)[0],
        "Rsquared": r2_score(y_true, y_pred),
        "MAE": mean_absolute_error(y_true, y_pred),
        "MaxError": max_error(y_true, y_pred),
    }
    metrics = convert_to_python_types(metrics)
    return metrics

def external_validation(db_file, model):
    """
    Generalized function for performing external validation with the provided model.
    """

    figures = []
    figure_names = []

    conn = duckdb.connect(database=db_file)

    extval_df = conn.execute("SELECT * FROM extval").df()

    # features and target for external validation
    X_extval = extval_df.drop(columns=['followers', 'artist'])  # Features
    y_extval = np.log1p(extval_df['followers'])  # Target

    # Perform external validation with the model provided
    y_extval_pred = model.predict(X_extval)  # Predict on the external validation set

    metrics = calculate_extval_metrics(y_extval, y_extval_pred) # Get the metrics of the prediction

    # Create a scatterplot
    figures.append(plot_y_test_y_pred(y_extval, y_extval_pred))
    figure_names.append("y_test_y_pred")

    # Plot the residuals
    figures.append(plot_residuals(y_extval, y_extval_pred))
    figure_names.append("residuals")

    return metrics, figures, figure_names

def external_validation_wrapper(db_file, metrics_dir, model_dir, figure_dir, keyword):
    """
    Wrapper to execute external_validation() on multiple models
    """

    messages = []

    for model_name in models_to_use:
        messages.append(f"Performing external validation with {model_name}...")

        # Load the model
        model_fullpath = os.path.join(model_dir, f'{keyword}_{model_name}_model.pk1')
        with open(model_fullpath, "rb") as file:
            model = pickle.load(file)

        [metrics, figures, figure_names] = external_validation(db_file, model)

        messages.append(f"Extval metrics for {model_name}:")
        messages.append(metrics)

        for i, fig in enumerate(figures):
            fig.suptitle(f"{model_name} ({keyword})")
            figpath = os.path.join(figure_dir, f"{keyword}_{model_name}_{figure_names[i]}")
            fig.savefig(figpath, dpi=300)
            st.pyplot(fig)

        messages.append(f"Figures saved in {figure_dir}")

        metricspath = os.path.join(metrics_dir, f"{keyword}_{model_name}.yaml")
        with open(metricspath, 'w') as file:
            yaml.dump(metrics, file, default_flow_style=False)

        messages.append(f"Metrics saved in {metrics_dir}")

    fig = plot_model_metrics(models_to_use, keyword, metrics_dir)
    figpath = os.path.join(figure_dir, f"{keyword}_performance")
    fig.savefig(figpath, dpi=300)
    st.pyplot(fig)

    messages.append(f"Performance figure saved in {figure_dir}")

    return messages



if __name__ == "__main__":
    duckdb_file_path = input("Path to DuckDB split database (input): ")
    model_dir = input("Path to model directory (input): ")
    metrics_dir = input("Path to metrics directory (output) ")
    figure_dir = input("Path to figure directory (output) ")
    keyword = input("Give a keyword to identify inputs and outputs (should be the same keyword as the model creation): ")

    out = external_validation_wrapper(
        db_file=duckdb_file_path,
        metrics_dir=metrics_dir,
        model_dir=model_dir,
        figure_dir=figure_dir,
        keyword=keyword
        )

    for message in out:
        pprint(message)
