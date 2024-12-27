from fast_flights import FlightData, Passengers, create_filter

def generate_flight_url(
        departure_date,
        from_airport,
        to_airport,
        trip_type="one-way",
        seat_type="economy",
        adults=1,
        children=0,
        infants_in_seat=0,
        infants_on_lap=0,
        currency="EUR"
):
    
    filter = create_filter(
        flight_data=[
            FlightData(
                date = departure_date,
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