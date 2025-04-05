import pandas as pd
import numpy as np
import networkx as nx

# Load the stop_times.csv file
file_path = 'stop_times.csv'  # Replace with your file path
stop_times_df = pd.read_csv(file_path)

# Sort stop_times by trip_id and stop_sequence
stop_times_df_sorted = stop_times_df.sort_values(by=['trip_id', 'stop_sequence'])

# Generate all reachable stop pairs within the same trip
def generate_all_stop_pairs(trip_data):
    stops = trip_data['stop_id'].values
    pairs = [
        (stops[i], stops[j])
        for i in range(len(stops)) for j in range(i + 1, len(stops))
    ]
    return pd.DataFrame(pairs, columns=['from_stop', 'to_stop'])

# Apply the function to each trip_id
all_stop_pairs = (
    stop_times_df_sorted.groupby('trip_id')
    .apply(generate_all_stop_pairs)
    .reset_index(drop=True)
)

# Count the occurrences of each (from_stop, to_stop) pair
all_stop_pair_counts = all_stop_pairs.value_counts().reset_index(name='trip_count')

# Create a mapping of stop_id to indices for the adjacency matrix
unique_stops = stop_times_df['stop_id'].unique()
stop_to_index = {stop: idx for idx, stop in enumerate(unique_stops)}

# Initialize the adjacency matrix with zeros
n_stops = len(unique_stops)
adj_matrix = np.zeros((n_stops, n_stops), dtype=int)

# Populate the adjacency matrix with trip counts for all stop pairs
for _, row in all_stop_pair_counts.iterrows():
    from_idx = stop_to_index[row['from_stop']]
    to_idx = stop_to_index[row['to_stop']]
    adj_matrix[from_idx, to_idx] = row['trip_count']

# Use Floyd-Warshall Algorithm to compute the transitive closure
for k in range(n_stops):
    for i in range(n_stops):
        for j in range(n_stops):
            if adj_matrix[i, k] > 0 and adj_matrix[k, j] > 0:
                adj_matrix[i, j] = max(adj_matrix[i, j], min(adj_matrix[i, k], adj_matrix[k, j]))

# Normalize the adjacency matrix to ensure no zeros
adj_matrix = np.where(adj_matrix > 0, adj_matrix, 1)  # Fill missing connections with minimal weight

# Convert the adjacency matrix to a DataFrame for better readability
adj_matrix_df = pd.DataFrame(adj_matrix, index=unique_stops, columns=unique_stops)

# Save the enhanced adjacency matrix to a CSV file
output_path = 'adjacency_matrix_fixed.csv'  # Replace with your desired output path
adj_matrix_df.to_csv(output_path)
print(f"Enhanced adjacency matrix saved to {output_path}")

# ---- Shortest Route Calculation ---- #

# Create a directed graph from the adjacency matrix with weights
graph = nx.from_numpy_array(adj_matrix, create_using=nx.DiGraph)

# Ensure the weights are correctly assigned
for u, v, data in graph.edges(data=True):
    data['weight'] = adj_matrix[u, v]  # Use the trip count as the weight

# Reverse mappings for user-friendly input/output
index_to_stop = {idx: stop for stop, idx in stop_to_index.items()}

# Function to calculate the shortest route between stops
def find_fastest_route(graph, stop_to_index, index_to_stop, origin_stop, destination_stop):
    # Convert user input to indices
    if origin_stop not in stop_to_index or destination_stop not in stop_to_index:
        raise ValueError("One or both stops are not valid stop IDs.")
    
    origin_idx = stop_to_index[origin_stop]
    destination_idx = stop_to_index[destination_stop]
    
    # Compute the shortest path using Dijkstra's algorithm with weights
    try:
        shortest_path_indices = nx.shortest_path(graph, source=origin_idx, target=destination_idx, weight='weight')
        shortest_path_stops = [index_to_stop[idx] for idx in shortest_path_indices]
        shortest_path_cost = nx.shortest_path_length(graph, source=origin_idx, target=destination_idx, weight='weight')
    except nx.NetworkXNoPath:
        return None, float('inf')  # No path exists

    return shortest_path_stops, shortest_path_cost

# Example user input
origin_stop =  57 # Replace with actual stop ID (integer)
destination_stop = 13  # Replace with actual stop ID (integer)

# Find and print the fastest route
try:
    fastest_route, route_cost = find_fastest_route(graph, stop_to_index, index_to_stop, origin_stop, destination_stop)
    if fastest_route:
        fastest_route_str = [str(stop) for stop in fastest_route]
        print("Fastest Route:", " -> ".join(fastest_route_str))
        print("Route Cost (trips):", route_cost)
    else:
        print(f"No route exists between {origin_stop} and {destination_stop}.")
except ValueError as e:
    print(e)
