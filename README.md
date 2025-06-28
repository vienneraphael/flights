# Flights

The goal of this project is to provide a tool for optimizing flight travel costs using a flights API.

The project features an app allowing the user to select:

- A minimal departure date
- A maximal return date
- The origin city (e.g. Paris or France)
- A list of target destinations (e.g. [Japan, Seoul]) with their respective duration of stay in days (e.g. [10, 5])
- A sensibility parameter to allow staying +/- days for a target destination, negative and positive for each target destination.

Note that destinations or origin can also be countries. In this case, all the airports of the country will be considered.

It's also possible to enter a list of airports codes.

## tfs Builder

Build a function that encodes flight search parameters in a google flights url under the `tfs` flag (see `fast-flights` python library for that).

## Flights API

Retrieve flight data from an external API (<https://brightdata.com/pricing/serp>)
Note: use the `&curr=EUR` flag at the end of the url to get results in euros.

## Logic Engine

Create an engine able to translate user inputs (min departure date, max return date, origin city and target destinations) into a battery of Flights API calls to compare. This is the logic behind the app.

## Interface

Create a simple interface able to translate user input in requests with the logic engine, launch these requests and display them back in the app, giving the relevant GFlights URLs to the user.

We will use streamlit for this.

## Deployment

Deploy using Docker on the Streamlit Cloud.
