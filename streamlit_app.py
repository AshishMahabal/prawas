import streamlit as st
from flight_search import FlightSearch

def main():
    st.title("Travel Search App")
    
    # Initialize the FlightSearch class with Amadeus credentials from secrets
    flight_search = FlightSearch(
        client_id=st.secrets["amadeus"]["api_key"],
        client_secret=st.secrets["amadeus"]["api_secret"]
    )
    
    # Sidebar for search options
    with st.sidebar:
        search_type = st.selectbox("Select Search Type", ["Flight Search", "Do Nothing"])
        
        if search_type == "Flight Search":
            origin = st.text_input("Origin", "LAX")
            destination = st.text_input("Destination", "JFK")
            departure_date = st.date_input("Departure Date").strftime("%Y-%m-%d")
            max_stops = st.selectbox("Max Stops", [0, 1, 2], index=1)
            currency = st.text_input("Currency Code", "USD")
            search_button = st.button("Search Flights")
        elif search_type == "Do Nothing":
            st.info("This option is currently a placeholder for future features.")
    
    # Display the selected currency in the main area
    if search_type == "Flight Search":
        st.write(f"Displaying prices in: {currency}")
    
    # Handle flight search and display results
    if search_type == "Flight Search" and search_button:
        try:
            flights = flight_search.search_flights(origin, destination, departure_date, currency)
            if flights:
                flight_data = flight_search.extract_flight_data(flights, max_stops)
                if not flight_data.empty:
                    # Display the DataFrame with proper sorting
                    st.dataframe(
                        flight_data.sort_values(by=["Price", "Duration"], ascending=[True, True]),
                        use_container_width=True
                    )
                else:
                    st.warning("No flights found with the selected number of stopovers.")
            else:
                st.warning("No flights found.")
        except Exception as e:
            st.error(str(e))
    elif search_type == "Do Nothing":
        st.info("Please select a search type from the dropdown menu.")

if __name__ == "__main__":
    main()
