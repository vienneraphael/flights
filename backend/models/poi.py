from pydantic import BaseModel

from backend.models.constraint import DateConstraint, DurationConstraint


class StartPoint(BaseModel):
    name: str
    date_constraint: DateConstraint


class EndPoint(BaseModel):
    name: str
    date_constraint: DateConstraint


class PointOfInterest(BaseModel):
    arrival_name: str
    departure_name: str
    duration_constraint: DurationConstraint
