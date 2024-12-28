import streamlit as st
import os
import sys

sys.path.insert(0, './scripts/data_ingestion')
sys.path.insert(0, './scripts/landing')
sys.path.insert(0, './scripts/formatted')
sys.path.insert(0, './scripts/trusted')
sys.path.insert(0, './scripts/trusted/generic_data_quality')
sys.path.insert(0, './scripts/exploitation')
sys.path.insert(0, './scripts/analytical_backbone/sandbox')
sys.path.insert(0, './scripts/analytical_backbone/feature_engineering')
sys.path.insert(0, './scripts/analytical_backbone/data_augmentation')
sys.path.insert(0, './scripts/analytical_backbone/data_split')
sys.path.insert(0, './scripts/analytical_backbone/modelling')
sys.path.insert(0, './scripts/analytical_backbone/data_augmentation')


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
from sandbox import exploitation2sandbox
from feature_generation import feature_generation
from data_preparation import data_preparation
from data_split import data_split
from model_generation import model_generation_wrapper
from external_validation import external_validation_wrapper
from data_augmentation import data_augmentation



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

######### PART 2: ANALYTICAL BACKBONE #########

st.markdown("<h1 style='color: #155a8a;'>Analytical Backbone</h1>", unsafe_allow_html=True)

####### Step 8: Exploitation to Sandbox #######

st.markdown("<h3 style='color: #1f77b4;'>8. Exploitation to Sandbox</h3>", unsafe_allow_html=True)

# Input fields for the DuckDB file path and the trusted directory
duckdb_file_path = st.text_input("Input DuckDB database (exploitation):","./data/exploitation/exploitation.duckdb" , key="step8a")
sandbox_dir = st.text_input("Output data path (sandbox):","./data/analytical_backbone/sandbox", key="step8b")

if st.button("Pass from Exploitation Zone to the Sandbox"):
    if duckdb_file_path and sandbox_dir:
        # Call the  function exploitation2sandbox(
        exploitation2sandbox(duckdb_file_path, sandbox_dir)
        st.success("Sandbox database successfully created.")
    else:
        st.error("Please provide both paths.")


####### Step 9: Feature Engineering #######

st.markdown("<h3 style='color: #1f77b4;'>9. Feature Engineering</h3>", unsafe_allow_html=True)

engineering_dir = st.text_input("Output data path (feature engineering):","./data/analytical_backbone/feature_engineering" , key="step9outdir")

tab1, tab2 = st.tabs(["Data Preparation", "Feature Geneartion"])

with tab1:
    # Input field for the DuckDB database file path
    db_file_path = st.text_input("Input DuckDB database (sandbox):","./data/analytical_backbone/sandbox/sandbox.duckdb" , key="step9dataprepa")
    # Button for data preparation
    if st.button("Run Data Preparation"):
        if db_file_path:
            try:
                # consistent formatting function
                output_messages = data_preparation(db_file_path, engineering_dir)
                st.success("Data preparation process completed successfully.")
                for message in output_messages:
                    st.write(message)
            except Exception as e:
                st.error(f"An error occurred during data preparation: {e}")
        else:
            st.error("Please provide a valid DuckDB file path.")


with tab2:
    # Input field for the DuckDB database file path
    db_file_path = st.text_input("Input DuckDB database (data preparation):","./data/analytical_backbone/feature_engineering/data_preparation.duckdb" , key="step9featgena")

    if st.button("Run Feature Generation"):
        if db_file_path:
            try:
                # feature generation function
                output_messages = feature_generation(db_file_path, engineering_dir)
                st.success("Feature generation completed successfully.")
                for message in output_messages: # print each message
                    st.write(message)
            except Exception as e:
                st.error(f"An error occurred during feature generation: {e}")
        else:
            st.error("Please provide a valid DuckDB file path.")

####### Step 10: Data Split #######

st.markdown("<h3 style='color: #1f77b4;'>10. Data Split</h3>", unsafe_allow_html=True)

# Input fields for the DuckDB file path and the data split directory
duckdb_file_path = st.text_input("Input DuckDB database (feature generation):","./data/analytical_backbone/feature_engineering/feature_generation.duckdb" , key="step10a")
split_dir = st.text_input("Output data path (data split):","./data/analytical_backbone/data_split", key="step10b")
keyword = st.text_input("Enter a keyword to identify the data uniquely:", "default",key="step10c")

if st.button("Split the data"):
    if duckdb_file_path and split_dir:
        # Call the  function data_split()
        data_split(duckdb_file_path, split_dir, keyword)
        st.success("Data split database successfully created.")
    else:
        st.error("Please provide both paths.")

####### Step 11: Model Generation #######

st.markdown("<h3 style='color: #1f77b4;'>11. Model Generation</h3>", unsafe_allow_html=True)

# Input fields for the DuckDB file path and the model directory
duckdb_file_path = st.text_input("Input DuckDB database (split data):",f"./data/analytical_backbone/data_split/{keyword}_split.duckdb" , key="step11a")
model_dir = st.text_input("Output model directory:","./models", key="step11b")
params_path = st.text_input("Input model parameters:","./params.yaml", key="step11c")
keyword = st.text_input("Enter a keyword to identify the data uniquely:", keyword, key="step11d")

if st.button("Create the models"):
    if duckdb_file_path and model_dir and params_path:
        # Call the  function model_generation_wrapper()
        model_generation_wrapper(duckdb_file_path, model_dir, params_path, keyword)
        st.success("Models successfully created.")
    else:
        st.error("Please provide the three paths.")

