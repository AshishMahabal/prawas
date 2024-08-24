import pandas as pd
import streamlit as st
from amadeus import Client, ResponseError

# Initialize the Amadeus client
amadeus = Client(
    client_id=st.secrets["amadeus"]["api_key"],
    client_secret=st.secrets["amadeus"]["api_secret"]
)

# Search for flights
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

# Extract relevant flight data into a DataFrame
def extract_flight_data(flights, max_stops):
    flight_data = []
    
    for flight in flights:
        stopovers = len(flight['itineraries'][0]['segments']) - 1
        if stopovers <= max_stops:
            price = flight['price']['total']
            currency = flight['price']['currency']
            for itinerary in flight['itineraries']:
                total_duration = itinerary['duration'][2:]  # Skip 'PT' prefix
                for segment in itinerary['segments']:
                    airline = segment['carrierCode']
                    flight_number = segment['number']
                    departure = segment['departure']['iataCode']
                    arrival = segment['arrival']['iataCode']
                    departure_time = segment['departure']['at']
                    arrival_time = segment['arrival']['at']
                    
                    flight_data.append({
                        'Airline': f"{airline} {flight_number}",
                        'Departure': departure,
                        'Arrival': arrival,
                        'Departure Time': departure_time,
                        'Arrival Time': arrival_time,
                        'Duration': total_duration,
                        'Price': f"{price} {currency}"
                    })
    
    return pd.DataFrame(flight_data)

# Streamlit UI
def main():
    st.title("Travel Search App")
    
    # Sidebar with search options
    with st.sidebar:
        search_type = st.selectbox("Select Search Type", ["Flight Search", "Do Nothing"])
    
        if search_type == "Flight Search":
            origin = st.text_input("Origin", "LAX")
            destination = st.text_input("Destination", "JFK")
            departure_date = st.date_input("Departure Date").strftime("%Y-%m-%d")
            max_stops = st.selectbox("Max Stops", [0, 1, 2], index=1)
            search_button = st.button("Search Flights")
        elif search_type == "Do Nothing":
            st.write("Please select a search type from the dropdown menu.")
    
    # Display output in the main area
    if search_type == "Flight Search" and search_button:
        flights = search_flights(origin, destination, departure_date)
        if flights:
            flight_data = extract_flight_data(flights, max_stops)
            if not flight_data.empty:
                # Display the table in the main area
                st.dataframe(flight_data.sort_values(by="Price"))
            else:
                st.write("No flights found with the selected number of stopovers.")
        else:
            st.write("No flights found.")

if __name__ == "__main__":
    main()
