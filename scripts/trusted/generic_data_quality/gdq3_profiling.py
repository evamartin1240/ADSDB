import pandas as pd
import matplotlib.pyplot as plt

# Define a function for descriptive analysis of numerical columns
def desc_num_cols(df):
    """
    Prints the descriptive statistics for numerical columns in the dataframe.

    Parameters:
    df (pandas.DataFrame): The input dataframe.
    """
    print("Descriptive analysis for numerical columns:")
    print('-'*40)
    print(df.describe())

def desc_time_date_col(df, time_column, col_type='date'):
    """
    Prints the descriptive statistics for the specified column in the dataframe.

    Parameters:
    df (pandas.DataFrame): The input dataframe.
    time_column (str): The name of the time or date column.
    col_type (str): Type of the column, either 'date' or 'time'.
    """
    if col_type not in ['date', 'time']:
        raise ValueError("col_type must be either 'date' or 'time'")

    print(f"Descriptive analysis for '{time_column}' column:")
    print('-'*40)
    
    if col_type == 'date':
        print(f"Min Date: {df[time_column].min()}")
        print(f"Max Date: {df[time_column].max()}")
        print(f"Unique Dates: {df[time_column].nunique()}")
        print(f"Most Frequent Date: {df[time_column].mode()[0]}")
        
    elif col_type == 'time':
        print(f"Min Time: {df[time_column].min()}")
        print(f"Max Time: {df[time_column].max()}")
        print(f"Unique Times: {df[time_column].nunique()}")
        print(f"Most Frequent Time: {df[time_column].mode()[0]}")

def na_information(df):
    """
    Prints a table with the count and percentage of missing values (NAs) in each column of the DataFrame.

    Parameters:
    df (pandas.DataFrame): The input DataFrame.
    """
    print("Missing values (NAs) information:")
    print('-'*40)

    # Count of NAs in each column
    na_counts = df.isna().sum()
    
    # Create a DataFrame to summarize NAs
    na_table = pd.DataFrame({
        'Column': na_counts.index,
        'Number of NAs': na_counts.values,
        'Percentage of NAs (%)': ((na_counts.values / len(df)) * 100).round(2)
    })
    
    # Print the NA information table
    print(na_table)

# Generic function to plot a histogram
def plot_histogram(df, column, title, xlabel, ylabel, bins, ax):
    ax.hist(df[column].dropna(), bins=bins, color='maroon', edgecolor='black')
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)

# Function to plot the number of events per country
def plot_country_events(df, column_country, ax):
    country_counts = df[column_country].value_counts()
    countries = country_counts.index
    values = country_counts.values
    
    ax.barh(countries, values, color='maroon')
    
    # Add text annotations at the end of each bar
    for index, value in enumerate(values):
        ax.text(value, index, str(value), va='center')
    
    ax.set_xlabel("No. of Events")
    ax.set_ylabel("Country")
    ax.set_title("Number of Events per Country")
    ax.invert_yaxis()

# Function to plot all histograms and the bar chart in a grid layout
def plot_all_together(df, column_time, column_date, column_country):
    # Create subplots (2 rows x 3 columns grid)
    fig, axs = plt.subplots(2, 3, figsize=(18, 10))
    fig.tight_layout(pad=5.0)

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

    # Time series of daily counts (this one is not a histogram)
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

    # Adjust layout and display the plots
    plt.tight_layout()
    plt.show()


def city_country_info(df, city_column='city', country_column='country'):
    print(f"Descriptive analysis for city and country columns:")
    print('-'*40)

    # Unique counts
    unique_cities = df[city_column].nunique()
    unique_countries = df[country_column].nunique()
    
    print(f"Unique cities: {unique_cities}")
    print(f"Unique countries: {unique_countries}")

    
    # Most frequent
    most_frequent_city = df[city_column].mode()[0]
    most_frequent_country = df[country_column].mode()[0]
    
    print(f"Most frequent city: {most_frequent_city}")
    print(f"Most frequent country: {most_frequent_country}")

    # Frequency counts
    city_counts = df[city_column].value_counts()
    country_counts = df[country_column].value_counts()
    # Proportions
    city_proportions = ((city_counts / len(df)) * 100).round(2)
    country_proportions = ((country_counts / len(df)) * 100).round(2)
    
    # Create DataFrames for city and country counts with proportions
    city_proportions_df = pd.DataFrame({
        'City': city_counts.index,
        'Count': city_counts.values,
        'Proportion (%)': city_proportions.values
    })

    country_proportions_df = pd.DataFrame({
        'Country': country_counts.index,
        'Count': country_counts.values,
        'Proportion (%)': country_proportions.values
    })

    print("\nMost popular cities:")
    print(city_proportions_df.head()) 

    print("\nLess popular cities:")
    print(city_proportions_df.tail())  # Print last 5

    print("\nMost popular countries:")
    print(country_proportions_df.head())  # Print first 5

    print("\nLess popular countries:")
    print(country_proportions_df.tail()) 

# Main execution block
if __name__ == "__main__":
    # Prompt user for input file path
    in_file_name = input("Please enter the path of the input CSV file: ")

    # Read the CSV file into a pandas dataframe
    df = pd.read_csv(in_file_name, dtype={'source_date': 'string'})
    df['time'] = pd.to_datetime(df['time'], format='%H:%M:%S', errors='coerce')
    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')

    # Print to output the descriptive analysis for:

    # Numerical columns
    print('-'*40)
    desc_num_cols(df[['max_price_EUR', 'min_price_EUR']])

    # Date/time columnns
    print('-'*40)
    desc_time_date_col(df, 'date', col_type='date')
    print('-'*40)
    desc_time_date_col(df, 'time', col_type='time')

    # Country/city columns
    print('-'*40)
    city_country_info(df)


    # Missing values information
    print('-'*40)
    na_information(df)
    

    # Plots and histograms
    print('-'*40)
    plot_all_together(df, 'time', 'date', 'country')