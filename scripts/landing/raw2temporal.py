import os
import shutil

"""# Raw to Temporal Landing
Take the data files for Spotify and Ticketmaster in the raw directory and copies them to the temporal landing directory.
"""

def raw2temporal(rawdir_in, tempdir_out):
    """
    Copy raw data files from the directory where the raw data is stored (rawdir_in)
    to the temporal directory (tempdir_out).
    """
    
    # Ensure the temporal directory exists
    if not os.path.exists(tempdir_out):
        os.makedirs(tempdir_out)

    # Copy each file from the raw_data_path to the tempdir_out directory
    for filename in os.listdir(rawdir_in):
        source_path = os.path.join(rawdir_in, filename)
        dest_path = os.path.join(tempdir_out, filename)
        
        shutil.copy2(source_path, dest_path)  # Copy with metadata
        print(f"Copied {source_path} to {dest_path}")
       
if __name__ == "__main__":
    rawdir_in = input("Raw directory path (input): ")
    tempdir_out = input("Temporal landing directory path (output): ")
    raw2temporal(rawdir_in, tempdir_out)