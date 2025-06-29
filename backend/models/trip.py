import itertools
from datetime import date, timedelta
from enum import StrEnum
from functools import cached_property

from pydantic import BaseModel, computed_field

from backend.models.constraint import DateConstraint
from backend.models.poi import EndPoint, PointOfInterest, StartPoint
from backend.url import generate_flight_url


# Arrival is arrival in an airport
# Departure is the departure form a airport
class TripStepType(StrEnum):
    ARRIVAL = "Arrival"
    DEPARTURE = "Departure"


class TripStep(BaseModel):
    name: str
    type: TripStepType
    date_constraint: DateConstraint


class TripFlight(BaseModel):
    departure_date: date
    from_airport: str
    to_airport: str

    @computed_field
    @cached_property
    def url(self) -> str:
        formatted_date = self.departure_date.strftime("%Y-%d-%m")
        return generate_flight_url(
            departure_date=formatted_date,
            from_airport=self.from_airport,
            to_airport=self.to_airport,
        )


class Trip(BaseModel):
    start_point: StartPoint
    points_of_interest: list[PointOfInterest]
    end_point: EndPoint

    @computed_field
    @cached_property
    def steps(self) -> list[TripStep]:
        previous_step = TripStep(
            name=self.start_point.name,
            type=TripStepType.DEPARTURE,
            date_constraint=self.start_point.date_constraint,
        )
        trip_steps = [previous_step]
        for point_of_interest in self.points_of_interest:
            trip_steps.append(
                TripStep(
                    name=point_of_interest.arrival_name,
                    type=TripStepType.ARRIVAL,
                    date_constraint=previous_step.date_constraint,
                )
            )
            previous_step = TripStep(
                name=point_of_interest.departure_name,
                type=TripStepType.DEPARTURE,
                date_constraint=DateConstraint(
                    min_date=previous_step.date_constraint.min_date
                    + timedelta(days=point_of_interest.duration_constraint.min_days),
                    max_date=previous_step.date_constraint.max_date
                    + timedelta(days=point_of_interest.duration_constraint.max_days),
                ),
            )
            trip_steps.append(previous_step)
        trip_steps.append(
            TripStep(
                name=self.end_point.name,
                type=TripStepType.ARRIVAL,
                date_constraint=self.end_point.date_constraint,
            )
        )
        return trip_steps

    @computed_field
    @cached_property
    def candidate_trips(self) -> list[TripFlight]:
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
        return list(itertools.product(*trips))
