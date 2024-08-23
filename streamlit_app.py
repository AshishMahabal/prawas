from amadeus import Client, ResponseError
import streamlit as st

# Initialize the Amadeus client
amadeus = Client(
    client_id=st.secrets["amadeus"]["api_key"],
    client_secret=st.secrets["amadeus"]["api_secret"]
)

# Search for flights with a limit on max stops
def search_flights(origin, destination, departure_date, max_stops=1):
    try:
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=destination,
            departureDate=departure_date,
            adults=1,
            max=1 if max_stops is None else max_stops
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
    
    # Dropdown for max stops
    max_stops = st.selectbox("Max Stops", [0, 1, 2], index=1)

    if st.button("Search Flights"):
        flights = search_flights(origin, destination, departure_date, max_stops)
        if flights:
            for flight in flights:
                price = flight['price']['total']
                st.write(f"Total Price: {price} {flight['price']['currency']}")
                
                for itinerary in flight['itineraries']:
                    for segment in itinerary['segments']:
                        st.write(f"Flight from {segment['departure']['iataCode']} "
                                 f"to {segment['arrival']['iataCode']} "
                                 f"at {segment['departure']['at']}")
        else:
            st.write("No flights found.")

if __name__ == "__main__":
    main()
