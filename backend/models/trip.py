import itertools
from datetime import date, timedelta
from enum import StrEnum
from functools import cached_property

import numpy as np
from pydantic import BaseModel, Field, computed_field

from backend.models.constraint import DateConstraint
from backend.models.poi import EndPoint, PointOfInterest, StartPoint
from backend.url import generate_flight_url


# Arrival is arrival in an airport
# Departure is the departure form a airport
class UserTripStepType(StrEnum):
    ARRIVAL = "Arrival"
    DEPARTURE = "Departure"


class UserTripStep(BaseModel):
    name: str
    type: UserTripStepType
    date_constraint: DateConstraint


class TripFlight(BaseModel):
    departure_date: date
    from_airport: str
    to_airport: str
    result: list[dict] | None = Field(
        None, description="flight results from Google Flights", init=False
    )

    @computed_field
    @cached_property
    def url(self) -> str:
        formatted_date = self.departure_date.strftime("%Y-%m-%d")
        return generate_flight_url(
            departure_date=formatted_date,
            from_airport=self.from_airport,
            to_airport=self.to_airport,
        )

    def __hash__(self):
        return hash(self.url)


class Scenario(BaseModel):
    flights: list[TripFlight]

    @computed_field
    @cached_property
    def min_total_price(self) -> int:
        minimal_price_flights = [flight.result[0]["price"] for flight in self.flights]
        return sum(minimal_price_flights)


class UserTrip(BaseModel):
    start_point: StartPoint
    points_of_interest: list[PointOfInterest]
    end_point: EndPoint

    @computed_field
    @cached_property
    def steps(self) -> list[UserTripStep]:
        previous_step = UserTripStep(
            name=self.start_point.name,
            type=UserTripStepType.DEPARTURE,
            date_constraint=self.start_point.date_constraint,
        )
        trip_steps = [previous_step]
        for point_of_interest in self.points_of_interest:
            trip_steps.append(
                UserTripStep(
                    name=point_of_interest.arrival_name,
                    type=UserTripStepType.ARRIVAL,
                    date_constraint=previous_step.date_constraint,
                )
            )
            previous_step = UserTripStep(
                name=point_of_interest.departure_name,
                type=UserTripStepType.DEPARTURE,
                date_constraint=DateConstraint(
                    min_date=previous_step.date_constraint.min_date
                    + timedelta(days=point_of_interest.duration_constraint.min_days),
                    max_date=previous_step.date_constraint.max_date
                    + timedelta(days=point_of_interest.duration_constraint.max_days),
                ),
            )
            trip_steps.append(previous_step)
        trip_steps.append(
            UserTripStep(
                name=self.end_point.name,
                type=UserTripStepType.ARRIVAL,
                date_constraint=self.end_point.date_constraint,
            )
        )
        return trip_steps

    @computed_field
    @cached_property
    def candidate_trips(self) -> list[Scenario]:
        trips = []
        it = iter(self.steps)
        for departure, arrival in zip(it, it, strict=True):
            trip_flights = []
            for possible_date in departure.date_constraint.possible_dates:
                trip_flights.append(
                    TripFlight(
                        departure_date=possible_date,
                        from_airport=departure.name,
                        to_airport=arrival.name,
                    )
                )
            trips.append(trip_flights)
        return [
            Scenario(flights=list(flight_combination))
            for flight_combination in itertools.product(*trips)
        ]

    @computed_field
    @cached_property
    def possible_trips(self) -> list[Scenario]:
        validated_trips = []
        candidate_trips = self.candidate_trips
        for candidate_trip in candidate_trips:
            flight_dates = [flight.departure_date for flight in candidate_trip.flights]
            diff = np.diff(flight_dates)
            constraint_values = [
                poi.duration_constraint.max_days for poi in self.points_of_interest
            ]
            passed_tests = True
            for days_diff, constraint_value in zip(
                diff, constraint_values, strict=True
            ):
                if days_diff.days > constraint_value:
                    passed_tests = False
                    break
            if not passed_tests:
                continue
            if flight_dates[-1] < self.end_point.date_constraint.max_date:
                validated_trips.append(Scenario(flights=candidate_trip.flights))
        return validated_trips

    @computed_field
    @cached_property
    def unique_requests(self) -> list[TripFlight]:
        possible_trips = [scenario.flights for scenario in self.possible_trips]
        return list(set(np.array(possible_trips).flatten().tolist()))
