import duckdb
import pandas 

def deduplication(db_file):
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
            print(f"TicketMaster dataset dimensions: {df_deduplicated.shape}")
        else:  # for spotify
            df_deduplicated = df.drop_duplicates(subset=['artist', 'source_date'])
            print(f"Spotify dataset dimensions: {df_deduplicated.shape}")
        
        # Save the deduplicated DataFrame back to DuckDB
        conn.execute(f"DROP TABLE IF EXISTS {table}")
        conn.execute(f"CREATE TABLE {table} AS SELECT * FROM df_deduplicated")

    # Close the connection
    conn.close()

# Example usage
deduplication('/Users/evamartin/Desktop/MDS/curs1/ADSDB_copia/data/probando_trusted/trusted.duckdb')