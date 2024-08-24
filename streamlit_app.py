import streamlit as st
from flight_search import FlightSearch

def main():
    st.title("थोडा प्रवास करू या")
    
    # Initialize the FlightSearch class with Amadeus credentials from secrets
    flight_search = FlightSearch(
        client_id=st.secrets["amadeus"]["api_key"],
        client_secret=st.secrets["amadeus"]["api_secret"]
    )
    
    # Sidebar for search options
    with st.sidebar:
        search_type = st.selectbox("Select Search Type", ["Flight Search", "Airports", "Do Nothing"])
        
        if search_type == "Flight Search":
            origin = st.text_input("Origin", "LAX").upper()
            destination = st.text_input("Destination", "JFK").upper()
            departure_date = st.date_input("Departure Date").strftime("%Y-%m-%d")
            max_stops = st.selectbox("Max Stops", [0, 1, 2], index=1)
            currency = st.text_input("Currency Code", "USD")
            search_button = st.button("Search Flights")
        elif search_type == "Airports":
            country = st.selectbox("Select Country", ["USA", "Canada", "UK", "India", "Australia", ...])
            intl_flights_only = st.radio("Include Only International Airports?", ("Yes", "No"))
            show_airports_button = st.button("Show Airports")
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
    elif search_type == "Airports" and show_airports_button:
        airport_data = get_airports_by_country(country, intl_flights_only)
        
        if not airport_data.empty:
            # Display the selected country and filter
            st.write(f"Airports in {country} ({'International' if intl_flights_only == 'Yes' else 'All'})")
            
            # Pagination and sorting
            page_size = st.selectbox("Entries per page", [10, 20, 50, 100, "All"], index=1)
            if page_size == "All":
                st.dataframe(airport_data)
            else:
                page_size = int(page_size)
                st.dataframe(airport_data.head(page_size))  # Implement proper pagination logic here
        else:
            st.write(f"No airports found for {country} ({'International' if intl_flights_only == 'Yes' else 'All'}).")
    elif search_type == "Do Nothing":
            st.info("Please select a search type from the dropdown menu.")

if __name__ == "__main__":
    main()
