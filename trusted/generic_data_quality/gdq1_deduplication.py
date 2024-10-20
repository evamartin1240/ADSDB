import pandas as pd
import os

"""# Generic data quality - Deduplication"""

def deduplication(in_file_name, out_file_name, ignore_column=None, filter_conditions=None):
  """
  Deduplicate a dataframe based on all columns or a subset if an ignore_column is provided.

  Parameters:
  - in_file_name: Path to the input CSV file.
  - out_file_name: Path to save the deduplicated CSV file.
  - ignore_column: (Optional) Column name to be ignored during deduplication.
  - filter_conditions: (Optional) Filter condition to select just a portion of the dataset.
  """
  # Read the csv file into a pandas dataframe
  df = pd.read_csv(in_file_name)
  print(f"Number of rows original dataframe: {df.shape[0]}")

  # Apply filter conditions if provided
  if filter_conditions:
    for col, value in filter_conditions.items():
      df = df.loc[df[col] == value]
      print(f"Dataframe filtered by {col} = {value}: {df.shape[0]} rows")

  # Define the subset of columns for deduplication
  if ignore_column:
    subset = df.columns.drop(ignore_column).tolist()
  else:
    subset = df.columns.tolist()

  # Remove duplicates based on the subset
  df_deduplicated = df.drop_duplicates(subset=subset)
  print(f"Number of rows after deduplication: {df_deduplicated.shape[0]}")

  # Save the deduplicated dataframe to csv
  df_deduplicated.to_csv(out_file_name, index=False)

  print(f"Deduplicated CSV saved as {out_file_name}")

  return df_deduplicated

if __name__ == "__main__":
    in_file_name = input("Enter the path of the CSV file to deduplicate: ")
    out_file_name = input("Enter the output file name (including .csv): ")

    ignore_column = input("Enter the column name to ignore during deduplication (or press Enter to skip): ")
    ignore_column = ignore_column if ignore_column else None

    filter_conditions = {}
    filter_condition_input = input("Do you want to filter the DataFrame? (yes/no): ").strip().lower()
    
    if filter_condition_input == 'yes':
        column = input("Enter the column name to filter on (or press Enter to finish): ")
        value = input(f"Enter the value for '{column}': ")
        filter_conditions[column] = int(value)
        print(filter_conditions)

    # Call the deduplication function
    deduplication(in_file_name, out_file_name, ignore_column, filter_conditions)