from datetime import datetime
import time
import shutil
import os
import psutil

"""# Temporal landing to Persisten landing
Take the data files for Spotify and Ticketmaster in the temporal landing and moves them to the persistent landing applying the necessary transformations.
"""

def temporal2persistent(tempdir_in, persistdir_out, version):
    """ Function to move the files from the temporal landing to the persistent landing with the correponding transformations.
    """

    current_date = datetime.today().strftime('%Y%m%d') # Get the current date

    for filename_in in os.listdir(tempdir_in): # Iterate over files in the temporary directory
        if version in filename_in: # Check if the specified version is in the filename
            # Determine the source and corresponding output subdirectory
            if 'spotify' in filename_in.lower():
                subdir = 'spotify_source'
                filename_out = f'spotify_{current_date}.json'
            elif 'ticketmaster' in filename_in.lower():
                subdir = 'ticketmaster_source'
                filename_out = f'ticketmaster_{current_date}.json'
            else:
                print(f"{time.time()}: filename_in format unrecognized: {filename_in}")
                continue  

            # Create the target subdirectory if it doesn't exist
            target_dir = os.path.join(persistdir_out, subdir)
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)

            output_path = os.path.join(target_dir, filename_out) # Construct the full output file path
            shutil.move(os.path.join(tempdir_in, filename_in), output_path) # Move the file from the temp directory to the persistent subdirectory
            print(f"Moved {tempdir_in}/{filename_in} to {output_path}")

if __name__ == "__main__":
    tempdir_in = '/Users/evamartin/Desktop/MDS/curs1/ADSDB/landing/temporal'
    persistdir_out = '/Users/evamartin/Desktop/MDS/curs1/ADSDB/landing/persistent'
    temporal2persistent(tempdir_in, persistdir_out, 'V1')

