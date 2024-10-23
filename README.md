# ADSDB <a href="https://github.com/evamartin1240/ADSDB"><img src="others/spotify.png" align="right" height="25" /></a> <a href="https://github.com/evamartin1240/ADSDB"><img src="others/ticketmaster.png" align="right" height="20" /></a>

### Step 1: Data Ingestion

```bash
$ python /landing/ticketmaster_data_ingestion.py
```
```
Please enter the path of the input .txt file with the artist names: /data/artist_names_subset.txt
Please enter the path to the temporal directory where you want to store the JSON file: /landing/temporal
How do you want to name the output JSON file? Remember to specify the file version (e.g., ticketmaster_dataV1.json): ticketmaster_dataV1.json
Please enter your TicketMaster API key: SR6gANwlcVVGnF5DIhkAh38oaRf3a7PR
Ticketmaster data has been saved to /landing/temporal/ticketmaster_dataV1.json
```

Ticketmaster data has been saved to /landing/temporal/ticketmaster_dataV1.json


