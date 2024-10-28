import duckdb

def deduplication(db_file):
    """
    Removes duplicates from the tables 'ticketmaster' and 'spotify', with a different deduplication logic for each table.

    - For TicketMaster data, duplicates are removed across all columns except the `source_date` 
      column (indicating the version). This approach ensures that the function only retains unique events, 
      as duplicates without `source_date` differences represent identical events with no new information.

    - For Spotify data, the function removes duplicates that share both the same `artist` and `source_date`, 
      addressing accidental duplicates from the same data version. Duplicates between different `source_date` 
      entries are kept, as they represent the same artist data collected on different dates, 
      which is useful for tracking changes over time.
    """
    # List to store the output messages in order to print them later
    output = []
    
    # Connect to the DuckDB database
    conn = duckdb.connect(database=db_file, read_only=False)
    
    # Table names and ignore column
    tables = ['ticketmaster', 'spotify']
    
    for table in tables:
        # Load table into a DataFrame
        df = conn.execute(f"SELECT * FROM {table}").df()
        
        # Define the subset of columns for deduplication
        if table == 'ticketmaster':
            subset = df.columns.drop('source_date').tolist()
            # Remove duplicates based on the subset
            df_deduplicated = df.drop_duplicates(subset=subset)
            output.append(f"TicketMaster dataset dimensions after deduplication: {df_deduplicated.shape}")
        else:  # for spotify
            df_deduplicated = df.drop_duplicates(subset=['artist', 'source_date'])
            output.append(f"Spotify dataset dimensions after deduplication: {df_deduplicated.shape}")
        
        # Save the deduplicated DataFrame back to DuckDB
        conn.execute(f"DROP TABLE IF EXISTS {table}")
        conn.execute(f"CREATE TABLE {table} AS SELECT * FROM df_deduplicated")

    # Close the connection
    conn.close()
    
    return output

# deduplication('/Users/evamartin/Desktop/MDS/curs1/ADSDB_copia/data/probando_trusted/trusted.duckdb')
if __name__ == "__main__":
    duckdb_file_path = input("Path to DuckDB file (input): ")
    out = deduplication(duckdb_file_path)
    for message in out:
        print(message)