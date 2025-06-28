import json
import os
import re

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from backend.url import generate_flight_url


def fetch_flight_data(
    api_url: str,
    api_key: str,
    flight_url: str,
    zone: str,
) -> requests.Response:
    """
    Fetches flight data from the specified API URL using BrightData.

    Parameters:
    - api_url (str): SERP API URL of BrightData.
    - api_key (str): API key generated in your BrightData account.
    - flight_url (str): URL containing flight search parameters.
    - zone (str): Name of your BrightData API zone configuration project.

    Returns:
    - requests.Response: Response object containing HTML content of the flight search page.
    """
    payload = {
        "zone": zone,
        "url": flight_url,
        "format": "raw",
        "method": "GET",
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    response = requests.post(api_url, json=payload, headers=headers)
    response.raise_for_status()
    return response


def get_flight_description(response: requests.Response) -> list[str]:
    """
    Extracts flight information texts from the HTML response.

    Parameters:
    - response (requests.Response): The API response containing flight data.

    Returns:
    - list[str]: List of flight descriptions extracted from HTML.
    """
    soup = BeautifulSoup(response.text, "html.parser")
    return list(
        set(
            tag["aria-label"]
            for tag in soup.select("li > div > div")
            if "aria-label" in tag.attrs
        )
    )


def extract_currency(flight_url: str) -> str:
    """
    Extracts the currency from the flight URL.

    Parameters:
    - flight_url (str): The URL containing the flight search parameters.

    Returns:
    - str: The detected currency, defaulting to "UNKNOWN" if not found.
    """
    match = re.search(r"curr=([A-Z]+)", flight_url)
    return match.group(1) if match else "UNKNOWN"


def extract_price(text: str, currency: str) -> str | None:
    """Extracts the flight price from the text."""
    match = re.search(r"From (\d+) euros", text)
    return f"{match.group(1)} {currency}" if match else None


def extract_airlines(text: str) -> list[str]:
    """Extracts airline names from the text."""
    match = re.findall(r"flight with ([\w\s&\-]+)", text)
    return match[0].split(" and ") if match else []


def extract_departure_time(text: str) -> str | None:
    """Extracts the departure time from the text."""
    match = re.search(r"Leaves [\w\s]+ at (\d{1,2}:\d{2}\s*[APM]{2}?)", text)
    return match.group(1).replace("\u202f", " ").strip() if match else None


def extract_arrival_time(text: str) -> str | None:
    """Extracts the arrival time from the text."""
    match = re.search(r"arrives at [\w\s]+ at (\d{1,2}:\d{2}\s*[APM]{2}?)", text)
    return match.group(1).replace("\u202f", " ").strip() if match else None


def extract_flight_duration(text: str) -> str | None:
    """Extracts the total flight duration from the text."""
    match = re.search(r"Total duration (\d+\s*hr\s*\d*\s*min)", text)
    return match.group(1) if match else None


def extract_layovers(text: str) -> int:
    """Extracts the number of layovers from the text."""
    match = re.search(r"(\d+) stop", text)
    return int(match.group(1)) if match else 0


def extract_layover_details(text: str) -> list[dict[str, str]]:
    """Extracts detailed layover information from the text."""
    layover_times = re.findall(
        r"Layover \(\d+ of \d+\) is a (\d+\s*hr\s*\d*\s*min) layover", text
    )
    layover_airports = re.findall(r"layover at ([\w\s]+) in ([\w\s]+)\.", text)

    return [
        {
            "layover_time": layover_times[i],
            "layover_airport": f"{layover_airports[i][0]} ({layover_airports[i][1]})",
        }
        for i in range(min(len(layover_times), len(layover_airports)))
    ]


def extract_flight_info(
    flight_texts: list[str], currency: str
) -> list[dict[str, str | int | list]]:
    """
    Extracts structured flight information from raw text data.

    Parameters:
    - flight_texts (list[str]): List of raw text descriptions of flights.
    - currency (str): The currency used for pricing.

    Returns:
    - list[dict[str, str | int | list]]: List of dictionaries containing structured flight details.
    """
    flight_list = []

    for text in flight_texts:
        flight_info = {
            "price": extract_price(text, currency),
            "airlines": extract_airlines(text),
            "departure_time": extract_departure_time(text),
            "arrival_time": extract_arrival_time(text),
            "flight_duration": extract_flight_duration(text),
            "layovers": extract_layovers(text),
            "layover_details": extract_layover_details(text),
        }
        flight_list.append(flight_info)

    return flight_list


# Exemple


def main():
    load_dotenv(override=True)
    api_url = "https://api.brightdata.com/request"
    api_key = os.getenv("BRIGHTDATA_API_KEY") or ""
    flight_url = generate_flight_url(
        departure_date="2025-07-28",
        from_airport="CDG",
        to_airport="KIX",
        trip_type="one-way",
        seat_type="economy",
        adults=1,
        children=1,
    )
    zone = os.getenv("BRIGHTDATA_API_ZONE") or ""

    response = fetch_flight_data(api_url, api_key, flight_url, zone)
    flight_descriptions = get_flight_description(response)
    currency = extract_currency(flight_url)
    flight_data = extract_flight_info(flight_descriptions, currency)

    print(json.dumps(flight_data, indent=4))


if __name__ == "__main__":
    main()
