import csv

def reorder_csv_by_second_column(file_name):
    """
    Reorder the rows in a CSV file in ascending order according to the value in the second column.

    Parameters:
    - input_file: str, path to the input CSV file
    - output_file: str, path to the output CSV file
    """
    # Read the data from the input file
    with open(f'{file_name}.csv', 'r') as file:
        reader = csv.reader(file)
        data = list(reader)

    # Sort the data by the value in the second column (index 1)
    sorted_data = sorted(data, key=lambda row: float(row[1]))

    # Write the sorted data to the output file
    with open(f'{file_name}_____________SORTED.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(sorted_data)

    print(f"Data has been sorted and written to {file_name}_____________SORTED.csv ")

# Example usage
if __name__ == "__main__":
    file_name_1 = 'raspberry/data/wind_data/16-09-23--18-35/16-09-23--18-35_N_10_Simple_ARMA_24000-28800_U_combined_quantile_errors'
    file_name_2 = 'raspberry/data/wind_data/16-09-23--18-35/16-09-23--18-35_N_10_Simple_ARMA_24000-28800_U_combined_RMSE'
    file_name_3 = 'raspberry/data/wind_data/16-09-23--18-35/16-09-23--18-35_N_10_Simple_ARMA_24000-28800_U_last_step_quantile_error'
    file_name_4 = 'raspberry/data/wind_data/16-09-23--18-35/16-09-23--18-35_N_10_Simple_ARMA_24000-28800_U_last_step_RMSE'
    file_name_5 = 'raspberry/data/wind_data/16-09-23--18-35/16-09-23--18-35_N_10_Simple_ARMA_24000-28800_V_combined_quantile_errors'
    file_name_6 = 'raspberry/data/wind_data/16-09-23--18-35/16-09-23--18-35_N_10_Simple_ARMA_24000-28800_V_combined_RMSE'
    file_name_7 = 'raspberry/data/wind_data/16-09-23--18-35/16-09-23--18-35_N_10_Simple_ARMA_24000-28800_V_last_step_quantile_error'
    file_name_8 = 'raspberry/data/wind_data/16-09-23--18-35/16-09-23--18-35_N_10_Simple_ARMA_24000-28800_V_last_step_RMSE'
    file_name_9 = 'raspberry/data/wind_data/16-09-23--18-35/16-09-23--18-35_N_10_Simple_ARMA_24000-28800_W_combined_quantile_errors'
    file_name_10 = 'raspberry/data/wind_data/16-09-23--18-35/16-09-23--18-35_N_10_Simple_ARMA_24000-28800_W_combined_RMSE'
    file_name_11 = 'raspberry/data/wind_data/16-09-23--18-35/16-09-23--18-35_N_10_Simple_ARMA_24000-28800_W_last_step_quantile_error'
    file_name_12 = 'raspberry/data/wind_data/16-09-23--18-35/16-09-23--18-35_N_10_Simple_ARMA_24000-28800_W_last_step_RMSE'
    reorder_csv_by_second_column(file_name_1)
    reorder_csv_by_second_column(file_name_2)
    reorder_csv_by_second_column(file_name_3)
    reorder_csv_by_second_column(file_name_4)
    reorder_csv_by_second_column(file_name_5)
    reorder_csv_by_second_column(file_name_6)
    reorder_csv_by_second_column(file_name_7)
    reorder_csv_by_second_column(file_name_8)
    reorder_csv_by_second_column(file_name_9)
    reorder_csv_by_second_column(file_name_10)
    reorder_csv_by_second_column(file_name_11)
    reorder_csv_by_second_column(file_name_12)