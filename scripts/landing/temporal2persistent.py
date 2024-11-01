from datetime import datetime
import shutil
import os

"""# Temporal Landing to Persisten Landing
Take the data files for Spotify and Ticketmaster in the temporal landing and moves them to the persistent landing applying the necessary transformations.
"""

def temporal2persistent(tempdir_in, persistdir_out):
    """
    Move files from the temporal landing to the persistent landing.
    The function renames each file using its source and ingestion date ("source_DD/MM/YYYY.json").
    """

    for filename_in in os.listdir(tempdir_in):  # Iterate over files in the temporary directory
        # Define the source and output subdirectory based on file name
        if 'spotify' in filename_in.lower():
            subdir = 'spotify_source'
        elif 'ticketmaster' in filename_in.lower():
            subdir = 'ticketmaster_source'
        else:
            print(f"Filename_in format unrecognized: {filename_in}")
            continue

        # Fetch the creation time of the file and format it as DDMMYYYY
        source_path = os.path.join(tempdir_in, filename_in)
        creation_time = os.path.getctime(source_path)
        creation_date = datetime.fromtimestamp(creation_time).strftime('%d%m%Y')
        
        # Format the output file name with the creation date
        filename_out = f"{subdir.split('_')[0]}_{creation_date}.json"
        
        # Create the target subdirectory if it doesn't exist
        target_dir = os.path.join(persistdir_out, subdir)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        # Construct the full output path and move the file
        output_path = os.path.join(target_dir, filename_out)
        shutil.move(source_path, output_path)  # Move the file to the persistent directory
        print(f"Moved {source_path} to {output_path}")

if __name__ == "__main__":
    tempdir_in = input("Temporal landing directory path (input): ")
    persistdir_out = input("Persistent landing directory path (output): ")
    temporal2persistent(tempdir_in, persistdir_out)