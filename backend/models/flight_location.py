from enum import StrEnum

from pydantic import BaseModel


class FlightLocationType(StrEnum):
    ARRIVAL = "Arrival"
    DEPARTURE = "Departure"


class FlightLocation(BaseModel):
    type: FlightLocationType
