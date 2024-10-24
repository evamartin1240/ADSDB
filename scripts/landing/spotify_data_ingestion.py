import requests
import json
import base64
import time
import os

"""# Spotify Data Ingestion
Fetch data from the Spotify API saves the resulting .json files to the temporal landing zone.
"""

"""## Spotify Credentials
"""

def get_headers_spotify(client_id, client_secret):
    auth_str = f"{client_id}:{client_secret}"
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()
    # Request access token
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {b64_auth_str}"
    }
    data = {
        "grant_type": "client_credentials"
    }
    response = requests.post(url, headers=headers, data=data)
    access_token = response.json()['access_token']
    # Headers with access token
    headers = { 
        "Authorization": f"Bearer {access_token}"
    }
    return headers

"""## Fetch data from Spotify and save to JSON
Something.
"""

def ingest_spotify_data(temporal_dir, out_filename, artist_names, client_id, client_secret):
    """ Function that retrieves data from Spotify API.
    """
    headers = get_headers_spotify(client_id, client_secret)
    
    artist_info = []
    for artist_name in artist_names:
        search_url = f"https://api.spotify.com/v1/search?q={artist_name}&type=artist"
        response = requests.get(search_url, headers=headers)
        time.sleep(0.5)  # Avoid exceeding the API request limit
        
        # Check if the request was successful
        if response.status_code == 200:
            result = response.json()
            
            if 'artists' in result and len(result['artists']['items']) > 0:
                artist_data = result['artists']['items'][0]  # Get the first result if more than one result is found
                artist_info.append({
                    'artist': artist_data['name'],
                    'genres': artist_data['genres'],
                    'followers': artist_data['followers']['total'],
                    'popularity': artist_data['popularity']
                })
            else:
                print(f"{time.time()}: Spotify response unsuccessful for artist \"{artist_name}\"")

    # Save the results to a JSON file
    if not os.path.exists(temporal_dir): # If the path to the temporal directory doesn't exist, create it
        os.makedirs(temporal_dir)
    output_path = os.path.join(temporal_dir, out_filename)
    with open(output_path, 'w') as json_file:
        json.dump(artist_info, json_file, indent=4)

    print(f"Spotify data has been saved to {output_path}")

if __name__ == "__main__":
    artist_names_file = input("Artist names to retrieve (.txt file): ")
    with open(artist_names_file, 'r') as file: 
        artist_names = [line.strip() for line in file]
    artist_names = ['Black Pumas', "Haze"] 

    temporal_dir = input("Path to temporal landing directory: ")
    
    out_filename = input("Output .json file name (specify the file version): ").strip()

    client_id = input("Spotify client id: ") 
    client_secret = input("Spotify client secret: ")
    
    ingest_spotify_data(temporal_dir, out_filename, artist_names, client_id, client_secret)

    # artist_names_file = '/Users/evamartin/Desktop/MDS/curs1/ADSDB/data/artist_names_subset.txt'
    # temporal_dir = '/Users/evamartin/Desktop/MDS/curs1/ADSDB/data/landing/temporal'
    # out_filename = 'spotify_dataV1.json'
    # Keys for the Spotify API: client_id = '62f9499b009c49d8b6363890028ce155', client_secret = '8b1ec143c4d94ea6aa3920b3b8bf2ee6'
    # ffmpeg -i name.mov -vf "fps=10,scale=600:-1:flags=lanczos" /Users/evamartin/Desktop/MDS/curs1/ADSDB/others/salida.gif