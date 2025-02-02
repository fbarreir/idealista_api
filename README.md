# Idealista API client
Script to extract the number of listings and average sqm price for selected locations

# Installation/dependencies
Install the required packages with pip:
```bash
pip install -r requirements.txt
```

# API Key
To use the Idealista API, you need to get an API key. You can get one by registering at [Idealista Developers](https://developers.idealista.com/access-request).

Add the key and secret to `idealista_api_key.json` file in the following format:
```json
{
  "API_KEY": "your key",
  "API_SECRET": "your secret"
}
```
# Configuration variables in the script

```python
CSV_FILE = "idealista_price_trends.csv"
KEY_FILE = "/Users/fbarreir/idealista_api_key.json"
LOCATION_ID_MAP = {
    "Tres Cantos": "0-EU-ES-28-01-001-903",
    "Colmenar Viejo": "0-EU-ES-28-01-009-045",
}
```
- `CSV_FILE`: CSV=Comma Separated Values. This variable indicates the file location to store the data. See the Results section for the format.
- `KEY_FILE`: File location with the API key and secret.
- `LOCATION_ID_MAP`: Dictionary with the location names and the corresponding Idealista location ID. The location ID is a string with the format `0-EU-ES-28-01-001-903`. 
The location IDs were extracted from https://igolaizola.github.io/idealista-scraper/ 

# Results

The script will generate or append data to an existing CSV file with the following format. You can 
```csv
location,timestamp,avg_price_per_sqm,num_flats
Tres Cantos,2025-02-02 13:36:56,3229.8198273246353,59
Colmenar Viejo,2025-02-02 13:36:56,2506.4071318190054,162
```

# Execution
Run the script with the following command:
```bash
python idealista_api.py
```
