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
            currency = st.text_input("चलन को", "USD")
            search_button = st.button("विमाने शोधा")
        elif search_type == "विमानतळ":
            country_selection_method = st.radio(
                "देश निवडण्याची पद्धत",
                ("प्रमुख देशांमधून निवडा", "देशाचे नाव प्रविष्ट करा")
            )

            if country_selection_method == "प्रमुख देशांमधून निवडा":
                main_countries = {
                    "भारत": "IN",
                    "कॅनडा": "CA",
                    "युनायटेड स्टेट्स": "US"
                }
                selected_country = st.selectbox("देश निवडा", list(main_countries.keys()))
                country_code = main_countries[selected_country]
            else:
                country_name = st.text_input("देशाचे नाव प्रविष्ट करा")
                country_code = country_name[:2].upper() if country_name else ""

            intl_flights_only = st.radio("केवळ आंतरराष्ट्रीय विमानतळ समाविष्ट करायचे?", ("होय", "नाही"))
            show_airports_button = st.button("विमानतळ दाखवा")
        elif search_type == "काहीही करू नका":
            st.info("हा पर्याय भविष्यातील वैशिष्ट्यांसाठी प्लेसहोल्र आहे.")
    
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
    elif search_type == "वि���ानतळ" and show_airports_button:
        if country_code:
            try:
                airports_df = flight_search.get_airports_by_country(country_code, intl_flights_only == "होय")
                if not airports_df.empty:
                    st.dataframe(airports_df)
                else:
                    st.warning(f"निवडलेल्या देशासाठी कोणतेही विमानतळ सापडले नाही.")
            except Exception as e:
                st.error(f"विमानतळांची माहिती मिळवताना त्रुटी आली: {str(e)}")
        else:
            st.warning("कृपया वैध देश निवडा किंवा प्रविष्ट करा.")
    elif search_type == "काहीही करू नका":
        st.info("कृपया ड्रॉपडाउन मेनूमधून शोध प्रकार निवडा.")

if __name__ == "__main__":
    main()