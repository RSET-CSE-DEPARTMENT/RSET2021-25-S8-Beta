import pandas as pd
import networkx as nx
from datetime import datetime, timedelta

# Load the stop_times data
file_path = 'stop_times.csv'
stop_times_df = pd.read_csv(file_path)

# Initialize directed graph
bus_graph = nx.DiGraph()

# Function to convert HH:MM:SS string to a datetime object and handle "1 day" cases
def parse_time(time_str):
    try:
        if "day" in time_str:
            # Handle the "1 day, HH:MM:SS" format
            days, time_part = time_str.split(", ")
            day_offset = int(days.split()[0])  # Extract the day count
            time_obj = datetime.strptime(time_part, '%H:%M:%S') + timedelta(days=day_offset)
        else:
            # Normal time in HH:MM:SS format
            time_obj = datetime.strptime(time_str, '%H:%M:%S')
        return time_obj
    except Exception as e:
        print(f"Error parsing time: {time_str}, Error: {e}")
        return None

# Add edges (routes) between stops based on stop_times data
prev_stop = None
prev_departure = None
prev_trip_id = None

for index, row in stop_times_df.iterrows():
    current_stop = row['stop_id']
    
    current_arrival = str(row['arrival_time']).strip()
    current_departure = str(row['departure_time']).strip()
    current_trip_id = row['trip_id']

    # Print the current trip ID and times for debugging
    print(f"Processing row {index} - Trip ID: {current_trip_id}, Arrival: {current_arrival}, Departure: {current_departure}")

    # Convert arrival and departure times
    current_arrival_time = parse_time(current_arrival)
    current_departure_time = parse_time(current_departure)

    if current_arrival_time is None or current_departure_time is None:
        print(f"Skipping row {index} due to time parsing issue")
        continue

    # Ensure both stops are part of the same trip
    if prev_trip_id == current_trip_id and prev_stop is not None:
        # Calculate travel time by subtracting the departure time of the previous stop from the arrival time of the current stop
        travel_time = (current_arrival_time - prev_departure).total_seconds()

        if travel_time >= 0:  # Ensure valid travel time
            bus_graph.add_edge(prev_stop, current_stop, weight=travel_time)
            print(f"Added edge from stop {prev_stop} to stop {current_stop} with travel time {travel_time} seconds")

    # Update previous stop, departure, and trip ID for the next iteration
    prev_stop = current_stop
    prev_departure = current_departure_time
    prev_trip_id = current_trip_id

# Check the number of nodes and edges created in the graph
print(f"Number of bus stops (nodes): {len(bus_graph.nodes())}")
print(f"Number of bus routes (edges): {len(bus_graph.edges())}")

# Example to display the created graph (optional)
for edge in bus_graph.edges(data=True):
    print(edge)
