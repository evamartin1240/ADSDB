import streamlit as st
import os
import sys

sys.path.insert(0, './scripts/data_ingestion')
sys.path.insert(0, './scripts/landing')
sys.path.insert(0, './scripts/formatted')
sys.path.insert(0, './scripts/trusted')
sys.path.insert(0, './scripts/trusted/generic_data_quality')

# Import functions from scripts directory
from spotify_data_ingestion import ingest_spotify_data # step 1.spotify
from ticketmaster_data_ingestion import ingest_ticketmaster_data # step 1.ticketmaster
from raw2temporal import raw2temporal # step 2
from temporal2persistent import temporal2persistent # step 3
from landing2formatted import landing2formatted # step 4
from formatted2trusted import formatted2trusted # step 5
from deduplication import deduplication # step 6.deduplication

# APP

st.logo('./others/logo_app.png', size="large")

st.markdown("<h1 style='color: #155a8a;'>Data Management Backbone</h1>", unsafe_allow_html=True)

####### Step 1: Data Ingestion Section #######

st.markdown("<h3 style='color: #1f77b4;'>1. Data Ingestion</h3>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Spotify", "TicketMaster"])

with tab1:
    client_id = st.text_input("Spotify Client ID", type="password")
    client_secret = st.text_input("Spotify Client secret", type="password", key="tab1a")
    artist_file = st.file_uploader("Upload artist names file (.txt)", type="txt", key="tab1b")
    raw_data_path = st.text_input("Path to store the ingested raw data files", "./data/raw", key="tab1c")
    out_filename = st.text_input("Output (.json) file name", "spotify_data.json", key="tab1d")
    
    if st.button("Fetch Spotify Data"):
        if client_id and client_secret and artist_file:
            artist_names = [line.strip() for line in artist_file.read().decode("utf-8").splitlines()]
            ingest_spotify_data(client_id, client_secret, artist_names, raw_data_path, out_filename)
            st.success(f"Spotify data has been saved to {os.path.join(raw_data_path, out_filename)}")
        else:
            st.error("Please enter all required fields.")

with tab2:
    api_key = st.text_input("TicketMaster API Key", type="password")
    artist_file_tm = st.file_uploader("Upload artist names file (.txt)", type="txt", key="tab2a")
    raw_data_path_tm = st.text_input("Path to store the ingested raw data files", "./data/raw", key="tab2b")
    out_filename_tm = st.text_input("Output .json file name", "ticketmaster_data.json", key="tab23")
    
    if st.button("Fetch TicketMaster Data"):
        if api_key and artist_file_tm:
            artist_names = [line.strip() for line in artist_file_tm.read().decode("utf-8").splitlines()]
            ingest_ticketmaster_data(api_key, artist_names, raw_data_path_tm, out_filename_tm)
            st.success(f"Ticketmaster data has been saved to {os.path.join(raw_data_path_tm, out_filename_tm)}")
        else:
            st.error("Please enter all required fields.")


####### Step 2: Raw to Temporal Landing Section #######

st.markdown("<h3 style='color: #1f77b4;'>2. Raw to Temporal Landing</h3>", unsafe_allow_html=True)
#st.markdown("<hr style='margin: 0; border: 1px solid blue;'>", unsafe_allow_html=True)

# Input fields for the raw and temporal directory paths
rawdir_in = st.text_input("Raw Directory Path (input)", "./raw_data")
tempdir_out = st.text_input("Temporal Landing Directory Path (output)", "./temporal_data")

# Button to trigger the raw2temporal function
if st.button("Copy raw data to temporal landing directory"):
    if rawdir_in and tempdir_out:
        raw2temporal(rawdir_in, tempdir_out)
        st.success(f"Data has been moved from {rawdir_in} to {tempdir_out}")
    else:
        st.error("Please provide both input and output directory paths.")


####### Step 3: Temporal to Persistent Landing #######

st.markdown("<h3 style='color: #1f77b4;'>3. Temporal to Persistent Landing</h3>", unsafe_allow_html=True)

# Input fields for the temporal and persistent directories
tempdir_in = st.text_input("Enter Temporal Landing Directory Path:", key="step3a")
persistdir_out = st.text_input("Enter Persistent Landing Directory Path:", key="step3b")

if st.button("Move Data"):
    if tempdir_in and persistdir_out:
        # Call the temporal2persistent function
        temporal2persistent(tempdir_in, persistdir_out)
        st.success("Data has been successfully moved from temporal to persistent landing.")
    else:
        st.error("Please provide both paths.")

####### Step 4: Landing to Formatted Zone #######

st.markdown("<h3 style='color: #1f77b4;'>4. Landing to Formatted Zone</h3>", unsafe_allow_html=True)

# Input fields for the persistent and formatted directories
persdir_in = st.text_input("Enter Persistent Landing Directory Path:", key="step4a")
formdir_out = st.text_input("Enter Formatted Landing Directory Path:", key="step4b")

if st.button("Convert Data"):
    if persdir_in and formdir_out:
        # Call the landing2formatted function
        landing2formatted(persdir_in, formdir_out)
        st.success("Data successfully converted to DuckDB format in the formatted landing zone.")
    else:
        st.error("Please provide both paths.")

####### Step 5: Formatted to Trusted Zone #######

st.markdown("<h3 style='color: #1f77b4;'>5. Formatted to Trusted Zone</h3>", unsafe_allow_html=True)

# Input fields for the DuckDB file path and the trusted directory
duckdb_file_path = st.text_input("Enter Formatted DuckDB File Path:", key="formatted_duckdb_input")
trusted_dir = st.text_input("Enter Trusted Directory Path:", key="trusted_dir_output")

if st.button("Homogenize and Save Data to Trusted Zone"):
    if duckdb_file_path and trusted_dir:
        # Call the formatted2trusted function
        formatted2trusted(duckdb_file_path, trusted_dir)
        st.success("Data successfully homogenized and saved to the trusted landing zone.")
    else:
        st.error("Please provide both paths.")

####### Step 6: Generic Data Quality #######

st.markdown("<h3 style='color: #1f77b4;'>6. Generic Data Quality</h3>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Deduplication", "Others"])

# Deduplication Tab
with tab1:
    # st.write("##### Deduplication")
    
    # Input field for the DuckDB database file path
    db_file_path = st.text_input("Enter the DuckDB file path for deduplication:", key="db_file_path_dedup")
    
    # Button to trigger deduplication
    if st.button("Run Deduplication"):
        if db_file_path:
            try:
                # Call the deduplication function
                deduplication(db_file_path)
                st.success("Deduplication process completed successfully.")
            except Exception as e:
                st.error(f"An error occurred during deduplication: {e}")
        else:
            st.error("Please provide a valid DuckDB file path.")
