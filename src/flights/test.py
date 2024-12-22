from bs4 import BeautifulSoup
import requests
import json

def get_price(soup_element):
    price = soup_element.find('div','BVAVmf').find('div','YMlIz').get_text()

    return price


def get_time(soup_element):
    spans = soup_element.find('div','Ir0Voe').find('div','zxVSec', recursive=False).find_all('span', 'eoY5cb')

    time = ""

    for span in spans:
        time = time + span.get_text() + "; "

    return time


def get_airline(soup_element):
    airline = soup_element.find('div','Ir0Voe').find('div','sSHqwe')

    spans = airline.find_all('span', attrs={"class": None}, recursive=False)

    result = ""

    for span in spans:
        result = result + span.get_text() + "; "

    return result


def save_results(results, filepath):
    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(results, file, ensure_ascii=False, indent=4)

    return


def get_flights_html(url):
    payload = {
        'source': 'google',
        'render': 'html',
        'url': url,
    }

    # Get response.
    response = requests.request(
        'POST',
        'https://realtime.oxylabs.io/v1/queries',
        auth=('amatera_BY6CZ', 'Oxylabs77+oxylabs'),
        json=payload,
    )

    response_json = response.json()
    html = response_json['results'][0]['content']

    return html


def extract_flight_information_from_soup(soup_of_the_whole_page):
    flight_listings = soup_of_the_whole_page.find_all('li','pIav2d')

    flights = []

    for listing in flight_listings:
        if listing is not None:
            price = get_price(listing)
            time = get_time(listing)
            airline = get_airline(listing)

            flight = {
                "airline": airline,
                "time": time,
                "price": price
            }

            flights.append(flight)

    return flights


def extract_flights_data_from_urls(urls):
    constructed_flight_results = []

    for url in urls:
        html = get_flights_html(url)

        soup = BeautifulSoup(html,'html.parser')

        flights = extract_flight_information_from_soup(soup)

        constructed_flight_results.append({
            'url': url,
            'flight_data': flights
        })

    return constructed_flight_results


def main():
    results_file = 'data.json'

    urls = [
        
    ]

    constructed_flight_results = extract_flights_data_from_urls(urls)

    save_results(constructed_flight_results, results_file)


if __name__ == "__main__":
    main()