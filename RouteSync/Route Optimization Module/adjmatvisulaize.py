import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

# Load the Excel file and the relevant sheets
file_path = 'combined.xlsx'  # Replace with your file path
excel_data = pd.ExcelFile(file_path)
stop_times_df = excel_data.parse('stop_times')

# Sort stop_times by trip_id and stop_sequence to ensure consecutive stops are correctly ordered
stop_times_df_sorted = stop_times_df.sort_values(by=['trip_id', 'stop_sequence'])

# Create pairs of consecutive stops within each trip
stop_pairs = (
    stop_times_df_sorted
    .groupby('trip_id')
    .apply(lambda x: pd.DataFrame({
        'from_stop': x['stop_id'].values[:-1],
        'to_stop': x['stop_id'].values[1:]
    }))
    .reset_index(drop=True)
)

# Count the occurrences of each (from_stop, to_stop) pair
stop_pair_counts = stop_pairs.value_counts().reset_index(name='trip_count')

# Create a list of unique stops to build the adjacency matrix
unique_stops = stop_times_df['stop_id'].unique()
stop_to_index = {stop: idx for idx, stop in enumerate(unique_stops)}

# Initialize the adjacency matrix with zeros
n_stops = len(unique_stops)
adj_matrix = np.zeros((n_stops, n_stops), dtype=int)

# Populate the adjacency matrix with trip counts
for _, row in stop_pair_counts.iterrows():
    from_idx = stop_to_index[row['from_stop']]
    to_idx = stop_to_index[row['to_stop']]
    adj_matrix[from_idx, to_idx] = row['trip_count']

# Convert the adjacency matrix to a DataFrame for readability
adj_matrix_df = pd.DataFrame(adj_matrix, index=unique_stops, columns=unique_stops)
print(adj_matrix_df)
adj_matrix_df.to_csv('adjacency_matrix.csv')

# Create a directed graph using NetworkX
bus_graph = nx.DiGraph()

# Add edges with weights (trip counts) to the graph
for _, row in stop_pair_counts.iterrows():
    from_stop = row['from_stop']
    to_stop = row['to_stop']
    trip_count = row['trip_count']
    bus_graph.add_edge(from_stop, to_stop, weight=trip_count)

# Visualize the bus network graph
plt.figure(figsize=(12, 8))
pos = nx.spring_layout(bus_graph)  # positions for all nodes

# Draw nodes and edges
nx.draw_networkx_nodes(bus_graph, pos, node_size=700, node_color='lightblue', edgecolors='black')
nx.draw_networkx_edges(bus_graph, pos, edge_color='gray')

# Add labels to nodes (bus stops)
nx.draw_networkx_labels(bus_graph, pos, font_size=10, font_color='black')

# Edge labels with trip counts
edge_labels = {(u, v): f"{d['weight']}" for u, v, d in bus_graph.edges(data=True)}
nx.draw_networkx_edge_labels(bus_graph, pos, edge_labels=edge_labels, font_color='red', font_size=8)

# Title and show plot
plt.title("Bus Network Graph (Adjacency Between Stops)")
plt.xlabel("Bus Stops (Nodes)")
plt.ylabel("Number of Trips (Edges)")
plt.show()
