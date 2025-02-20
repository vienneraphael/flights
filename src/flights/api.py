import requests
import re
import json
from bs4 import BeautifulSoup

def fetch_flight_data(
    api_url: str,
    api_key: str,
    flight_url: str,
    zone: str,
  ) -> requests.Response:

    """
  Fetches flight data from the specified API URL.

  Parameters:
  - api_url: str, SERP API Url of BrightData.
  - api_key: str, The API Key BrightData generate in your account.
  - flight_url: str, URL containing flight search parameters.
  - zone: str, Name of your API zone configuration project on BrightData.

  Returns:
  - HTML code response for of the flight_url. 

  """
    payload = {
        "zone": zone,
        "url": flight_url,
        "format": "raw",
        "method": "GET",
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    return requests.post(api_url, json=payload, headers=headers)

def get_flight_texts(response):

    soup = BeautifulSoup(response.text, "html.parser")
    return list(set([tag.attrs['aria-label'] for tag in soup.select('li > div > div') if 'aria-label' in tag.attrs]))
    
    """
    Extract flight information texts from the HTML response.
    
    Parameters:
    - response: The API response containing flight data.
    
    Returns:
    - List of flight descriptions extracted from HTML.
    """
  
def extract_currency(flight_url):
    
    match = re.search(r"curr=([A-Z]+)", flight_url)
    return match.group(1) if match else "UNKNOWN"

    """
    Extract currency from the flight URL.

    Parameters:
    - flight_url: The URL containing the flight search parameters.

    Returns:
    - The detected currency (default: "UNKNOWN").
    """

def extract_flight_info(flight_texts, currency):

    flight_list = []
    
    for text in flight_texts:
        flight_info = {}

        # Extract price
        price_match = re.search(r'From (\d+) euros', text)
        flight_info['price'] = f"{price_match.group(1)} {currency}" if price_match else None

        # Extract airlines
        airline_match = re.findall(r'flight with ([\w\s&\-]+)', text)
        flight_info['airlines'] = airline_match[0].split(" and ") if airline_match else []

        # Extract departure time
        departure_match = re.search(r'Leaves [\w\s]+ at (\d{1,2}:\d{2}\s*[APM]{2}?)', text)
        flight_info['departure_time'] = departure_match.group(1).replace("\u202f", " ").strip() if departure_match else None

        # Extract arrival time
        arrival_match = re.search(r'arrives at [\w\s]+ at (\d{1,2}:\d{2}\s*[APM]{2}?)', text)
        flight_info['arrival_time'] = arrival_match.group(1).replace("\u202f", " ").strip() if arrival_match else None

        # Extract flight duration
        duration_match = re.search(r'Total duration (\d+\s*hr\s*\d*\s*min)', text)
        flight_info['flight_duration'] = duration_match.group(1) if duration_match else None

        # Extract layovers
        layover_match = re.search(r'(\d+) stop', text)
        flight_info['layovers'] = int(layover_match.group(1)) if layover_match else 0

        # Extract layover details
        layover_time_match = re.findall(r'Layover \(\d+ of \d+\) is a (\d+\s*hr\s*\d*\s*min) layover', text)
        layover_airport_match = re.findall(r'layover at ([\w\s]+) in ([\w\s]+)\.', text)

        layovers_list = [
            {"layover_time": layover_time_match[i], "layover_airport": f"{layover_airport_match[i][0]} ({layover_airport_match[i][1]})"}
            for i in range(len(layover_time_match))
            if i < len(layover_airport_match)
        ]

        flight_info['layover_details'] = layovers_list
        flight_list.append(flight_info)

    return flight_list

    """
    Extract structured flight information from raw text data.
    
    Parameters:
    - flight_texts: List of raw text descriptions of flights.
    
    Returns:
    - List of dictionaries containing structured flight details.
    """

 # Exemple

def main():
    api_url = "https://api.brightdata.com/request"
    api_key = "your_api_key_there"  # Replace with your actual API key
    flight_url = "https://www.google.com/travel/flights?tfs=GhoSCjIwMjUtMjgtMDNqBRIDQ0RHcgUSA0tJWEIDAQECSAGYAQI=&curr=EUR" # Replace with your actual flight_url
    zone = "your_api_zone_there"  # Replace with the actual zone generate from BrightData
    
    response = fetch_flight_data(api_url, api_key, flight_url, zone)
    if response.status_code == 200:
        flight_texts = get_flight_texts(response)
        currency = extract_currency(flight_url)
        flight_data = extract_flight_info(flight_texts, currency)
        print(json.dumps(flight_data, indent=4)) # Convert dictionaries to json.
    else:
        print(f"Failed to fetch data: {response.status_code}")

if __name__ == "__main__":
    main()