import pandas as pd
import json
import os

"""# Persistent landing zone to formatted zone
Take all the files in the system (persistent landing zone) and unify the formats.
"""

def convert_json_to_csv(json_file_path, csv_file_path):
  """ Function to convert json to csv.
  """

  with open(json_file_path, 'r') as json_file:
    data = json.load(json_file)

    # Convertir el JSON a un DataFrame
    df = pd.json_normalize(data)

    # Guardar como archivo CSV
    df.to_csv(csv_file_path, index=False)
    print(f'CSV file saved: {csv_file_path}')

def landing2formatted(persdir_in, formdir_out):
    """ Function to iterate over JSON files in the persistent directory,
        convert them to CSV, and save in the formatted directory.
    """

    if not os.path.exists(formdir_out): # If the formatted directory doesn't exist, create it
       os.makedirs(formdir_out)

    # Iterate over all the files in the persistent directory to change the format from JSON to CSV
    for root, dirs, files in os.walk(persdir_in):
        for file in files:
            if file.endswith('.json'):  # Only process .json files
                json_file_path = os.path.join(root, file)
                csv_file_name = file.replace('.json', '.csv')
                csv_file_path = os.path.join(formdir_out, csv_file_name)
                convert_json_to_csv(json_file_path, csv_file_path)

if __name__ == "__main__":
    persdir_in = input("Persistent landing directory path (input): ")
    formdir_out = input("Formatted landing directory path (output): ")

    landing2formatted(persdir_in, formdir_out)