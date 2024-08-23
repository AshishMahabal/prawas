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

# Load API keys from config file
#def load_config(config_file='config.ini'):
def load_config():
    # config = configparser.ConfigParser()
    # config.read(config_file)
    api_key = st.secrets["amadeus"]["api_key"]
    api_secret = st.secrets["amadeus"]["api_secret"]
    return api_key, api_secret

# Get access token from Amadeus API
def get_access_token(api_key, api_secret):
    auth_url = 'https://test.api.amadeus.com/v1/security/oauth2/token'
    auth_data = {
        'grant_type': 'client_credentials',
        'client_id': api_key,
        'client_secret': api_secret
    }
    response = requests.post(auth_url, data=auth_data)
    return response.json().get('access_token')

# Search for flights
def search_flights(access_token, origin, destination, departure_date):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    flight_search_url = 'https://test.api.amadeus.com/v2/shopping/flight-offers'
    params = {
        'originLocationCode': origin,
        'destinationLocationCode': destination,
        'departureDate': departure_date,
        'currencyCode': 'USD'
    }
    response = requests.get(flight_search_url, headers=headers, params=params)
    return response.json()

# Streamlit UI
def main():
    st.title("Flight Search App")
    
    origin = st.text_input("Origin", "LAX")
    destination = st.text_input("Destination", "JFK")
    departure_date = st.date_input("Departure Date").strftime("%Y-%m-%d")
    
    if st.button("Search Flights"):
        api_key, api_secret = load_config()
        access_token = get_access_token(api_key, api_secret)
        flight_offers = search_flights(access_token, origin, destination, departure_date)
        
        if flight_offers:
            for offer in flight_offers.get('data', []):
                price = offer['price']['total']
                itinerary = offer['itineraries'][0]
                flight_info = f"Flight from {itinerary['segments'][0]['departure']['iataCode']} to {itinerary['segments'][0]['arrival']['iataCode']} costs {price} USD."
                st.write(flight_info)
        else:
            st.write("No flights found.")

if __name__ == "__main__":
    main()

