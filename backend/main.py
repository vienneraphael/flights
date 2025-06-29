from dotenv import load_dotenv
from fastapi import FastAPI

from backend.models.trip import Scenario, UserTrip
from backend.utils import fetch_flights_from_urls

load_dotenv(override=True)
app = FastAPI()


@app.get("/health")
async def healthcheck():
    return {"status": "ok"}


@app.get("/")
async def root():
    return {"message": "Welcome to the flights API"}


@app.post("/flights_from_urls/")
async def fetch_from_urls(urls: list[str]):
    results = await fetch_flights_from_urls(urls=urls)
    for result in results.values():
        result["flights"] = sorted(result["flights"], key=lambda d: d.get("price"))[:3]
    return results


@app.post("/flights/", response_model=list[Scenario])
async def fetch_multiple_flights(trip: UserTrip):
    flight_requests = trip.unique_requests
    results = await fetch_flights_from_urls(
        urls=[flight_req.url for flight_req in flight_requests]
    )
    for result in results.values():
        result["flights"] = sorted(result["flights"], key=lambda d: d.get("price"))[:3]
    possible_trips = trip.possible_trips
    for scenario in possible_trips:
        for trip_flight in scenario.flights:
            unique_id = hash(trip_flight)
            trip_flight.result = results[unique_id]["flights"]
    return possible_trips
