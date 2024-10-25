import os
import shutil

def raw2temporal(rawdir_in, tempdir_out):
    """
    Function to copy raw data files from the rawdir_in to the temporal directory (tempdir_out).
    This prepares the data for further processing.
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

    # rawdir_in = '/Users/evamartin/Desktop/MDS/curs1/ADSDB/data/raw'
    # tempdir_out = '/Users/evamartin/Desktop/MDS/curs1/ADSDB/data/landing/temporal'

