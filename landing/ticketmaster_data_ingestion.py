import requests
import json
import time
import os

"""# Ticketmaster data ingestion
Fetch data from the Ticketmaster API and saves the resulting .json files in the temporal landing zone.
"""

"""## Import subset artists list
Something.
"""

artist_names_file = '/Users/evamartin/Desktop/MDS/curs1/ADSDB/artist_names_subset.txt'
with open(artist_names_file, 'r') as file:
    artist_names = [line.strip() for line in file]
artist_names = ['Black Pumas', "Haze"]

"""## TicketMaster Credentials
Something.
"""

api_key = 'SR6gANwlcVVGnF5DIhkAh38oaRf3a7PR'

"""## Fetch data from Ticketmaster and save to JSON in the temporal landing directory
Something.
"""

def extract_event_info(artist, event):
    """Function that gets an artist event and returns its information (date, location, price, etc.)
    """

    venue = event['_embedded']['venues'][0] if '_embedded' in event and 'venues' in event['_embedded'] else {}

    # Obtain price information
    price_range = event.get('priceRanges', [])
    if price_range:
        min_price = price_range[0].get('min', 'N/A')
        max_price = price_range[0].get('max', 'N/A')
        currency = price_range[0].get('currency', 'N/A')
        price_info = f"{min_price}-{max_price} {currency}"
    else:
        price_info = 'N/A'
    
    # Add to the list all the desired event information
    event_info = {
        'artist': artist,
        'name': event.get('name', 'N/A'),
        'date': event['dates']['start'].get('localDate', 'N/A') if 'dates' in event else 'N/A',
        'time': event['dates']['start'].get('localTime', 'N/A') if 'dates' in event else 'N/A',
        'venue': venue.get('name', 'N/A'),
        'location': f"{venue.get('city', {}).get('name', 'N/A')}, {venue.get('country', {}).get('name', 'N/A')}",
        'price_range': price_info,
    }

    return event_info

def ingest_ticketmaster_data(temporal_dir, artist_names, api_key):
    """ Function that retrieves data from TicketMaster API.
    """

    out_filename = input("How do you want to name the output JSON file? Remember to specify the file version (e.g., ticketmaster_dataV1.json): ").strip()

    # List to store the events found for the given artists
    all_artist_events = []

    # For each of the artists in the artis_names list, store its event information in the all_artist_events list
    for artist_name in artist_names:
        url = f"https://app.ticketmaster.com/discovery/v2/events.json?keyword={artist_name}&apikey={api_key}"
        response = requests.get(url) # Request response from the TicketMaster API
        time.sleep(0.5) # Avoid exceeding the API request limit

        # Check if the request was successful
        if response.status_code == 200:
            print(f"{time.time()}: Fetched Ticketmaster data for artist \"{artist_name}\"")
            artist_events = response.json()
            
            # Extraer eventos si existen
            if '_embedded' in artist_events and 'events' in artist_events['_embedded']:
                for event in artist_events['_embedded']['events']:
                    event_data = extract_event_info(artist_name, event)
                    all_artist_events.append(event_data)
        else:
            print(f"{time.time()}: Ticketmaster response unsuccessful for artist \"{artist_name}\"")
          
    # Save the results to a JSON file
    if not os.path.exists(temporal_dir): # If the temporal_directory path doesn't exist, create it
        os.makedirs(temporal_dir)
    output_path = os.path.join(temporal_dir, out_filename)
    with open(output_path, 'w') as json_file:
        json.dump(all_artist_events, json_file, indent=4)

    print(f"Ticketmaster data has been saved to {output_path}")

if __name__ == "__main__":
    ingest_ticketmaster_data("/Users/evamartin/Desktop/MDS/curs1/ADSDB/landing/temporal", artist_names, api_key)