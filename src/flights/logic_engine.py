import json
import os
import typing as t
from datetime import datetime, timedelta, date
from pydantic import BaseModel, Field, computed_field
from enum import StrEnum
from dotenv import load_dotenv
from fast_flights import Airport
from flights.api import (
    get_flight_description,
    fetch_flight_data,
    extract_currency,
    extract_flight_info,
)
from flights.url import generate_flight_url



class SeatType(StrEnum):
    ECONOMY = 'economy'
    PREMIUM = 'premium economy'
    BUSINESS = 'business'
    FIRST = 'first'

class FlightRequest(BaseModel):
    from_airport: Airport
    to_airport: Airport
    departure_date: date
    max_stopovers: int
    seat_type: SeatType
    adults: int

    @computed_field
    def url(self) -> str:
        return generate_flight_url(
            departure_date=self.departure_date.strftime("%Y-%m-%d"),
            from_airport=self.from_airport,
            to_airport=self.to_airport,
            seat_type=self.seat_type,
            max_stops=self.max_stopovers,
            adults=self.adults,
        )

class UserTripParams(BaseModel):
    from_airport: Airport
    to_airport: Airport
    seat_type: SeatType
    min_departure_datetime: datetime = Field(gt=datetime.now())
    max_return_datetime: datetime = Field(gt=datetime.now())
    min_trip_duration_days: int = Field(gt=0)
    max_trip_duration_days: int = Field(gt=0)
    adults: int = Field()
    max_stopovers: int = Field()
    max_price: float = Field(gt=0)

    def generate_possible_trips(self) -> t.List[t.List[FlightRequest]]:
        """
        Generates possible trips (list of outbound and return flights)
        """
        possible_trips = []
        departure = self.min_departure_datetime
        while departure <= self.max_return_datetime:
            return_time = self.min_departure_datetime + timedelta(days=self.min_trip_duration_days)
            while (return_time - departure).days <= self.max_trip_duration_days:
                possible_trips.append([
                    FlightRequest(
                        from_airport=self.from_airport,
                        to_airport=self.to_airport,
                        departure_date=departure.date(),
                        max_stopovers=self.max_stopovers,
                        seat_type=self.seat_type,
                        adults=self.adults,
                    ),
                    FlightRequest(
                        from_airport=self.to_airport,
                        to_airport=self.from_airport,
                        departure_date=return_time.date(),
                        max_stopovers=self.max_stopovers,
                        seat_type=self.seat_type,
                        adults=self.adults,
                    )
                ])
                return_time += timedelta(days=1)
            departure += timedelta(days=1)
        return possible_trips

def process_flight_request(
    flight_req: FlightRequest, 
    api_url: str, 
    api_key: str, 
    zone: str
) -> t.List[dict[str, t.Any]]:
    """
    Processes a flight request: calls the API and extracts flight information.
    """
    flight_url = flight_req.url
    try:
        response = fetch_flight_data(api_url, api_key, flight_url, zone)
        flight_descriptions = get_flight_description(response)
        currency = extract_currency(flight_url)
        flight_info = extract_flight_info(flight_descriptions, currency)
        return flight_info
    except Exception as e:
        print(f"Error processing flight {flight_url}: {e}")
        return []

def process_trip(
    trip: t.List[FlightRequest], 
    api_url: str, 
    api_key: str, 
    zone: str
) -> t.List[t.List[dict[str, t.Any]]]:
    """
    For each flight in a trip (outbound and return), executes the requests and returns the results.
    """
    results = []
    for flight_req in trip:
        results.append(process_flight_request(flight_req, api_url, api_key, zone))
    return results

def main():
    """
    Main execution function: configures API, generates user trip parameters, 
    processes all possible trips, and outputs the results.
    """
    api_url = "https://api.brightdata.com/request"
    api_key = os.getenv("BRIGHTDATA_API_KEY")
    zone = os.getenv("BRIGHTDATA_ZONE")

    user_params = UserTripParams(
        from_airport="CDG",
        to_airport="KIX",
        seat_type=SeatType.ECONOMY,
        min_departure_datetime=datetime(2025, 3, 25, 10, 0),
        max_return_datetime=datetime(2025, 4, 5, 23, 59),
        min_trip_duration_days=3,
        max_trip_duration_days=7,
        adults=1,
        max_stopovers=1,
        max_price=1000.0
    )

    possible_trips = user_params.generate_possible_trips()
    print(f"Number of possible trips generated: {len(possible_trips)}")

    for i, trip in enumerate(possible_trips, start=1):
        print(f"\nProcessing trip {i}:")
        trip_results = process_trip(trip, api_url, api_key, zone)
        print(json.dumps(trip_results, indent=4))

if __name__ == "__main__":
    main()