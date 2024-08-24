import pandas as pd
from amadeus import Client, ResponseError

class FlightSearch:
    def __init__(self, client_id, client_secret):
        """
        Initializes the Amadeus client with the provided credentials.
        """
        self.amadeus = Client(
            client_id=client_id,
            client_secret=client_secret
        )

    def get_airports_by_country(country, intl_flights_only):
        # This function would query a dataset or API to retrieve airports by country.
        # For simplicity, we'll use a placeholder for airport data.
        
        # Example placeholder data:
        airports = [
            {"Airport Code": "JFK", "City": "New York"},
            {"Airport Code": "LAX", "City": "Los Angeles"},
            {"Airport Code": "ORD", "City": "Chicago"},
            # Add more entries or query a real dataset...
        ]
        
        # Filter based on international flights if required
        if intl_flights_only == "Yes":
            airports = [airport for airport in airports if is_international_airport(airport['Airport Code'])]  # Placeholder for filter logic
        
        return pd.DataFrame(airports)

    def is_international_airport(airport_code):
        # Placeholder function to determine if an airport is international
        # You would implement real logic or queries here
        international_airports = ["JFK", "LAX", "ORD"]  # Example list
        return airport_code in international_airports
    
    def search_flights(self, origin, destination, departure_date, currency):
        """
        Searches for flights using the Amadeus API based on the provided parameters.
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
            raise Exception(f"Error searching flights: {error}")
    
    def convert_duration(self, duration_str):
        """
        Converts duration from ISO 8601 format to "XX:YY" string format.
        """
        hours = 0
        minutes = 0
        # Remove the 'PT' prefix
        duration = duration_str[2:]
        if 'H' in duration:
            hours_part, _, minutes_part = duration.partition('H')
            hours = int(hours_part)
            if 'M' in minutes_part:
                minutes = int(minutes_part.replace('M', ''))
        elif 'M' in duration:
            minutes = int(duration.replace('M', ''))
        # Format with zero-padding
        return f"{hours:02d}:{minutes:02d}"
    
    def calculate_halt_duration(self, arrival_time, departure_time):
        """
        Calculate the halt duration between two segments.
        """
        arrival_dt = pd.to_datetime(arrival_time)
        departure_dt = pd.to_datetime(departure_time)
        halt_duration = departure_dt - arrival_dt
        # Format halt duration as "HH:MM"
        return f"{halt_duration.components.hours:02}:{halt_duration.components.minutes:02}"
    
    def extract_flight_data(self, flights, max_stops):
        """
        Extracts relevant flight information from the API response and returns a pandas DataFrame.
        """
        flight_data = []
        index = 1  # To keep track of the itinerary index
        
        for flight in flights:
            stopovers = len(flight['itineraries'][0]['segments']) - 1
            if stopovers <= max_stops:
                price = float(flight['price']['total'])  # Numeric value for sorting
                currency = flight['price']['currency']
                
                for itinerary in flight['itineraries']:
                    segments = itinerary['segments']
                    total_duration_str = itinerary['duration']  # e.g., 'PT20H5M'
                    total_duration = self.convert_duration(total_duration_str)
                    
                    # Initialize lists and variables
                    airlines = []
                    connecting_cities = []
                    halt_durations = []
                    
                    for i, segment in enumerate(segments):
                        airline = segment['carrierCode']
                        flight_number = segment['number']
                        airlines.append(f"{airline} {flight_number}")
                        
                        if i > 0:  # Not the first segment
                            previous_arrival_time = segments[i-1]['arrival']['at']
                            current_departure_time = segment['departure']['at']
                            
                            # Calculate halt duration
                            halt_duration = self.calculate_halt_duration(previous_arrival_time, current_departure_time)
                            halt_durations.append(halt_duration)
                            
                            # Add the connecting city
                            connecting_cities.append(segment['departure']['iataCode'])
                    
                    # Get departure and arrival details
                    departure = segments[0]['departure']['iataCode']
                    departure_time = segments[0]['departure']['at']
                    arrival = segments[-1]['arrival']['iataCode']
                    arrival_time = segments[-1]['arrival']['at']
                    
                    # Create a row for the itinerary
                    flight_data.append({
                        'Index': index,
                        'Price': price,
                        'Airlines': ', '.join(airlines),
                        'Departure': departure,
                        'Arrival': arrival,
                        'Departure Time': departure_time,
                        'Arrival Time': arrival_time,
                        'Duration': total_duration,
                        'Connecting Cities': ', '.join(connecting_cities) if connecting_cities else '',
                        'Halts': ', '.join(halt_durations) if halt_durations else ''
                    })
                    
                    index += 1  # Increment the index for the next itinerary
        
        return pd.DataFrame(flight_data)
