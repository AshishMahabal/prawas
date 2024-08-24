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
            try:
                countries = flight_search.get_countries()
                if not countries:
                    st.error("देशांची यादी मिळवण्यात अडचण आली. कृपया पुन्हा प्रयत्न करा.")
                else:
                    country = st.selectbox("देश निवडा", [name for name, code in countries])
                    country_code = next(code for name, code in countries if name == country)
                    intl_flights_only = st.radio("केवळ आंतरराष्ट्रीय विमानतळ समाविष्ट करायचे?", ("होय", "नाही"))
                    show_airports_button = st.button("विमानतळ दाखवा")
            except Exception as e:
                st.error(f"देशांची यादी मिळवताना त्रुटी आली: {str(e)}")
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
        airport_data = flight_search.get_airports_by_country(country_code, intl_flights_only == "Yes")
        
        if not airport_data.empty:
            st.write(f"Airports in {country} ({'International' if intl_flights_only == 'Yes' else 'All'})")
            page_size = st.selectbox("Entries per page", [10, 20, 50, 100, "All"], index=1)
            if page_size == "All":
                st.dataframe(airport_data)
            else:
                st.dataframe(airport_data.head(int(page_size)))
        else:
            st.write(f"No airports found for {country} ({'International' if intl_flights_only == 'Yes' else 'All'}).")
    elif search_type == "Do Nothing":
            st.info("Please select a search type from the dropdown menu.")

if __name__ == "__main__":
    main()