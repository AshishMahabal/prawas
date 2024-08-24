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
    
    def extract_flight_data(self,flights, max_stops):
        flight_data = []
        index = 1  # To keep track of the itinerary index
        
        for flight in flights:
            stopovers = len(flight['itineraries'][0]['segments']) - 1
            if stopovers <= max_stops:
                price = float(flight['price']['total'])  # Numeric value for sorting
                currency = flight['price']['currency']
                for itinerary in flight['itineraries']:
                    total_duration_str = itinerary['duration']  # e.g., 'PT20H5M'
                    total_duration = self.convert_duration(total_duration_str)
                    
                    for i, segment in enumerate(itinerary['segments']):
                        airline = segment['carrierCode']
                        flight_number = segment['number']
                        departure = segment['departure']['iataCode']
                        arrival = segment['arrival']['iataCode']
                        departure_time = segment['departure']['at']
                        arrival_time = segment['arrival']['at']
                        
                        # Add a row for each segment
                        flight_data.append({
                            'Index': index if i == 0 else '',  # Only display index for the first segment
                            'Price': price if i == 0 else '',  # Only display price for the first segment
                            'Airline': f"{airline} {flight_number}",
                            'Departure': departure,
                            'Arrival': arrival,
                            'Departure Time': departure_time,
                            'Arrival Time': arrival_time,
                            'Duration': total_duration if i == 0 else ''  # Only display total duration for the first segment
                        })
                    index += 1  # Increment the index for the next itinerary
        
        return pd.DataFrame(flight_data)
