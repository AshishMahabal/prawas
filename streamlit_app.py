from amadeus import Client, ResponseError
import streamlit as st

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

# Streamlit UI
def main():
    st.title("Flight Search App")

    origin = st.text_input("Origin", "LAX")
    destination = st.text_input("Destination", "JFK")
    departure_date = st.date_input("Departure Date").strftime("%Y-%m-%d")
    
    # Dropdown for max stops
    max_stops = st.selectbox("Max Stops", [0, 1, 2], index=1)

    if st.button("Search Flights"):
        flights = search_flights(origin, destination, departure_date)
        if flights:
            filtered_flights = []
            for flight in flights:
                stopovers = len(flight['itineraries'][0]['segments']) - 1
                if stopovers <= max_stops:
                    filtered_flights.append(flight)
                    
            if filtered_flights:
                for flight in filtered_flights:
                    price = flight['price']['total']
                    st.write(f"Total Price: {price} {flight['price']['currency']}")
                    
                    for itinerary in flight['itineraries']:
                        for segment in itinerary['segments']:
                            airline = segment['carrierCode']
                            flight_number = segment['number']
                            departure = segment['departure']['iataCode']
                            arrival = segment['arrival']['iataCode']
                            departure_time = segment['departure']['at']
                            st.write(f"Flight {airline} {flight_number} from {departure} to {arrival} at {departure_time}")
            else:
                st.write("No flights found with the selected number of stopovers.")
        else:
            st.write("No flights found.")

if __name__ == "__main__":
    main()

