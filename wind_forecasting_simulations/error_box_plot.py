# error box plot

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import textwrap

def plot_error_box_plot(file_name):
    """
    Plot a box plot of wind speed prediction errors from a CSV file."
    """
    # Read error data
    df_error = pd.read_csv(file_name, usecols=[0])
    
    # Set up the figure and axes
    plt.figure(figsize=(10, 6))
    
    # Create a box plot for the error data
    sns.boxplot(data=df_error, palette="Set2")
    
    # Set title and labels
    plt.title('Box Plot of Wind Speed Prediction Errors', fontsize=16)
    plt.xlabel('Prediction Horizon', fontsize=14)
    plt.ylabel('Error (m/s)', fontsize=14)
    
    # Show the plot
    plt.show()

def plot_multiple_error_box_plot(file_name_1, 
                                 file_name_2=None, 
                                 file_name_3=None, 
                                 file_name_4=None,
                                 file_name_5=None,
                                 file_name_6=None,
                                 file_name_7=None,
                                 file_name_8=None,
                                 showfliers=True,
                                 plot_rmse_line=False,
                                 labels=None):
    """
    Plot multiple box plots of wind speed prediction errors from multiple CSV files in a single figure.
    Each file should contain one column titled 'error'.

    Parameters:
        showfliers (bool): Whether to display outliers in the box plot.
        plot_rmse_line (bool): Whether to plot a horizontal RMSE line for each model.
        labels (list): Custom labels for each box plot (must match number of files provided).
    """
    file_names = [file_name_1, file_name_2, file_name_3, file_name_4,
                  file_name_5, file_name_6, file_name_7, file_name_8]

    file_names = [f for f in file_names if f is not None]

    if labels and len(labels) != len(file_names):
        raise ValueError("Length of 'labels' must match number of non-None input files.")

    # Use provided labels or default ones
    plot_labels = labels if labels else [f'Model {i + 1}' for i in range(len(file_names))]

    error_data = []
    rmses = []

    for file in file_names:
        df = pd.read_csv(file, usecols=[0])
        column_name = df.columns[0]
        errors = df[column_name].dropna()
        error_data.append(errors)
        rmses.append(np.sqrt(np.mean(errors**2)))

    # Prepare long-form DataFrame
    error_df = pd.DataFrame({label: data.reset_index(drop=True) for label, data in zip(plot_labels, error_data)})
    error_df_long = pd.melt(error_df, var_name='Model', value_name='Error')

    # Create plot
    plt.figure(figsize=(12, 6))
    ax = sns.boxplot(x='Model', y='Error', data=error_df_long, palette='Set3', showfliers=showfliers)

    # Plot RMSE line per model
    if plot_rmse_line:
        for i, rmse in enumerate(rmses):
            ax.hlines(rmse, i - 0.4, i + 0.4, colors='red', linestyles='--', label='RMSE' if i == 0 else "")
        ax.legend(loc='upper right')

    # Wrap long x-axis labels
    wrapped_labels = ['\n'.join(textwrap.wrap(label, width=12)) for label in plot_labels]
    ax.set_xticklabels(wrapped_labels)

    # Set titles and labels
    plt.title('Comparison of Wind Speed Prediction Errors', fontsize=16)
    plt.xlabel('Prediction Model', fontsize=14)
    plt.ylabel('Error (m/s)', fontsize=14)

    plt.tight_layout()
    plt.show()


# Example usage
# if __name__ == "__main__":
#     # plot_error_box_plot('raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10_error_ph_40_NN.csv')
#     plot_multiple_error_box_plot('raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10_error_ph_10_baseline.csv',
#         'raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10_error_ph_10_ARMA.csv',
#         'raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10_error_ph_10_ARMA_updating.csv',
#         'raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10_error_ph_10_NN.csv',
#         'raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10_error_ph_10_RBF.csv',
#         'raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10_error_ph_10_RBF_update_weights.csv',
#         'raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10_error_ph_10_RBF_update_both.csv',
#         showfliers=False,
#         plot_rmse_line=True,
#         labels=['Baseline', 'ARMA', 'ARMA Updating', 'NN', 'RBF', 'RBF Update Weights', 'RBF Update Weights + centres'])

if __name__ == "__main__":
    # plot_error_box_plot('raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10_error_ph_40_NN.csv')
    plot_multiple_error_box_plot('raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10_error_ph_40_baseline.csv',
        'raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10_error_ph_40_ARMA.csv',
        'raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10_error_ph_40_ARMA_updating.csv',
        'raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10_error_ph_40_NN.csv',
        'raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10_error_ph_40_RBF.csv',
        'raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10_error_ph_40_RBF_update_weights.csv',
        'raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10_error_ph_40_RBF_update_both.csv',
        'raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10_error_ph_40_RBF_update_downdate_weights.csv',
        showfliers=False,
        plot_rmse_line=True,
        labels=['Baseline', 'ARMA', 'ARMA Updating', 'NN', 'RBF', 'RBF Update Weights', 'RBF Update Weights + centres', 'RBF update + downdate weights'])
