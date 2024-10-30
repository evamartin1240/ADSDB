import streamlit as st
import os
import sys

sys.path.insert(0, './scripts/data_ingestion')
sys.path.insert(0, './scripts/landing')
sys.path.insert(0, './scripts/formatted')
sys.path.insert(0, './scripts/trusted')
sys.path.insert(0, './scripts/trusted/generic_data_quality')
sys.path.insert(0, './scripts/exploitation')


# Import functions from scripts directory
from spotify_data_ingestion import ingest_spotify_data # step 1.spotify
from ticketmaster_data_ingestion import ingest_ticketmaster_data # step 1.ticketmaster
from raw2temporal import raw2temporal # step 2
from temporal2persistent import temporal2persistent # step 3
from landing2formatted import landing2formatted # step 4
from formatted2trusted import formatted2trusted # step 5
from deduplication import deduplication # step 6.deduplication
from profiling_formatted import spotify_profiling_app
from profiling_formatted import ticketmaster_profiling_app
from profiling_formatted import quick_format_prep
from consistent_formatting import consistent_formatting
from misspellings import misspellings
from profiling_trusted import spotify_profiling_app_trusted
from profiling_trusted import ticketmaster_profiling_app_trusted
from trusted2exploitation import trusted2exploit
from trusted2exploitation import add_tables_to_duckdb
from profiling_exploitation import profiling_explo_app

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


####### Step 2: Raw to Temporal Landing #######

st.markdown("<h3 style='color: #1f77b4;'>2. Raw to Temporal Landing</h3>", unsafe_allow_html=True)
#st.markdown("<hr style='margin: 0; border: 1px solid blue;'>", unsafe_allow_html=True)

# Input fields for the raw and temporal directory paths
rawdir_in = st.text_input("Input data path (raw)", "./data/raw", key="step2a")
tempdir_out = st.text_input("Output data path (temporal)", "./data/landing/temporal", key="step2b")

# Button to run the raw2temporal function
if st.button("Copy Data"):
    if rawdir_in and tempdir_out:
        raw2temporal(rawdir_in, tempdir_out)
        st.success(f"Data has been moved from '{rawdir_in}' to '{tempdir_out}'")
    else:
        st.error("Please provide both paths.")


####### Step 3: Temporal Landing to Persistent Landing #######

st.markdown("<h3 style='color: #1f77b4;'>3. Temporal to Persistent Landing</h3>", unsafe_allow_html=True)

# Input fields for the temporal and persistent directories
tempdir_in = st.text_input("Input data path (temporal):", "./data/landing/temporal", key="step3a")
persistdir_out = st.text_input("Output data path (persistent):", "./data/landing/persistent", key="step3b")

if st.button("Move Data"):
    if tempdir_in and persistdir_out:
        # Call the temporal2persistent function
        temporal2persistent(tempdir_in, persistdir_out)
        st.success(f"Data has been moved from '{tempdir_in}' to '{persistdir_out}'")
    else:
        st.error("Please provide both paths.")

####### Step 4: Persistent Landing to Formatted #######

st.markdown("<h3 style='color: #1f77b4;'>4. Persistent Landing to Formatted</h3>", unsafe_allow_html=True)

# Input fields for the persistent and formatted directories
persdir_in = st.text_input("Input data path (persistent):", "./data/landing/persistent", key="step4a")
formdir_out = st.text_input("Output data path (formatted):", "./data/formatted",key="step4b")

if st.button("Convert Data"):
    if persdir_in and formdir_out:
        # Call the landing2formatted function
        landing2formatted(persdir_in, formdir_out)
        st.success("Data successfully converted to DuckDB format in the formatted zone.")
    else:
        st.error("Please provide both paths.")

####### PROFILING FORMATTED ########

st.markdown("<h4 style='color: #1f77b4;'> PROFILING - Formatted Zone</h4>", unsafe_allow_html=True)
st.markdown("<hr style='margin: 0; border: 1px solid #1f77b4;'>", unsafe_allow_html=True)

# Input fields for the DuckDB file path and the trusted directory
duckdb_file_path = st.text_input("Input DuckDB database (formatted):","./data/formatted/formatted.duckdb" , key="prof1")

if st.button("Profile"):
    quick_format_prep(duckdb_file_path)
    spotify_profiling_app(duckdb_file_path)
    ticketmaster_profiling_app(duckdb_file_path)

####### Step 5: Formatted to Trusted #######

st.markdown("<h3 style='color: #1f77b4;'>5. Formatted to Trusted</h3>", unsafe_allow_html=True)

