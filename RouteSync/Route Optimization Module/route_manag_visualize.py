import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load data files
routes_file = "final_unique_routes_with_stop_sequences.csv"
adjacency_matrix_file = "adjacency_matrix_fixed.csv"
stops_file = "stops.csv"

routes = pd.read_csv(routes_file)
adjacency_matrix = pd.read_csv(adjacency_matrix_file, header=None).to_numpy()
stops = pd.read_csv(stops_file)

# Dijkstra's Algorithm
def dijkstra(weight_matrix, src, dest):
    n = len(weight_matrix)
    dist = [float('inf')] * n
    prev = [-1] * n
    visited = [False] * n

    dist[src] = 0

    for _ in range(n):
        u = min((dist[i], i) for i in range(n) if not visited[i])[1]
        visited[u] = True

        for v in range(n):
            if weight_matrix[u][v] != float('inf') and not visited[v]:
                alt = dist[u] + weight_matrix[u][v]
                if alt < dist[v]:
                    dist[v] = alt
                    prev[v] = u

    path = []
    u = dest
    while u != -1:
        path.insert(0, u)
        u = prev[u]

    return path

# Find alternative routes
def find_alternative_routes(routes, weight_matrix):
    alternative_routes = []

    for _, route in routes.iterrows():
        stop_sequence = list(map(int, route['stop_id']))  # Already processed as a list
        alternative_route = []

        for i in range(len(stop_sequence) - 1):
            src = stop_sequence[i] - 1  # Adjust for 0-based indexing
            dest = stop_sequence[i + 1] - 1
            path = dijkstra(weight_matrix, src, dest)
            if alternative_route and alternative_route[-1] == path[0]:
                alternative_route.extend(path[1:])
            else:
                alternative_route.extend(path)

        alternative_routes.append(alternative_route)

    return alternative_routes

# Visualization
def visualize_routes(routes, alternative_routes, stops):
    plt.figure(figsize=(12, 8))

    # Map stop IDs to lat/lon
    stop_coords = {row['stop_id']: (row['stop_lat'], row['stop_lon']) for _, row in stops.iterrows()}

    # Plot original routes
    for _, route in routes.iterrows():
        stop_sequence = list(map(int, route['stop_id'].split(',')))
        lats = [stop_coords[stop][0] for stop in stop_sequence]
        lons = [stop_coords[stop][1] for stop in stop_sequence]
        plt.plot(lons, lats, label='Original Route', color='blue', alpha=0.6, linestyle='--')

    # Plot alternative routes
    for alt_route in alternative_routes:
        lats = [stop_coords[stop + 1][0] for stop in alt_route]  # Adjust for 1-based IDs
        lons = [stop_coords[stop + 1][1] for stop in alt_route]
        plt.plot(lons, lats, label='Alternative Route', color='red', alpha=0.8)

    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('Route Visualization: Original vs Alternative Routes')
    plt.legend()
    plt.grid(True)
    plt.show()

# Main Execution
routes['stop_id'] = routes['stop_id'].apply(lambda x: x.strip('[]').split(','))  # Process stop IDs
alternative_routes = find_alternative_routes(routes, adjacency_matrix)
visualize_routes(routes, alternative_routes, stops)
