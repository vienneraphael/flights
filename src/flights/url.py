from fast_flights import FlightData, Passengers, create_filter

def generate_flight_url(
        departure_date: str,
        from_airport: str,
        to_airport: str,
        trip_type: str="one-way",
        seat_type: str="economy",
        adults: int=1,
        children: int=0,
        infants_in_seat: int=0,
        infants_on_lap: int=0,
        currency: str="EUR"
) -> str:
    """ 
    Generate Flights URL form parameters.

    Paraleters:
    - departure_date: str,date of departure, formated as YYYY-DD-MM.
    - from_airport: str, IATA code of the departure airport (e.g., "CDG".)
    - to_airport: str, IATA code of the arrival airport (e.g., "JFK")
    - trip_type: str, type of trip, either "one-way" or "round-trip" (default: "one-way").
    - seat_type: str, class of service, e.g., "economy", "business" (default: "economy").
    - adults: int, number of adult passengers (default: 1).
    - children: int, number of child passengers (default: 0).
    - infants_in_seat: int, number of infants sitting on laps ( default: 0).
    - infants_on_laps : int, number of infants on laps (default: 0).
    - currency: str, currency for pricing (default: "EUR").

    Returns:
    - str, a URL string with the flight search parameters.
    """
        
    filter = create_filter(
        flight_data=[
            FlightData(
                date=departure_date,
                from_airport=from_airport,
                to_airport=to_airport,
            )
        ],
        trip=trip_type,
        seat=seat_type,
        passengers=Passengers(
                adults=adults,
                children=children,
                infants_in_seat=infants_in_seat,
                infants_on_lap=infants_on_lap,
        ),
    )

    b64=filter.as_b64().decode('utf-8')
    return f"https://www.google.com/travel/flights?tfs={b64}&curr={currency}"

#Exemple
def main():
    url= generate_flight_url(
        departure_date="2025-28-03",
        from_airport="CDG",
        to_airport="KIX",
        trip_type="one-way",
        seat_type="economy",
        adults=2,
        children=1,
    )
    print(url)

if __name__=="__main__":
    main()
