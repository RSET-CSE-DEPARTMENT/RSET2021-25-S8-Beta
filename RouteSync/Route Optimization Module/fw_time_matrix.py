import pandas as pd
import networkx as nx
from datetime import datetime, timedelta

# Parse time and handle cases where hours exceed 24
def parse_time(time_str):
    try:
        hours, minutes, seconds = map(int, time_str.split(':'))
        if hours >= 24:
            day_offset = hours // 24
            hours = hours % 24
        else:
            day_offset = 0
        time_obj = datetime.strptime(f"{hours:02}:{minutes:02}:{seconds:02}", "%H:%M:%S") + timedelta(days=day_offset)
        return time_obj
    except Exception as e:
        print(f"Error parsing time: {time_str}, Error: {e}")
        return None

# Load the stop_times data
file_path = 'stop_times.csv'  # Update with your file path
print("Loading stop_times data...")
stop_times_df = pd.read_csv(file_path)
print("stop_times data loaded successfully.")

# Initialize directed graph
print("Initializing directed graph...")
bus_graph = nx.DiGraph()

# Add edges (routes) between stops based on stop_times data
print("Building the graph from stop_times data...")
prev_stop = None
prev_departure = None
prev_trip_id = None

for index, row in stop_times_df.iterrows():
    current_stop = row['stop_id']
    current_arrival = str(row['arrival_time']).strip()
    current_departure = str(row['departure_time']).strip()
    current_trip_id = row['trip_id']

    current_arrival_time = parse_time(current_arrival)
    current_departure_time = parse_time(current_departure)

    if current_arrival_time is None or current_departure_time is None:
        continue

    if prev_trip_id == current_trip_id and prev_stop is not None:
        travel_time = (current_arrival_time - prev_departure).total_seconds()
        if travel_time >= 0:
            bus_graph.add_edge(prev_stop, current_stop, weight=travel_time)

    prev_stop = current_stop
    prev_departure = current_departure_time
    prev_trip_id = current_trip_id

print("Graph built successfully with nodes and edges.")

# Generate the travel time matrix
def create_travel_time_matrix(graph):
    print("Creating initial travel time matrix...")
    stops = list(graph.nodes())
    travel_time_matrix = pd.DataFrame(float('inf'), index=stops, columns=stops)

    for stop in stops:
        travel_time_matrix.loc[stop, stop] = 0  # Travel time from a stop to itself is 0

    for u, v, data in graph.edges(data=True):
        travel_time_matrix.loc[u, v] = data['weight']

    print("Initial travel time matrix created.")
    return travel_time_matrix

# Floyd-Warshall algorithm to compute shortest paths for all pairs of nodes
def floyd_warshall(matrix):
    print("Running Floyd-Warshall algorithm...")
    stops = matrix.index
    for k in stops:
        print(f"Processing intermediate stop: {k}")
        for i in stops:
            for j in stops:
                current_value = matrix.loc[i, j]
                new_value = matrix.loc[i, k] + matrix.loc[k, j]
                matrix.loc[i, j] = min(current_value, new_value)
    print("Floyd-Warshall algorithm completed.")
    return matrix

# Normalize the travel time matrix to a range of [0, 1]
def normalize_matrix(matrix):
    print("Normalizing the travel time matrix...")
    # Replace infinity values with NaN for normalization
    matrix = matrix.replace(float('inf'), pd.NA)

    # Calculate min and max values, ignoring NaN
    min_val = matrix.min().min()
    max_val = matrix.max().max()

    # Apply normalization
    normalized_matrix = (matrix - min_val) / (max_val - min_val)

    # Replace NaN back with infinity
    normalized_matrix = normalized_matrix.fillna(float('inf'))
    print("Normalization completed.")
    return normalized_matrix

# Create the initial travel time matrix
travel_time_matrix = create_travel_time_matrix(bus_graph)
print("Initial Travel Time Matrix (direct connections only):")
print(travel_time_matrix)

# Apply Floyd-Warshall to fill in all parts of the matrix
complete_travel_time_matrix = floyd_warshall(travel_time_matrix)
print("Complete Travel Time Matrix (all connections):")
print(complete_travel_time_matrix)

# Normalize the travel time matrix
normalized_travel_time_matrix = normalize_matrix(complete_travel_time_matrix)
print("Normalized Travel Time Matrix:")
print(normalized_travel_time_matrix)

# Save the complete and normalized matrices to CSV files
output_file_complete = 'complete_travel_time_matrix.csv'
output_file_normalized = 'normalized_travel_time_matrix.csv'

print(f"Saving complete travel time matrix to {output_file_complete}...")
complete_travel_time_matrix.to_csv(output_file_complete)
print(f"Complete travel time matrix saved to {output_file_complete}.")

print(f"Saving normalized travel time matrix to {output_file_normalized}...")
normalized_travel_time_matrix.to_csv(output_file_normalized)
print(f"Normalized travel time matrix saved to {output_file_normalized}.")

print("Process completed successfully.")
