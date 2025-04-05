import pandas as pd
import networkx as nx
from datetime import datetime, timedelta

# Function to convert HH:MM:SS string to a datetime object and handle times exceeding 24 hours
def parse_time(time_str):
    try:
        # Split the time into hours, minutes, and seconds
        hours, minutes, seconds = map(int, time_str.split(':'))
        
        # Normalize times greater than 24 hours
        if hours >= 24:
            day_offset = hours // 24
            hours = hours % 24
        else:
            day_offset = 0

        # Create the datetime object for the time
        time_obj = datetime.strptime(f"{hours:02}:{minutes:02}:{seconds:02}", "%H:%M:%S") + timedelta(days=day_offset)
        return time_obj
    except Exception as e:
        print(f"Error parsing time: {time_str}, Error: {e}")
        return None

# Load the stop_times data
file_path = 'stop_times.csv'  # Update with your file path
stop_times_df = pd.read_csv(file_path)

# Initialize directed graph
bus_graph = nx.DiGraph()

# Add edges (routes) between stops based on stop_times data
prev_stop = None
prev_departure = None
prev_trip_id = None

for index, row in stop_times_df.iterrows():
    current_stop = row['stop_id']
    current_arrival = str(row['arrival_time']).strip()
    current_departure = str(row['departure_time']).strip()
    current_trip_id = row['trip_id']

    # Convert arrival and departure times
    current_arrival_time = parse_time(current_arrival)
    current_departure_time = parse_time(current_departure)

    if current_arrival_time is None or current_departure_time is None:
        continue

    # Ensure both stops are part of the same trip
    if prev_trip_id == current_trip_id and prev_stop is not None:
        # Calculate travel time in seconds
        travel_time = (current_arrival_time - prev_departure).total_seconds()

        if travel_time >= 0:  # Ensure valid travel time
            bus_graph.add_edge(prev_stop, current_stop, weight=travel_time)

    # Update previous stop, departure, and trip ID for the next iteration
    prev_stop = current_stop
    prev_departure = current_departure_time
    prev_trip_id = current_trip_id

# Generate the travel time matrix
def create_travel_time_matrix(graph):
    # Get all bus stops (nodes) from the graph
    stops = list(graph.nodes())
    
    # Initialize a matrix (DataFrame) with stops as row and column labels
    travel_time_matrix = pd.DataFrame(index=stops, columns=stops, data=float('inf'))
    
    # Fill the matrix with travel times
    for u, v, data in graph.edges(data=True):
        travel_time_matrix.loc[u, v] = data['weight']
    
    # Set diagonal to 0 (travel time from a stop to itself is zero)
    for stop in stops:
        travel_time_matrix.loc[stop, stop] = 0
    
    return travel_time_matrix

# Create and display the travel time matrix
travel_time_matrix = create_travel_time_matrix(bus_graph)
print("Travel Time Matrix (in seconds):")
print(travel_time_matrix)

# Save the matrix to a CSV file
output_file = 'travel_time_matrix.csv'
travel_time_matrix.to_csv(output_file)
print(f"Travel time matrix saved to {output_file}")
