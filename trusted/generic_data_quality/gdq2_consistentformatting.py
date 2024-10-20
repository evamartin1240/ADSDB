import pandas as pd
from datetime import datetime
import numpy as np

"""# Consistent formatting
Date, time, location, and price variables will be standardized for uniformity across the dataset.
"""

"""## Date
Date format from 'YYYY-MM-DD' to 'DD-MM-YYYY'.
"""

def clean_date_format(df, date_column):
  """ Function to check date format and convert to DD-MM-YYYY, keeping missing values
  """
  # Function to check if a string is in 'YYYY-MM-DD' format or NaN, then convert to 'DD-MM-YYYY'.
  def is_valid_date(date_str):
    if pd.isna(date_str):
      return date_str
    elif isinstance(date_str, str):
      try:
        # Parse the date in 'YYYY-MM-DD' format
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        # Convert to 'DD-MM-YYYY' format
        return date_obj.strftime('%d-%m-%Y')
      except ValueError:
        return np.nan  # Return NaN for invalid dates
    return np.nan  # Return NaN for non-strings

  # Apply the validation and conversion function to the date column
  df[date_column] = df[date_column].apply(is_valid_date)
  return df

"""## Time
Time format as 'H:M:S'.
"""

def clean_time_format(df, time_column):
    """ Function to check and clean time format in 'HH:MM:SS', keeping missing values. """

    # Function to check if a string is in 'HH:MM:SS' format or NaN
    def is_valid_time(time_str):
        if pd.isna(time_str):  # Allow NaN values
            return time_str
        elif isinstance(time_str, str):  # Check if the value is a string
            try:
                datetime.strptime(time_str, '%H:%M:%S')  # Check if it's in 'HH:MM:SS' format
                return time_str
            except ValueError:
                return np.nan  # Return NaN for invalid times
        return np.nan  # Return NaN if it's not a string

    # Apply the validation function to the time column, replacing invalid times with NaN
    df[time_column] = df[time_column].apply(is_valid_time)

    return df

"""## Location
Location format from city, country into two separate columns 'city' and 'country'.
"""

def clean_location_format(df, location_column):
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
    df[['city', 'country']] = df[location_column].apply(lambda x: pd.Series(split_location(x)))

    return df

"""## Price
Range price format in EUR and split in columns min_price_EUR and max_price_EUR:

Since the price_range column contains prices in different currencies, we will first extract the unique currencies and then convert everything to euros.
"""

def get_unique_currencies(df, price_column):
    """ Function to extract unique currencies from the price_column. """

    # Function to extract the currency from each price_range
    def extract_currency(price_range):
        if pd.isna(price_range):
            return np.nan
        try:
            # Extract the currency by splitting on the last space
            return price_range.rsplit(' ', 1)[-1]
        except:
            return np.nan

    # Extract currencies and return unique non-NaN values
    unique_currencies = df[price_column].apply(extract_currency).dropna().unique()

    return unique_currencies

# get_unique_currencies(ticketmaster_data, 'price_range')

"""Once we know the different currencies, we will manually create a dictionary containing the exchange rates for converting to euros and will convert all prices to euros."""

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

    return (round(min_price, 2), round(max_price, 2))

# Function to clean and convert price_range to min_price and max_price in EUR
def clean_price_range_format(df, price_column):
  # Apply the process_price_range function and split the result into two columns
  df[['min_price_EUR', 'max_price_EUR']] = df[price_column].apply(lambda x: pd.Series(process_price_range(x)))
  return df

if __name__ == "__main__":
    in_file_name = input("Enter the path of the CSV file for consistent formatting: ")
    out_file_name = input("Enter the output file name (including .csv): ")

    df = pd.read_csv(in_file_name)

    required_columns = ['date', 'time', 'location', 'price_range']

    # Check if the DataFrame contains the required columns
    if all(col in df.columns for col in required_columns):
        df = clean_date_format(df, 'date')
        df = clean_time_format(df, 'time')
        df = clean_location_format(df, 'location')
        df = clean_price_range_format(df, 'price_range')
        print("DataFrame consistently formatted successfully.")
    else:
        print("The DataFrame already has consistent formatting or is missing required columns.")
    
    df.to_csv(out_file_name, index=False)

