import sys
import streamlit as st
import duckdb
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, './scripts/formatted')

from profiling_formatted import desc_stats
from profiling_formatted import plots_spotify
from profiling_formatted import plots_ticketmaster
from profiling_formatted import plot_histogram

def na_information(df):
    """
    Returns a table with the count and percentage of missing values in each column of the dataframe.
    """
    print("Missing values (NAs) information:")
    print('-'*40)

    # Count of NAs in each column
    na_counts = df.isna().sum()

    na_table = pd.DataFrame({
        'Column': na_counts.index,
        'Number of NAs': na_counts.values,
        'Percentage of NAs (%)': ((na_counts.values / len(df)) * 100).round(2)
    })
    print(na_table)
    return na_table

def spotify_profiling_trusted(duckdb_file_path):
    """
    Put together all the profiling analysis for the Spotify
    tables (decriptive statistics + plots).

    It provides an overview of each Spotify table by calculating
    descriptive statistics, checking for missing values and creating plots
    of the followers, popularity, and genres data.
    """
    # Connect to the DuckDB database
    conn = duckdb.connect(duckdb_file_path)

    # Fetch all table names in the database
    tables = ['spotify', 'ticketmaster']

    # Iterate over each table and if it is a Spotify table, print its statistics and build its plots
    for table in tables:
        
        if table == 'spotify':
            df = conn.execute(f"SELECT * FROM {table}").df()
            print(f"\nTable: {table}")

            # Head of table
            print('-'*40)
            print('Table head (6 first lines of the table):')
            print('-'*40)
            print(df.head(6))
            print(f"Table {table} dimensions: {df.shape}")
            print('-'*40)

            # Descriptive stats all columns
            print('-'*40)
            desc_stats(df)

            # Missing values information
            print('-'*40)
            na_information(df)

            # Plots
            plots_spotify(df, 'followers', 'popularity', title=f"Table: {table}")
    conn.close()

def ticketmaster_profiling_trusted(duckdb_file_path):
    """
    Put together all the profiling analysis for the TicketMaster
    tables (decriptive statistics + plots).

    It provides an overview of each TicketMaster table by calculating
    descriptive statistics, checking for missing values and creating plots
    of the time, date, and location data.
    """
    # Connect to the DuckDB database
    conn = duckdb.connect(duckdb_file_path)

    # Update max_price_EUR values greater than 10000 to NA
    conn.execute("""
        UPDATE ticketmaster
        SET max_price_EUR = NULL
        WHERE max_price_EUR > 10000
    """)

    # Fetch all table names in the database
    tables = ['spotify', 'ticketmaster']

    # Iterate over each table and if it is a Spotify table, print its statistics and build its plots
    for table in tables:
        
        if table == 'ticketmaster':
            df = conn.execute(f"SELECT * FROM {table}").df()
            df['time'] = pd.to_datetime(df['time'], format='%H:%M:%S', errors='coerce')
            df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')

            print(f"\nTable: {table}")

            # Head of table
            print('-'*40)
            print('Table head (6 first lines of the table):')
            print('-'*40)
            print(df.head(6))
            print(f"Table {table} dimensions: {df.shape}")
            print('-'*40)

            # Descriptive stats all columns
            print('-'*40)
            desc_stats(df)

            # Missing values information
            print('-'*40)
            na_information(df)

            # Plots
            plots_ticketmaster(df, 'time', 'date', 'country', title=f"Table: {table}")

            # Min/max prices histograms
            fig, axes = plt.subplots(1, 2, figsize=(12, 6))
            plot_histogram(df, 'min_price_EUR', 'Distribution of Minimum Ticket Prices',
                              'Price', 'Frequency', bins=40, ax=axes[0])
            plot_histogram(df, 'max_price_EUR', 'Distribution of Maximum Ticket Prices',
                   'Price', 'Frequency', bins=40, ax=axes[1])

    conn.close()

### APP adjusted functions ###

# Same function as spotify_profiling but adjusted for the streamlit app
def spotify_profiling_app_trusted(duckdb_file_path):
    # Connect to your DuckDB database
    conn = duckdb.connect(duckdb_file_path)
    tables = ['spotify', 'ticketmaster']

    for table in tables:
        
        
        # Check the source of the table
        if table == 'spotify':
            df = conn.execute(f"SELECT * FROM {table}").df()
            st.subheader(f"Profiling for table: {table}")

            st.write("**Head table**")
            st.dataframe(df.head(6))
            st.write(f"Dimensions of the table: {df.shape}")

            # Describe() tables for numerical and non-numerical columns           
            num_summary = df.describe()  # Summary of numerical columns
            cat_summary = df.describe(include=['object', 'category'])  # Summary of categorical columns

            # Create the two columns that will allow to have both tables in same row
            col1, col2, col3 = st.columns(3)

            # Displaying numerical summary in the first column
            with col1:
                st.write("**Numerical columns summary**")
                st.dataframe(num_summary) 

            # Displaying categorical summary in the second column
            with col2:
                st.write("**Categorical columns summary**")
                st.dataframe(cat_summary)  

            # Displaying NA information in the third column
            with col3:
                st.write("**Missing values information**")
                st.dataframe(na_information(df))

            fig = plots_spotify(df, 'followers', 'popularity', title=f"Table: {table}")
            st.pyplot(fig)

# Same function as spotify_profiling but adjusted for the streamlit app
def ticketmaster_profiling_app_trusted(duckdb_file_path):
    # Connect to your DuckDB database
    conn = duckdb.connect(duckdb_file_path)
    tables = ['spotify', 'ticketmaster']

    # Update max_price_EUR values greater than 10000 to NA
    conn.execute("""
        UPDATE ticketmaster
        SET max_price_EUR = NULL
        WHERE max_price_EUR > 10000
    """)
    
    for table in tables:

        # Check the source of the table
        if table == 'ticketmaster':
            df = conn.execute(f"SELECT * FROM {table}").df()
            df['time'] = pd.to_datetime(df['time'], format='%H:%M:%S', errors='coerce')
            df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')

            st.subheader(f"Profiling for table: {table}")

            st.write("**Head table**")
            st.dataframe(df.head(6))
            st.write(f"Dimensions of the table: {df.shape}")

            # Describe() tables for numerical and non-numerical columns           
            num_summary = df.describe()  # Summary of numerical columns
            cat_summary = df.describe(include=['object', 'category'])  # Summary of categorical columns

            # Create the two columns that will allow to have both tables in same row
            col1, col2 = st.columns(2)

            # Displaying numerical summary in the first column
            with col1:
                st.write("**Numerical columns summary**")
                st.dataframe(num_summary) 

            # Displaying categorical summary in the second column
            with col2:
                st.write("**Categorical columns summary**")
                st.dataframe(cat_summary)  
            
            st.write("**Missing values information**")
            st.dataframe(na_information(df))
            
            fig = plots_ticketmaster(df, 'time', 'date', 'country', title=f"Table: {table}")
            st.pyplot(fig)

            # Add Min/max prices histograms
            fig, axes = plt.subplots(1, 2, figsize=(10, 4))
            plot_histogram(df, 'min_price_EUR', 'Distribution of Minimum Ticket Prices',
                              'Price', 'Frequency', bins=40, ax=axes[0])
            plot_histogram(df, 'max_price_EUR', 'Distribution of Maximum Ticket Prices',
                   'Price', 'Frequency', bins=40, ax=axes[1])
            st.pyplot(fig)

if __name__ == "__main__":
    duckdb_file_path = input("Input DuckDB database (trusted): ")
    spotify_profiling_trusted(duckdb_file_path)
    ticketmaster_profiling_trusted(duckdb_file_path)