import pandas as pd
from amadeus import Client, ResponseError

class FlightSearch:
    def __init__(self, client_id, client_secret):
        """
        Amadeus क्लायंटला दिलेल्या क्रेडेन्शियल्ससह प्रारंभ करते.
        """
        self.amadeus = Client(
            client_id=client_id,
            client_secret=client_secret
        )

    def get_countries(self):
        try:
            response = self.amadeus.reference_data.locations.countries.get()
            countries = [(country['name'], country['iataCode']) for country in response.data]
            return sorted(countries, key=lambda x: x[0])
        except ResponseError as error:
            print(f"देशांची यादी मिळवताना त्रुटी आली: {error}")
            return []

    def get_airports_by_country(self, country_code, intl_flights_only=False):
        try:
            response = self.amadeus.reference_data.locations.get(
                keyword=country_code,
                subType=amadeus.location.AIRPORT,
                page={'limit': 100}  # जास्तीत जास्त 100 विमानतळ मिळवा
            )
            airports = []
            for airport in response.data:
                if not intl_flights_only or airport.get('internationalAirport', False):
                    airports.append({
                        "विमानतळ कोड": airport['iataCode'],
                        "नाव": airport['name'],
                        "शहर": airport['address'].get('cityName', 'N/A'),
                        "आंतरराष्ट्रीय": "होय" if airport.get('internationalAirport', False) else "नाही"
                    })
            return pd.DataFrame(airports)
        except ResponseError as error:
            print(f"विमानतळांची माहिती मिळवताना त्रुटी आली: {error}")
            return pd.DataFrame()
    
    def search_flights(self, origin, destination, departure_date, currency):
        """
        दिलेल्या मापदंडांच्या आधारे Amadeus API वापरून विमाने शोधते.
        """
        try:
            response = self.amadeus.shopping.flight_offers_search.get(
                originLocationCode=origin,
                destinationLocationCode=destination,
                departureDate=departure_date,
                adults=1,
                currencyCode=currency
            )
            return response.data
        except ResponseError as error:
            raise Exception(f"विमाने शोधताना त्रुटी आली: {error}")
    
    def convert_duration(self, duration_str):
        """
        कालावधीला ISO 8601 स्वरूपातून "XX:YY" स्ट्रिंग स्वरूपात रूपांतरित करते.
        """
        hours = 0
        minutes = 0
        duration = duration_str[2:]  # 'PT' उपसर्ग काढून टाकतो
        if 'H' in duration:
            hours_part, _, minutes_part = duration.partition('H')
            hours = int(hours_part)
            if 'M' in minutes_part:
                minutes = int(minutes_part.replace('M', ''))
        elif 'M' in duration:
            minutes = int(duration.replace('M', ''))
        return f"{hours:02d}:{minutes:02d}"
    
    def calculate_halt_duration(self, arrival_time, departure_time):
        """
        दोन सेगमेंट्समधील थांबण्याचा कालावधी गणना करते.
        """
        arrival_dt = pd.to_datetime(arrival_time)
        departure_dt = pd.to_datetime(departure_time)
        halt_duration = departure_dt - arrival_dt
        return f"{halt_duration.components.hours:02}:{halt_duration.components.minutes:02}"
    
    def extract_flight_data(self, flights, max_stops):
        """
        API प्रतिसादातून संबंधित विमान माहिती काढते आणि pandas DataFrame परत करते.
        """
        flight_data = []
        index = 1
        
        for flight in flights:
            stopovers = len(flight['itineraries'][0]['segments']) - 1
            if stopovers <= max_stops:
                price = float(flight['price']['total'])
                currency = flight['price']['currency']
                
                for itinerary in flight['itineraries']:
                    segments = itinerary['segments']
                    total_duration = self.convert_duration(itinerary['duration'])
                    
                    airlines = []
                    connecting_cities = []
                    halt_durations = []
                    
                    for i, segment in enumerate(segments):
                        airline = segment['carrierCode']
                        flight_number = segment['number']
                        airlines.append(f"{airline} {flight_number}")
                        
                        if i > 0:
                            previous_arrival_time = segments[i-1]['arrival']['at']
                            current_departure_time = segment['departure']['at']
                            
                            halt_duration = self.calculate_halt_duration(previous_arrival_time, current_departure_time)
                            halt_durations.append(halt_duration)
                            
                            connecting_cities.append(segment['departure']['iataCode'])
                    
                    departure = segments[0]['departure']['iataCode']
                    departure_time = segments[0]['departure']['at']
                    arrival = segments[-1]['arrival']['iataCode']
                    arrival_time = segments[-1]['arrival']['at']
                    
                    flight_data.append({
                        'क्रमांक': index,
                        'किंमत': price,
                        'विमान कंपन्या': ', '.join(airlines),
                        'प्रस्थान': departure,
                        'आगमन': arrival,
                        'प्रस्थान वेळ': departure_time,
                        'आगमन वेळ': arrival_time,
                        'कालावधी': total_duration,
                        'जोडणारी शहरे': ', '.join(connecting_cities) if connecting_cities else '',
                        'थांबे': ', '.join(halt_durations) if halt_durations else ''
                    })
                    
                    index += 1
        
        return pd.DataFrame(flight_data)