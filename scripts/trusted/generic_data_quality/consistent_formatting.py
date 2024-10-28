import duckdb
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

"""# Consistent formatting
Date, time, location, and price variables will be formatted to unify all entries accross the dataset.

## Quick data preparation
In this first step, all missing values—represented by variations like 'NA', 'N/A', 'NA/NA', and others—will be combined into a single NA value using the np.nan object.
"""

def quick_data_prep_ticketmaster(db_file):
    """
    Specify format for columns and set missing values as NA,
    then store changes in the DuckDB database.
    """

    # Connect to DuckDB database
    conn = duckdb.connect(database=db_file, read_only=False)
    # Fetch all table names in the database
    tables = ['spotify', 'ticketmaster']

    # Iterate over each table
    for table in tables:

        if table == 'ticketmaster':
            df = conn.execute(f"SELECT * FROM {table}").df()

            # Transformations
            df['time'] = pd.to_datetime(df['time'], format='%H:%M:%S', errors='coerce')
            df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d', errors='coerce')
            df['location'].replace(['N/A, N/A', 'NA'], np.nan, inplace=True)
            df['price_range'].replace(to_replace=r'.*N/A.*|.*NA.*', value=np.nan, regex=True, inplace=True)
            df['venue'].replace(to_replace=r'.*N/A.*|.*NA.*', value=np.nan, regex=True, inplace=True)

        if table == 'spotify':
            df = conn.execute(f"SELECT * FROM {table}").df()

            # Set np.nan for empty genres lists
            df['genres'] = df['genres'].apply(lambda x: 'NA' if len(x) == 0 else x)

        # Drop the existing table and write back the transformed data
        conn.execute(f"DROP TABLE IF EXISTS {table}")
        conn.execute(f"CREATE TABLE {table} AS SELECT * FROM df")

    # Close connection
    conn.close()

"""### a) Date formatting
Format dates from 'YYYY-MM-DD' to 'DD-MM-YYYY'. Additionally, the time and date columns will be checked, and any dates beyond the year 2040 will be marked as invalid and set to NA
"""

def clean_date_format(df):
    """
    Prepare data by formatting columns, handling missing values, and replacing dates later than 2040 with NA.
    """
    # Ensure the 'date' column is converted to datetime, forcing invalid formats to NaT
    #df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%d-%m-%Y')
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # Now we can safely filter dates greater than 2040-12-31
    df.loc[df['date'].dt.year > 2035, 'date'] = pd.NaT


    return df

"""### b) Location formatting"""

def clean_location_format(df):
    """ # Function to clean and split the location column into city and country.
    """
    # Function to split the location into city and country
    def split_location(location):
        if pd.isna(location):  # Leave NaNs as they are
            return (np.nan, np.nan)
        try:
            # Split by the last comma, as the country comes after the last comma
            city, country = location.rsplit(',', 1)
            return (city.strip(), country.strip())
        except Exception:
            # If splitting fails, return NaNs
            return (np.nan, np.nan)

    # Apply the split_location function and create new columns
    df[['city', 'country']] = df['location'].apply(lambda x: pd.Series(split_location(x)))
    df.drop(columns=['location'], inplace=True)

    return df

"""## c) Price range formatting
Range price format in EUR and split in columns min_price_EUR and max_price_EUR:
"""

def process_price_range(price_range):
    if pd.isna(price_range):  # Leave NaNs as they are
        return (np.nan, np.nan)
    EXCHANGE_RATES = {
        'EUR': 1.0,    # 1 EUR = 1 EUR
        'USD': 0.95,   # 1 USD = 0.95 EUR
        'GBP': 1.16,   # 1 GBP = 1.16 EUR
        'CAD': 0.69,   # 1 CAD = 0.69 EUR
        'AED': 0.26,   # 1 AED = 0.26 EUR
        'AUD': 0.60,   # 1 AUD = 0.60 EUR
        'NZD': 0.57,   # 1 NZD = 0.57 EUR
        'CZK': 0.04,   # 1 CZK = 0.04 EUR
        'MXN': 0.048,  # 1 MXN = 0.048 EUR
        'PLN': 0.22,   # 1 PLN = 0.22 EUR
        'DKK': 0.13,   # 1 DKK = 0.13 EUR
        'NOK': 0.088,  # 1 NOK = 0.088 EUR
        'SEK': 0.086,  # 1 SEK = 0.086 EUR
        'ZAR': 0.049   # 1 ZAR = 0.049 EUR
        }

    # Split the price and extract currency
    # Split the range part and currency part (e.g., '32.5-32.5 EUR' -> ['32.5', '32.5'], 'EUR')
    prices, currency = price_range.rsplit(' ', 1)
    min_price, max_price = prices.split('-')


    # Convert to float
    try:
        # Convert to float
        min_price = float(min_price)
        max_price = float(max_price)
    except ValueError:
        return (np.nan, np.nan)


    # Convert to EUR based on currency
    if currency in EXCHANGE_RATES:
        min_price *= EXCHANGE_RATES[currency]
        max_price *= EXCHANGE_RATES[currency]
    else:
        # If currency is unknown, return NaN
        return (np.nan, np.nan)

    return (min_price, max_price)

# Function to clean and convert price_range to min_price and max_price in EUR
def clean_price_range_format(df):
  # Apply the process_price_range function and split the result into two columns
  df[['min_price_EUR', 'max_price_EUR']] = df['price_range'].apply(lambda x: pd.Series(process_price_range(x)))
  return df

def consistent_formatting(db_file):
    quick_data_prep_ticketmaster(db_file)

    conn = duckdb.connect(database=db_file, read_only=False)
    df_ticket = conn.execute(f"SELECT * FROM {'ticketmaster'}").df()

    # Clean columns
    df_ticket = clean_date_format(df_ticket)
    df_ticket = clean_location_format(df_ticket)
    df_ticket = clean_price_range_format(df_ticket)
    print(df_ticket.head())

    # Save changes in the database
    conn.execute(f"DROP TABLE IF EXISTS {'ticketmaster'}")
    conn.execute(f"CREATE TABLE {'ticketmaster'} AS SELECT * FROM df_ticket")
    conn.close()

if __name__ == "__main__":
    duckdb_file_path = input("Input DuckDB database (trusted): ")
    consistent_formatting(duckdb_file_path)    