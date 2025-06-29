import asyncio

from dotenv import load_dotenv
from fastapi import FastAPI

from backend.api import (
    extract_currency,
    extract_flight_info,
    fetch_flight_data,
    get_flight_description,
)
from backend.models.trip import Trip

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
    results = {}
    async with asyncio.TaskGroup() as tg:
        tasks = {url: tg.create_task(fetch_flight_data(url)) for url in urls}
    for url, task in tasks.items():
        try:
            response = task.result()
            descriptions = get_flight_description(response)
            currency = extract_currency(url)
            flight_data = extract_flight_info(descriptions, currency)
            results[hash(url)] = {"url": url, "flights": flight_data}
        except Exception as e:
            results[hash(url)] = {"url": url, "error": e}
    return results


@app.post("/flights/")
async def fetch_multiple_flights(trip: Trip):
    flight_requests = trip.unique_requests
    results = {}

    async with asyncio.TaskGroup() as tg:
        tasks = {
            flight_req.url: tg.create_task(fetch_flight_data(flight_req.url))
            for flight_req in flight_requests
        }

    # At this point, all tasks have completed or been cancelled
    for url, task in tasks.items():
        try:
            response = task.result()
            descriptions = get_flight_description(response)
            currency = extract_currency(url)
            flight_data = extract_flight_info(descriptions, currency)
            results[hash(url)] = {"url": url, "flights": flight_data}
        except Exception as e:
            results[hash(url)] = {"url": url, "error": e}

    return results
