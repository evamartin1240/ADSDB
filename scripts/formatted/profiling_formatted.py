import pandas as pd
import matplotlib.pyplot as plt
import duckdb
from collections import Counter
import numpy as np
import warnings
import streamlit as st

warnings.filterwarnings("ignore")

""" Data Profiling
Generate summary statistics and visualizations to provide insights 
into the distribution of each table in the formatted DuckDB database.
"""

### Generic ###

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

    return na_table

def desc_stats(df):
    """
    Prints the descriptive statistics for all columns in the dataframe.
    """
    print("Descriptive analysis for all columns:")
    print('-'*40)
    print(df.describe(include='all'))

def plot_histogram(df, column, title, xlabel, ylabel, bins, ax):
    """
    Generic function to plot a histogram.
    """
    ax.hist(df[column].dropna(), bins=bins, color='maroon', edgecolor='black')
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)

### Spotify ###

def plot_genre(df, genre_column='genres', ax=None):
    """
    Function to plot the top 10 most common genres.
    """
    all_genres = [genre for sublist in df[genre_column].dropna() for genre in sublist]
    genre_counts = Counter(all_genres) # count all genres in the df

    # Get the top 10 most common genres
    top_genres = genre_counts.most_common(10)
    genres, counts = zip(*top_genres)  # Unzip the genres and their counts

    # Use ax if it is set
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))

    # Plotting
    ax.bar(genres, counts, color='maroon', edgecolor='black')
    ax.set_title('Top 10 most frequent genres')
    ax.set_xlabel('Genres')
    ax.set_ylabel('Frequency')
    ax.tick_params(axis='x', rotation=90)
    plt.tight_layout()

def plots_spotify(df, column_followers, column_popularity, title=None):
    """
    Function to plot the 3 Spotify plots in the same figure.
    """
    # Create subplots
    fig, axs = plt.subplots(1, 3, figsize=(10, 5))
    fig.tight_layout(pad=5.0)
    if title:
        fig.suptitle(title, fontsize=16)

    # Histogram of followers
    plot_histogram(df, column_followers, "Distribution of 'followers'",
                   'Followers', 'Count', bins=24, ax=axs[0])

    # Histogram of popularity
    plot_histogram(df, column_popularity, "Distribution of 'popularity'",
                   'Popularity', 'Count', bins=24, ax=axs[1])

    # Top 10 genres plot
    plot_genre(df, ax = axs[2])

    # Display
    plt.tight_layout()
    plt.show()
    return fig

### TicketMaster ###

def quick_data_prep_ticketmaster(df):
    """
    Specify format for columns and set missing values as NA.
    """
    df['time'] = pd.to_datetime(df['time'], format='%H:%M:%S', errors='coerce')
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d', errors='coerce')
    df['location'].replace(['N/A, N/A', 'NA'], np.nan, inplace=True)
    df['price_range'].replace(to_replace=r'.*N/A.*|.*NA.*', value=np.nan, regex=True, inplace=True)

def plot_country_events(df, column_country, ax):
    """
    Function to plot the number of events per country.
    """
    country_counts = df[column_country].dropna().value_counts()
    countries = country_counts.index
    values = country_counts.values

    # Select the top 20 countries with the highest event counts
    top_countries = country_counts.head(20)
    countries = top_countries.index
    values = top_countries.values

    ax.barh(countries, values, color='maroon')

    # Add text annotations at the end of each bar
    for index, value in enumerate(values):
        ax.text(value, index, str(value), va='center')

    ax.set_xlabel("No. of Events")
    ax.set_ylabel("Country")
    ax.set_title("Number of Events per Country")
    # Set smaller font size for country names
    ax.set_yticklabels(countries, fontsize=5)
    ax.invert_yaxis()

def plots_ticketmaster(df, column_time, column_date, column_country, title=None):
    """
    Function to plot the all TicketMaster plots in the same figure.
    """
    # Create subplots (2 rows x 3 columns grid)
    fig, axs = plt.subplots(2, 3, figsize=(18, 10))
    fig.tight_layout(pad=5.0)
    if title:
        fig.suptitle(title, fontsize=16)

    # Histogram of hours
    df['hour'] = df[column_time].dt.hour
    plot_histogram(df, 'hour', 'Distribution of Events by Hour of Day',
                   'Hour of the Day', 'Frequency', bins=24, ax=axs[0, 0])
    axs[0, 0].set_xticks(range(24))

    # Histogram of days of the month
    df['day'] = df[column_date].dt.day
    plot_histogram(df, 'day', 'Distribution of Events by Day of the Month',
                   'Day of the Month', 'Frequency', bins=31, ax=axs[0, 1])

    # Histogram of days of the week
    df['day_of_week'] = df[column_date].dt.dayofweek
    plot_histogram(df, 'day_of_week', 'Distribution of Events by Day of the Week',
                   'Day of the Week (0=Monday, 6=Sunday)', 'Frequency', bins=7, ax=axs[0, 2])

    # Time series of daily counts
    daily_counts = df[column_date].value_counts().sort_index()
    axs[1, 0].plot(daily_counts.index, daily_counts.values, color='maroon')
    axs[1, 0].set_xlabel('Date')
    axs[1, 0].set_ylabel('Number of Events')
    axs[1, 0].set_title('Number of Events Over Time')

    # Histogram of months
    df['month'] = df[column_date].dt.month
    plot_histogram(df, 'month', 'Distribution of Events by Month',
                   'Month', 'Frequency', bins=12, ax=axs[1, 1])

    # Plot number of events per country in the last subplot
    plot_country_events(df, column_country, ax=axs[1, 2])

    # Display
    plt.tight_layout()
    plt.show()
    return fig

