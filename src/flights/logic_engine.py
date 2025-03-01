from datetime import datetime, timedelta, date
from pydantic import BaseModel, Field, computed_field
from fast_flights import Airport
import typing as t
from enum import StrEnum
from url import generate_flight_url

class SeatType(StrEnum):
    ECONOMY  = 'economy'
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
    min_departure_datetime: datetime=Field(gt=datetime.now()),
    max_return_datetime: datetime=Field(gt=datetime.now()),
    min_trip_duration_days: int=Field(gt=0),
    max_trip_duration_days: int=Field(gt=0),
    adults: int=Field()
    max_stopovers: int=Field()
    max_price: float=Field(gt=0)

    def generate_possible_trips(self) -> t.List[t.List[FlightRequest]]:
        """Currently works for trips having one destination.

        Returns
        -------
        t.List[t.List[FlightRequest]]
            the possible trips, each trip is a list of flight requests.
        """
        possible_trips = []
        gone = self.min_departure_datetime
        while gone <= self.max_return_datetime:
            back = self.min_departure_datetime + timedelta(days=self.min_trip_duration_days)
            while (gone - back).days < self.max_trip_duration_days:
                possible_trips.append(
                    [
                        # first flight
                        FlightRequest(
                            from_airport=self.from_airport,
                            to_airport=self.to_airport,
                            departure_date=gone.date(),
                            max_stopovers=self.max_stopovers,
                            seat_type=self.seat_type,
                            adults=self.adults,
                        ),
                        # flight back
                        FlightRequest(
                            from_airport=self.to_airport,
                            to_airport=self.from_airport,
                            departure_date=back.date(),
                            max_stopovers=self.max_stopovers,
                            seat_type=self.seat_type,
                            adults=self.adults,
                        )
                    ]
                )
                back += timedelta(days=1)
            gone += timedelta(days=1)
        return possible_trips

def main():
    pass

if __name__ == '__main__':
    main()
