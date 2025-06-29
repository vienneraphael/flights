import asyncio

from backend.api import (
    extract_currency,
    extract_flight_info,
    fetch_flight_data,
    get_flight_description,
)


async def fetch_flights_from_urls(urls: list[str]):
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
