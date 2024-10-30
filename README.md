# ADSDB <a href="https://github.com/evamartin1240/ADSDB"><img src="others/spotify.png" align="right" height="25" /></a> <a href="https://github.com/evamartin1240/ADSDB"><img src="others/ticketmaster.png" align="right" height="20" /></a>

## How to run this program

### Set up your Python environment

First, you will need a working Python 3 installation. Then, clone this repository to access the code.

Setting up your Python environment depends on your operating system.

#### MacOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

#### Windows

```batch
python3 -m venv venv
.\venv\Scripts\activate
```

Now, recursively install all the dependencies for this program.

```bash
pip install -r requirements.txt
```

### Run program

There are two ways to run this program.

#### GUI

Simply run `streamlit run app.py`. This will open the GUI app on your browser.

#### CLI

If you prefer to run the program from the command line, do as follows. This way is recommended for debugging as you will get information printed on the command line.

##### MacOS/Linux

```bash
./run.sh
```

##### Windows

```batch
run.bat
```

## Step 1: Data Ingestion

When running the data ingestion scripts for both TicketMaster and Spotify sources,
you will be prompted for specific input details. You will need to provide the
following:

1. The path to the input `.txt` file containing artist names
2. The path to the temporal directory where the output `.json` file will be stored
3. The name of the output `.json` file including a version number
4. Your TicketMaster/Spotify API key.

Once all inputs are provided, the script will save the data and confirm the
location of the saved JSON file.

**TicketMaster:**

```bash
$ python scripts/data_ingestion/ticketmaster_data_ingestion.py
```

<img src="others/salida.gif">

**Spotify:**

```bash
$ python scripts/data_ingestion/spotify_data_ingestion.py
```

<img src="others/salida.gif">

## Step 2: Temporal Landing Zone

```bash
$ python scripts/landing/raw2temporal.py
```

## Step 3: Persistent Landing Zone

```bash
$ python scripts/landing/temporal2persistent.py
```

<img src="others/salida.gif">

## Step 4: Formatted Zone

```bash
$ python scripts/landing/landing2formatted.py
```
