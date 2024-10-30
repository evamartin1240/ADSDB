# ADSDB <a href="https://github.com/evamartin1240/ADSDB"><img src="others/spotify.png" align="right" height="25" /></a> <a href="https://github.com/evamartin1240/ADSDB"><img src="others/ticketmaster.png" align="right" height="20" /></a>

## Data Management Backbone

This repository contains the data management backbone for our project. 

We've implemented two methods for running the operations environment:

1. Web Interface: Access the pipeline through the web interface.
2. Command Line (CLI): Run all operations directly from the terminal.

### 1. Web Interface



### 2. Command Line (CLI)

If you prefer to run the program from the command line, do as follows. This way is recommended for debugging as you will get information printed on the command line. 

#### Set up your Python environment

First, you will need a working Python 3 installation. Then, clone this repository to access the code.

Setting up your Python environment depends on your operating system.

##### MacOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

##### Windows

```batch
python3 -m venv venv
.\venv\Scripts\activate
```

Now, recursively install all the dependencies for this program.

```bash
pip install -r requirements.txt
```

##### MacOS/Linux

Once all the environment is set, you are ready to execute all the scripts in the pipeline, requesting the user for paths to the data. Note that this will not produce profilings. To visualize profiling steps, use the app.

##### MacOS/Linux

```bash
./run.sh
```

##### Windows

```batch
run.bat
```

> **Note:** We are aware the data ingestion step is cumbersome due to rate limits on the Spotify and Ticketmaster APIs. For this reason, we have provided two datasets collected on 10/10/2024 and two more on 19/10/2024. If you wish to avoid fetching new information from the API and use these datasets instead: On the GUI app, simply skip the data ingestion step and continue with the rest. On the CLI, execute the `run.sh` or `run.bat` command with --skip-ingestion. (Example: `./run.sh --skip-ingestion`)


<img src="others/salida.gif">
