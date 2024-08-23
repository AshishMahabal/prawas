import streamlit as st
import pandas as pd
import math
from pathlib import Path
import configparser
import requests

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='करु या थोडा प्रवास',
    #page_icon=':earth_americas:', # This is an emoji shortcode. Could be a URL too.
)

# Load your API keys from config or environment variables
api_key = st.secrets["amadeus"]["api_key"]
api_secret = st.secrets["amadeus"]["api_secret"]

# Initialize the Amadeus client
amadeus = Client(
    client_id=api_key,
    client_secret=api_secret
)

# Example function to search for flights
def search_flights(origin, destination, departure_date):
    try:
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=destination,
            departureDate=departure_date,
            adults=1
        )
        return response.data
    except ResponseError as error:
        st.write(f"Error: {error}")
        return None

# Streamlit UI
def main():
    st.title("Flight Search App")

    origin = st.text_input("Origin", "LAX")
    destination = st.text_input("Destination", "JFK")
    departure_date = st.date_input("Departure Date").strftime("%Y-%m-%d")

    if st.button("Search Flights"):
        flights = search_flights(origin, destination, departure_date)
        if flights:
            for flight in flights:
                st.write(f"Flight from {flight['itineraries'][0]['segments'][0]['departure']['iataCode']} "
                         f"to {flight['itineraries'][0]['segments'][0]['arrival']['iataCode']} "
                         f"at {flight['itineraries'][0]['segments'][0]['departure']['at']}")
        else:
            st.write("No flights found.")

if __name__ == "__main__":
    main()
