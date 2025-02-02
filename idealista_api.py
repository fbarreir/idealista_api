import base64
import json
import os
from datetime import datetime

import pandas as pd
import requests

CSV_FILE = "idealista_price_trends.csv"
KEY_FILE = "/Users/fbarreir/idealista_api_key.json"

# IDs extracted using: https://igolaizola.github.io/idealista-scraper/
LOCATION_ID_MAP = {
    "Tres Cantos": "0-EU-ES-28-01-001-903",
    "Colmenar Viejo": "0-EU-ES-28-01-009-045",
}


def load_api_key():
    # Read API key and secret. Assumes idealista_api_key.json is in the home directory
    # Format for the file will be {"API_KEY": "your_key", "API_SECRET": "your_secret"}
    try:
        with open(KEY_FILE) as f:
            keys = json.load(f)
            return keys["API_KEY"], keys["API_SECRET"]
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        print("<load_api_key>: API key file not found or malformed.")
        return None, None  # Handle missing or malformed file


def get_token(api_key, api_secret):
    # Get temporary OAuth token through API key and secret

    # Encode credentials in Base64
    auth_string = f"{api_key}:{api_secret}"
    auth_b64 = base64.b64encode(auth_string.encode()).decode()

    # Request OAuth token
    url = "https://api.idealista.com/oauth/token"
    headers = {
        "Authorization": f"Basic {auth_b64}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"grant_type": "client_credentials", "scope": "read"}

    response = requests.post(url, headers=headers, data=data)
    try:
        access_token = response.json().get("access_token")
    except json.JSONDecodeError:
        print(
            f"<get_token>: Error decoding JSON response. (HTTP status code: {response.status_code})"
        )
        return None

    return access_token


def get_listings(access_token, location_id="0-EU-ES-28-01-001-903"):
    # Get property listings using the OAuth token
    url = "https://api.idealista.com/3.5/es/search"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }

    page = 1
    all_listings = []

    while True:
        params = {
            "country": "es",
            "operation": "sale",
            "propertyType": "homes",
            "locationId": location_id,
            "maxItems": 50,
            "numPage": page,
        }

        response = requests.post(url, headers=headers, params=params)
        try:
            data = response.json()
        except json.JSONDecodeError:
            print(
                f"<get_listings>: Error decoding JSON response. (HTTP status code: {response.status_code})"
            )
            return all_listings

        listings = data.get("elementList", [])
        total_pages = data.get("totalPages", 1)

        if not listings:
            break

        all_listings.extend(listings)
        print(
            f"Fetched page {page} of {total_pages}, total listings so far: {len(all_listings)}"
        )

        if page >= total_pages:
            break

        page += 1

    return all_listings


def calculate_price_per_sqm(listings):
    # Iterate the listings and calculate the average price per square meter for flats
    total_price_per_sqm = 0
    num_homes = 0

    for listing in listings:
        if "price" in listing and "size" in listing:
            price = listing["price"]
            size = listing["size"]

            if size > 0:  # Avoid division by zero
                total_price_per_sqm += price / size
                num_homes += 1

    avg_price_per_sqm = total_price_per_sqm / num_homes if num_homes > 0 else 0

    return avg_price_per_sqm, num_homes


def save_to_csv(location, timestamp, avg_price_per_sqm, num_flats):

    df = pd.DataFrame(
        [[location, timestamp, avg_price_per_sqm, num_flats]],
        columns=["location", "timestamp", "avg_price_per_sqm", "num_flats"],
    )

    # Append mode if file exists, else create a new one
    if os.path.exists(CSV_FILE):
        df.to_csv(CSV_FILE, mode="a", header=False, index=False)
    else:
        df.to_csv(CSV_FILE, mode="w", header=True, index=False)


if __name__ == "__main__":
    api_key, api_secret = load_api_key()
    access_token = get_token(api_key, api_secret)
    if not access_token:
        exit()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for location, location_id in LOCATION_ID_MAP.items():
        listings = get_listings(access_token, location_id)
        avg_price_per_sqm, num_homes = calculate_price_per_sqm(listings)

        print(f"Total number of flats in {location}: {num_homes}")
        print(
            f"Average price per square meter in {location}: {avg_price_per_sqm:.2f} €/m²"
        )

        save_to_csv(location, timestamp, avg_price_per_sqm, num_homes)
