from pydantic import BaseModel

from backend.models.flight_location import FlightLocation


class Trip(BaseModel):
    flight_locations: list[FlightLocation]
