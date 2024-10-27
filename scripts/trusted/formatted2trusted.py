import pandas as pd
import os
import duckdb

"""# Formatted to trusted:
Homogeneization of different version of data from same source into a single table.
"""

def formatted2trusted(duckdb_file_path, trusted_dir):
    """ Homogenize .duckdb files from the same source and add timestamps in order to keep track of the version.
    """
    # Initialize empty lists to store all the dataframes for Spotify and TicketMaster found in the formatted zone
    spotify_dfs = []
    ticketmaster_dfs = []

    # Connect to the DuckDB file
    con = duckdb.connect(database=duckdb_file_path, read_only=True)

    tables = con.execute("SHOW TABLES").fetchall()

    for table in tables:
        table_name = table[0]  # Extract table name from the result

        # Extract the source (either "spotify" or "ticketmaster") and date from the table name
        source, date = table_name.split('_', 1)         

        df = con.execute(f"SELECT * FROM {table_name}").df()

        # Add a new column with 'source_date' to store the date from the table name 
        df['source_date'] = date

        # Check if the table is a "spotify" or "ticketmaster" table and append to the respective list
        if 'spotify' in source:
            spotify_dfs.append(df)
        elif 'ticketmaster' in source:
            ticketmaster_dfs.append(df)

    # Close the connection after reading
    con.close()

    # Create the trusted directory if it doesn't exist
    if not os.path.exists(trusted_dir):
        os.makedirs(trusted_dir)

    # Create the trusted DuckDB database
    combined_duckdb_path = os.path.join(trusted_dir, 'trusted.duckdb')
    con = duckdb.connect(database=combined_duckdb_path)

    # Concatenate and save the resulting Spotify table into the DuckDB database
    if spotify_dfs:
        spotify_data = pd.concat(spotify_dfs, ignore_index=True)
        con.execute(f"DROP TABLE IF EXISTS {'spotify'}") # drop the table if it already existed
        con.execute("CREATE TABLE spotify AS SELECT * FROM spotify_data")
        print(f"Spotify dataset dimensions: {spotify_data.shape}")
        print("Spotify datasets homogenized and saved into the DuckDB file.")

    # Concatenate and save the resulting TicketMaster table into the DuckDB database
    if ticketmaster_dfs:
        ticketmaster_data = pd.concat(ticketmaster_dfs, ignore_index=True)
        con.execute(f"DROP TABLE IF EXISTS {'ticketmaster'}") # drop the table if it already existed
        con.execute("CREATE TABLE ticketmaster AS SELECT * FROM ticketmaster_data")
        print(f"TicketMaster dataset dimensions: {ticketmaster_data.shape}")
        print("TicketMaster datasets homogenized and saved into the DuckDB file.")

    # Close the DuckDB connection
    con.close()

if __name__ == "__main__":
    duckdb_file_path = input("Path to DuckDB file (input): ")
    trustdir_out = input("Trusted directory path (output): ")
    formatted2trusted(duckdb_file_path, trustdir_out)