####### Step 12: External Validation #######

st.markdown("<h3 style='color: #1f77b4;'>12. External Validation</h3>", unsafe_allow_html=True)

# Input fields for the DuckDB file path and the model directory
duckdb_file_path = st.text_input("Input DuckDB database (split data):",f"./data/analytical_backbone/data_split/{keyword}_split.duckdb" , key="step12a")
model_dir = st.text_input("Output model directory:","./models", key="step12b")
keyword = st.text_input("Enter a keyword to identify the data uniquely:", keyword, key="step12c")
metrics_dir = st.text_input("Directory to store the external validation metrics:", "./models/extval_metrics/", key="step12d")
figure_dir = st.text_input("Directory to store the external validation figures :", "./models/extval_figures/", key="step1de")

if st.button("Perform External Validation"):
    if duckdb_file_path and model_dir and metrics_dir and figure_dir:
        # Call the function external_validation_wrapper()
        out = external_validation_wrapper(
        db_file=duckdb_file_path,
        metrics_dir=metrics_dir,
        model_dir=model_dir,
        figure_dir=figure_dir,
        keyword=keyword
        )

        st.success("External validation performed.")
    else:
        st.error("Please provide the four paths.")

######### ADVANCED TOPIC #########

st.markdown("<h2 style='color: #155a8a;'>Advanced Topic: Data Augmentation</h1>", unsafe_allow_html=True)

###### Step 13: Data Augmentation ########

st.markdown("<h3 style='color: #1f77b4;'>13. Data Augmentation with SMOTE</h3>", unsafe_allow_html=True)

# Input fields for the DuckDB file path and the trusted directory
duckdb_file_path = st.text_input("Input DuckDB database (feature generation):","./data/analytical_backbone/feature_engineering/feature_generation.duckdb" , key="step13a")
augmentation_dir = st.text_input("Output data path (data augmentation):","./data/analytical_backbone/data_augmentation", key="step13b")

if st.button("Perform Data Augmentation with SMOTE"):
    if duckdb_file_path and augmentation_dir:
        # Call the  function data_augmentation(
        data_augmentation(duckdb_file_path, augmentation_dir)
        st.success("Data augmentation database successfully created.")
    else:
        st.error("Please provide both paths.")

####### Step 14: Data Split (augmented) #######

st.markdown("<h3 style='color: #1f77b4;'>14. Data Split (Augmented)</h3>", unsafe_allow_html=True)

# Input fields for the DuckDB file path and the data split directory
duckdb_file_path = st.text_input("Input DuckDB database (data augmentation):","./data/analytical_backbone/data_augmentation/augmentation.duckdb" , key="step14a")
split_dir = st.text_input("Output data path (data split):","./data/analytical_backbone/data_split", key="step14b")
keyword_aug = st.text_input("Enter a keyword to identify the data uniquely:", "augmented",key="step14c")

if st.button("Split the data (augmented)"):
    if duckdb_file_path and split_dir:
        # Call the  function data_split()
        data_split(duckdb_file_path, split_dir, keyword_aug)
        st.success("Data split database successfully created.")
    else:
        st.error("Please provide both paths.")

####### Step 15: Model Generation (augmented) #######

st.markdown("<h3 style='color: #1f77b4;'>15. Model Generation (augmented)</h3>", unsafe_allow_html=True)

# Input fields for the DuckDB file path and the model directory
duckdb_file_path = st.text_input("Input DuckDB database (split data):",f"./data/analytical_backbone/data_split/{keyword_aug}_split.duckdb" , key="step15a")
model_dir = st.text_input("Output model directory:","./models", key="step15b")
params_path = st.text_input("Input model parameters:","./params.yaml", key="step15c")
keyword_aug = st.text_input("Enter a keyword to identify the data uniquely:", keyword_aug, key="step15d")

if st.button("Create the models (augmented)"):
    if duckdb_file_path and model_dir and params_path:
        # Call the  function model_generation_wrapper()
        model_generation_wrapper(duckdb_file_path, model_dir, params_path, keyword_aug)
        st.success("Models successfully created.")
    else:
        st.error("Please provide the three paths.")

####### Step 16: External Validation (augmented) #######

st.markdown("<h3 style='color: #1f77b4;'>16. External Validation (Augmented)</h3>", unsafe_allow_html=True)

# Input fields for the DuckDB file path and the model directory
duckdb_file_path = st.text_input("Input DuckDB database (split data):",f"./data/analytical_backbone/data_split/{keyword_aug}_split.duckdb" , key="step16a")
model_dir = st.text_input("Output model directory:","./models", key="step16b")
keyword_aug = st.text_input("Enter a keyword to identify the data uniquely:", keyword_aug, key="step16c")
metrics_dir = st.text_input("Directory to store the external validation metrics:", "./models/extval_metrics/", key="step16d")
figure_dir = st.text_input("Directory to store the external validation figures :", "./models/extval_figures/", key="step16e")

if st.button("Perform External Validation (augmented)"):
    if duckdb_file_path and model_dir and metrics_dir and figure_dir:
        # Call the function external_validation_wrapper()
        out = external_validation_wrapper(
        db_file=duckdb_file_path,
        metrics_dir=metrics_dir,
        model_dir=model_dir,
        figure_dir=figure_dir,
        keyword=keyword_aug
        )

        st.success("External validation performed.")
    else:
        st.error("Please provide the four paths.")
