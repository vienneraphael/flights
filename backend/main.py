from dotenv import load_dotenv
from fastapi import FastAPI

from backend.models.trip import Trip
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
    return results


@app.post("/flights/")
async def fetch_multiple_flights(trip: Trip):
    flight_requests = trip.unique_requests
    results = await fetch_flights_from_urls(
        urls=[flight_req.url for flight_req in flight_requests]
    )
    return results
