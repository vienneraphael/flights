from enum import StrEnum

from pydantic import BaseModel

from backend.models.constraint import DateConstraint
from backend.models.poi import EndPoint, PointOfInterest, StartPoint


# Arrival is arrival in an airport
# Departure is the derpature form a airport
class TripStepType(StrEnum):
    ARRIVAL = "Arrival"
    DEPARTURE = "Departure"


class TripStep(BaseModel):
    name: str
    type: TripStepType
    date_constraint: DateConstraint


class Trip(BaseModel):
    start_point: StartPoint
    points_of_interest: list[PointOfInterest]
    end_point: EndPoint
    steps: list[TripStep]
