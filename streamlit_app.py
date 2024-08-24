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
        search_type = st.selectbox("शोध प्रकार निवडा", ["विमान शोध", "विमानतळ", "काहीही करू नका"])
        
        if search_type == "विमान शोध":
            origin = st.text_input("प्रारंभ स्थान", "LAX").upper()
            destination = st.text_input("गंतव्य स्थान", "JFK").upper()
            departure_date = st.date_input("प्रस्थान तारीख").strftime("%Y-%m-%d")
            max_stops = st.selectbox("कमाल थांबे", [0, 1, 2], index=1)
            currency = st.text_input("चलन कोड", "USD")
            search_button = st.button("विमाने शोधा")
        elif search_type == "विमानतळ":
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
        elif search_type == "काहीही करू नका":
            st.info("हा पर्याय भविष्यातील वैशिष्ट्यांसाठी प्लेसहोल्डर आहे.")
    
    # Display the selected currency in the main area
    if search_type == "विमान शोध":
        st.write(f"किंमती दर्शवत आहे: {currency}")
    
    # Handle flight search and display results
    if search_type == "विमान शोध" and search_button:
        try:
            flights = flight_search.search_flights(origin, destination, departure_date, currency)
            if flights:
                flight_data = flight_search.extract_flight_data(flights, max_stops)
                if not flight_data.empty:
                    # Display the DataFrame with proper sorting
                    st.dataframe(
                        flight_data.sort_values(by=["किंमत", "कालावधी"], ascending=[True, True]),
                        use_container_width=True
                    )
                else:
                    st.warning("निवडलेल्या थांब्यांच्या संख्येसह कोणतीही विमाने सापडली नाहीत.")
            else:
                st.warning("कोणतीही विमाने सापडली नाहीत.")
        except Exception as e:
            st.error(str(e))
    elif search_type == "विमानतळ" and show_airports_button:
        try:
            airports_df = flight_search.get_airports_by_country(country_code, intl_flights_only == "होय")
            st.dataframe(airports_df)
        except Exception as e:
            st.error(f"विमानतळांची माहिती मिळवताना त्रुटी आली: {str(e)}")
    elif search_type == "काहीही करू नका":
        st.info("कृपया ड्रॉपडाउन मेनूमधून शोध प्रकार निवडा.")

if __name__ == "__main__":
    main()