# Input fields for the DuckDB file path and the trusted directory
duckdb_file_path = st.text_input("Input DuckDB database (formatted):","./data/formatted/formatted.duckdb" , key="step5a")
trusted_dir = st.text_input("Output data path (trusted):","./data/trusted", key="step5b")

if st.button("Homogenize and Save Data to Trusted Zone"):
    if duckdb_file_path and trusted_dir:
        # Call the formatted2trusted function
        formatted2trusted(duckdb_file_path, trusted_dir)
        st.success("Data successfully homogenized and saved to the trusted zone.")
    else:
        st.error("Please provide both paths.")

####### Step 6: Data Quality (trusted zone) #######

st.markdown("<h3 style='color: #1f77b4;'>6. Data Quality (trusted zone)</h3>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Deduplication", "Consistent formatting", "Misspellings"])

# Deduplication Tab
with tab1:    
    # Input field for the DuckDB database file path
    db_file_path = st.text_input("Input DuckDB database (trusted):","./data/trusted/trusted.duckdb" , key="dedup")
    # Button for deduplication
    if st.button("Run Deduplication"):
        if db_file_path:
            try:
                # deduplication function
                output_messages = deduplication(db_file_path)
                st.success("Deduplication process completed successfully.")
                for message in output_messages: # print each message
                    st.write(message)
            except Exception as e:
                st.error(f"An error occurred during deduplication: {e}")
        else:
            st.error("Please provide a valid DuckDB file path.")

# Consistent formatting Tab
with tab2:    
    # Input field for the DuckDB database file path
    db_file_path = st.text_input("Input DuckDB database (trusted):","./data/trusted/trusted.duckdb" , key="cons_format")
    # Button for deduplication
    if st.button("Run formatting"):
        if db_file_path:
            try:
                # consistent formatting function
                consistent_formatting(db_file_path)
                st.success("Consistent formatting process completed successfully.")
            except Exception as e:
                st.error(f"An error occurred during consistent formatting: {e}")
        else:
            st.error("Please provide a valid DuckDB file path.")

# Misspellings Tab
with tab3:    
    # Input field for the DuckDB database file path
    db_file_path = st.text_input("Input DuckDB database (trusted):","./data/trusted/trusted.duckdb" , key="misspel")
    # Button for deduplication
    if st.button("Run misspellings"):
        if db_file_path:
            try:
                # consistent formatting function
                misspellings(db_file_path)
                st.success("Consistent formatting process completed successfully.")
            except Exception as e:
                st.error(f"An error occurred during consistent formatting: {e}")
        else:
            st.error("Please provide a valid DuckDB file path.")

####### PROFILING TRUSTED ########

st.markdown("<h4 style='color: #1f77b4;'> PROFILING - Trusted Zone</h4>", unsafe_allow_html=True)
st.markdown("<hr style='margin: 0; border: 1px solid #1f77b4;'>", unsafe_allow_html=True)

# Input fields for the DuckDB file path and the trusted directory
duckdb_file_path = st.text_input("Input DuckDB database (trusted):","./data/trusted/trusted.duckdb" , key="prof2")

if st.button("Profile trusted"):
    spotify_profiling_app_trusted(duckdb_file_path)
    ticketmaster_profiling_app_trusted(duckdb_file_path)

####### Step 7: Trusted to Exploitation #######

st.markdown("<h3 style='color: #1f77b4;'>7. Trusted to Exploitation</h3>", unsafe_allow_html=True)

# Input fields for the DuckDB file path and the trusted directory
duckdb_file_path = st.text_input("Input DuckDB database (trusted):","./data/trusted/trusted.duckdb" , key="step7a")
exploit_dir = st.text_input("Output data path (exploitation):","./data/exploitation", key="step7b")

if st.button("Pass from Trusted Exploitation Zone"):
    if duckdb_file_path and trusted_dir:
        # Call the formatted2trusted function
        trusted2exploit(duckdb_file_path, exploit_dir)
        exploit_duckdb_path = os.path.join(exploit_dir, 'exploitation.duckdb')
        add_tables_to_duckdb(exploit_duckdb_path)
        st.success("Exploitation zone database successfully created.")
    else:
        st.error("Please provide both paths.")

####### PROFILING EXPLOITATION ########

st.markdown("<h4 style='color: #1f77b4;'> PROFILING - Exploitation Zone</h4>", unsafe_allow_html=True)
st.markdown("<hr style='margin: 0; border: 1px solid #1f77b4;'>", unsafe_allow_html=True)

# Input fields for the DuckDB file path and the trusted directory
duckdb_file_path = st.text_input("Input DuckDB database (trusted):","./data/exploitation/exploitation.duckdb" , key="prof3")

if st.button("Profile exploitation database"):
    profiling_explo_app(duckdb_file_path)