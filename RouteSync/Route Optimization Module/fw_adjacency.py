import pandas as pd
import numpy as np

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

# Initialize the adjacency matrix with infinity (representing no direct connection)
n_stops = len(unique_stops)
adj_matrix = np.full((n_stops, n_stops), float('inf'))

# Populate the adjacency matrix with trip counts
for _, row in stop_pair_counts.iterrows():
    from_idx = stop_to_index[row['from_stop']]
    to_idx = stop_to_index[row['to_stop']]
    adj_matrix[from_idx, to_idx] = row['trip_count']

# Convert diagonal to 0 (self-loop has zero cost)
np.fill_diagonal(adj_matrix, 0)

# Floyd-Warshall algorithm to compute shortest paths between all pairs of stops
def floyd_warshall(adj_matrix):
    dist = adj_matrix.copy()
    n = len(dist)
    
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i, k] + dist[k, j] < dist[i, j]:
                    dist[i, j] = dist[i, k] + dist[k, j]
    return dist

# Calculate the shortest path matrix using Floyd-Warshall
shortest_path_matrix = floyd_warshall(adj_matrix)

# Convert the shortest path matrix to a DataFrame for readability
shortest_path_matrix_df = pd.DataFrame(
    shortest_path_matrix,
    index=unique_stops,
    columns=unique_stops
)

# Save the shortest path matrix to a CSV file
shortest_path_matrix_df.to_csv('shortest_path_matrix.csv')

# Normalize the shortest path matrix to range [0, 1]
def normalize_matrix(matrix):
    # Replace infinity values with NaN for normalization
    matrix = np.where(np.isinf(matrix), np.nan, matrix)
    
    # Find the min and max values, ignoring NaN
    min_val = np.nanmin(matrix)
    max_val = np.nanmax(matrix)
    
    # Apply normalization formula
    normalized_matrix = (matrix - min_val) / (max_val - min_val)
    
    # Replace NaN back with infinity (if needed)
    normalized_matrix = np.where(np.isnan(normalized_matrix), float('inf'), normalized_matrix)
    
    return normalized_matrix

# Normalize the shortest path matrix
normalized_shortest_path_matrix = normalize_matrix(shortest_path_matrix)

# Convert the normalized matrix to a DataFrame for readability
normalized_shortest_path_matrix_df = pd.DataFrame(
    normalized_shortest_path_matrix,
    index=unique_stops,
    columns=unique_stops
)

# Save the normalized shortest path matrix to a CSV file
normalized_shortest_path_matrix_df.to_csv('normalized_shortest_path_matrix.csv')

# Display both matrices
print("Shortest Path Matrix:")
print(shortest_path_matrix_df)
print("\nNormalized Shortest Path Matrix:")
print(normalized_shortest_path_matrix_df)