def spotify_profiling(duckdb_file_path):
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
    tables = conn.execute("SHOW TABLES").fetchall()

    # Iterate over each table and if it is a Spotify table, print its statistics and build its plots
    for table in tables:
        table_name = table[0]
        # Extract the source (either "spotify" or "ticketmaster") and date from the table name
        source, date = table_name.split('_', 1)
        if source == 'spotify':
            df = conn.execute(f"SELECT * FROM {table_name}").df()
            print(f"\nTable: {table_name}")

            # Head of table
            print('-'*40)
            print('Table head (6 first lines of the table):')
            print('-'*40)
            print(df.head(6))
            print(f"Table {table_name} dimensions: {df.shape}")
            print('-'*40)

            # Descriptive stats all columns
            print('-'*40)
            desc_stats(df)

            # Missing values information
            print('-'*40)
            na_information(df)

            # Plots
            plots_spotify(df, 'followers', 'popularity', title=f"Table: {table_name}")
    conn.close()

def ticketmaster_profiling(duckdb_file_path):
    """
    Put together all the profiling analysis for the TicketMaster
    tables (decriptive statistics + plots).

    It provides an overview of each TicketMaster table by calculating
    descriptive statistics, checking for missing values and creating plots
    of the time, date, and location data.
    """
    # Connect to the DuckDB database
    conn = duckdb.connect(duckdb_file_path)

    # Fetch all table names in the database
    tables = conn.execute("SHOW TABLES").fetchall()

    # Iterate over each table and if it is a Spotify table, print its statistics and build its plots
    for table in tables:
        table_name = table[0]

        # Extract the source (either "spotify" or "ticketmaster") and date from the table name
        source, date = table_name.split('_', 1)
        if source == 'ticketmaster':
            df = conn.execute(f"SELECT * FROM {table_name}").df()

            quick_data_prep_ticketmaster(df)
            print(f"\nTable: {table_name}")

            # Head of table
            print('-'*40)
            print('Table head (6 first lines of the table):')
            print('-'*40)
            print(df.head(6))
            print(f"Table {table_name} dimensions: {df.shape}")
            print('-'*40)

            # Descriptive stats all columns
            print('-'*40)
            desc_stats(df)

            # Missing values information
            print('-'*40)
            na_information(df)

            # Plots
            plots_ticketmaster(df, 'time', 'date', 'location', title=f"Table: {table_name}")

    conn.close()

### APP adjusted functions ###

# Same function as spotify_profiling but adjusted for the streamlit app
def spotify_profiling_app(duckdb_file_path):
    # Connect to your DuckDB database
    conn = duckdb.connect(duckdb_file_path)
    tables = conn.execute("SHOW TABLES").fetchall()

    for table in tables:
        table_name = table[0]
        
        # Check the source of the table
        if 'spotify' in table_name:
            df = conn.execute(f"SELECT * FROM {table_name}").df()
            st.subheader(f"Profiling for table: {table_name}")

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

            fig = plots_spotify(df, 'followers', 'popularity', title=f"Table: {table_name}")
            st.pyplot(fig)

# Same function as spotify_profiling but adjusted for the streamlit app
def ticketmaster_profiling_app(duckdb_file_path):
    # Connect to your DuckDB database
    conn = duckdb.connect(duckdb_file_path)
    tables = conn.execute("SHOW TABLES").fetchall()

    for table in tables:
        table_name = table[0]

        # Check the source of the table
        if 'ticketmaster' in table_name:
            df = conn.execute(f"SELECT * FROM {table_name}").df()
            quick_data_prep_ticketmaster(df)

            st.subheader(f"Profiling for table: {table_name}")

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
            
            fig = plots_ticketmaster(df, 'time', 'date', 'location', title=f"Table: {table_name}")
            st.pyplot(fig)

if __name__ == "__main__":
    duckdb_file_path = input("Input DuckDB database (formatted): ")
    spotify_profiling(duckdb_file_path)
    ticketmaster_profiling(duckdb_file_path)