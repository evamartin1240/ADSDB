#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

"""
Contains some functions for plotting used in external validation
"""



def plot_y_test_y_pred(y_test, y_pred):
    # Create a DataFrame for seaborn plotting
    df = pd.DataFrame({'y_test': y_test, 'y_pred': y_pred})

    # Plot using Seaborn scatterplot
    plt.figure(figsize=(8, 6))
    sns.scatterplot(data=df, x='y_test', y='y_pred', color='blue', alpha=0.6)

    # Add line for perfect predictions
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], color='red', linestyle='--', lw=2)

    plt.xlabel('Real Followers')
    plt.ylabel('Predicted Followers')
    plt.title('Real vs Predicted Followers')

    return plt.gcf()


def plot_residuals(y_true, y_pred):

    residuals = y_true - y_pred
    residuals_df = pd.DataFrame({'Predicted': y_pred, 'Residuals': residuals})

    plt.figure(figsize=(8, 6))
    sns.scatterplot(data=residuals_df, x='Predicted', y='Residuals', color='blue', alpha = 0.6)
    plt.axhline(0, color='red', linestyle='--')
    plt.xlabel('Predicted Values')
    plt.ylabel('Residuals')
    plt.title('Residuals Plot')

    return plt.gcf()


def plot_model_metrics(models, metricsdir):
    import yaml
    import os

    data = []

    for model in models:
        filename = os.path.join(f"{metricsdir}{model}.yaml")

        # Read the YAML file for the current model
        with open(filename, 'r') as file:
            metrics = yaml.safe_load(file)

        # Add the extval metrics to the data list
        for metric, value in metrics.items():
            data.append({
                'Model': model,
                'Metric': metric,
                'Value': value
            })

    df = pd.DataFrame(data)

    # Plot all the metrics
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Metric', y='Value', hue='Model', data=df, palette="plasma")
    plt.title('Model Performance Comparison')
    plt.xticks(rotation=45)
    plt.tight_layout()

    return plt.gcf()
