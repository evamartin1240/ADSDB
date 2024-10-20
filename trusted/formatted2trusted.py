import pandas as pd
import os

"""# Formatted to trusted:
Homogeneization of different version of data from same source into a single table.
"""

def formatted2trusted(formatted_dir, trusted_dir):
    """ Homogenize .csvs from same source and add timestamps in order to keep track of the version.
    """
  
    # Initialize empty lists to store all the dataframes for Spotify and TicketMaster found in the formatted zone
    spotify_dfs = []
    ticketmaster_dfs = []

    for file_name in os.listdir(formatted_dir): # Loop through all files in the formatted directory
        if file_name.endswith('.csv'): # Check if the file is a .csv
            file_path = os.path.join(formatted_dir, file_name)

            # Extract the source (either "spotify" or "ticketmaster") and date from the filename
            source, date = file_name.split('_')[0], file_name.split('_')[1].replace('.csv', '')

            # Load the CSV file into a DataFrame
            df = pd.read_csv(file_path)

            # Add a new column with 'source_date' to store the date from the file (in order to keep track of data versions)
            df['source_date'] = date

            # Check if the file is a "spotify" or "ticketmaster" file and append to the respective list
            if 'spotify' in file_name.lower():
                spotify_dfs.append(df)
            elif 'ticketmaster' in file_name.lower():
                ticketmaster_dfs.append(df)

    if not os.path.exists(trusted_dir):
            os.makedirs(trusted_dir)

    # Concatenate all the Spotify dataframes into a single dataframe
    if spotify_dfs:
        spotify_data = pd.concat(spotify_dfs, ignore_index=True)
        spotify_data.to_csv(os.path.join(trusted_dir, 'spotify_homogenized_dataset.csv'), index=False)
        print("Spotify datasets homogenized into a single table.")

    # Concatenate all the TicketMaster dataframes into a single dataframe
    if ticketmaster_dfs:
        ticketmaster_data = pd.concat(ticketmaster_dfs, ignore_index=True)
        ticketmaster_data.to_csv(os.path.join(trusted_dir, 'ticketmaster_homogenized_dataset.csv'), index=False)
        print("TicketMaster datasets homogenized into a single table.")

if __name__ == "__main__":
    formatted_dir = '/Users/evamartin/Desktop/MDS/curs1/ADSDB/formatted' # Formatted directory
    trusted_dir = '/Users/evamartin/Desktop/MDS/curs1/ADSDB/trusted' # Trusted directory
    formatted2trusted(formatted_dir, trusted_dir)