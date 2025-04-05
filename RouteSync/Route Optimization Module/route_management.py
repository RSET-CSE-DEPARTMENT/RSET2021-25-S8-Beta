import pandas as pd
import numpy as np
import ast  # To parse stringified lists in the routes file

def load_data():
    # Paths to input files
    normalized_time_matrix_path = "normalized_travel_time_matrix.csv"
    adjacency_matrix_path = "normalized_shortest_path_matrix.csv"
    routes_path = "final_unique_routes_with_stop_sequences.csv"

    # Load normalized travel time matrix
    normalized_time_matrix = pd.read_csv(normalized_time_matrix_path, index_col=0)

    # Load adjacency matrix
    adjacency_matrix = pd.read_csv(adjacency_matrix_path, index_col=0)

    # Load routes file and parse stop_id lists
    routes = pd.read_csv(routes_path)
    routes["stop_id"] = routes["stop_id"].apply(ast.literal_eval)

    return normalized_time_matrix, adjacency_matrix, routes

def map_stop_ids(adjacency_matrix, routes):
    """
    Map stop IDs in the routes file to indices in the adjacency matrix.
    """
    stop_id_to_index = {stop_id: idx for idx, stop_id in enumerate(adjacency_matrix.index)}
    index_to_stop_id = {idx: stop_id for stop_id, idx in stop_id_to_index.items()}

    # Map the stop_id sequences in routes to matrix indices
    routes["stop_id"] = routes["stop_id"].apply(
        lambda stop_sequence: [stop_id_to_index[stop] for stop in stop_sequence if stop in stop_id_to_index]
    )

    return routes, stop_id_to_index, index_to_stop_id

def compute_weight_matrix(normalized_time_matrix, adjacency_matrix, bus_capacity, alpha):
    """
    Compute the weighted cost matrix combining crowding and normalized travel time.
    """
    n = adjacency_matrix.shape[0]
    weight_matrix = np.full((n, n), np.inf)  # Initialize with infinity

    for i, row in enumerate(adjacency_matrix.index):
        for j, col in enumerate(adjacency_matrix.columns):
            trips = adjacency_matrix.loc[row, col]
            normalized_time = normalized_time_matrix.loc[row, col]

            if trips > 0 and not np.isinf(normalized_time):
                crowding_factor = trips / bus_capacity
                weight_matrix[i, j] = normalized_time + alpha * crowding_factor

    return weight_matrix

def find_alternative_routes(routes, weight_matrix):
    """
    Generate alternative routes using the weight matrix.
    """
    def dijkstra(weight_matrix, src, dest):
        n = weight_matrix.shape[0]
        dist = np.full(n, np.inf)
        prev = np.full(n, -1)
        dist[src] = 0

        visited = set()
        while len(visited) < n:
            # Find the unvisited node with the smallest distance
            u = np.argmin([dist[i] if i not in visited else np.inf for i in range(n)])
            if u in visited or dist[u] == np.inf:
                break

            visited.add(u)

            for v in range(n):
                if weight_matrix[u, v] < np.inf and v not in visited:
                    new_dist = dist[u] + weight_matrix[u, v]
                    if new_dist < dist[v]:
                        dist[v] = new_dist
                        prev[v] = u

        # Reconstruct the path
        path = []
        current = dest
        while current != -1:
            path.append(current)
            current = prev[current]

        return path[::-1]  # Return reversed path

    alternative_routes = []

    for _, route in routes.iterrows():
        stop_sequence = route["stop_id"]
        new_route = []

        for i in range(len(stop_sequence) - 1):
            src = stop_sequence[i]
            dest = stop_sequence[i + 1]

            # Find shortest path for this segment
            path = dijkstra(weight_matrix, src, dest)
            new_route.extend(path[:-1])  # Exclude last stop to avoid duplication

        new_route.append(stop_sequence[-1])  # Add the final stop
        alternative_routes.append(new_route)

    return alternative_routes

# Main Execution
if __name__ == "__main__":
    # Load data
    normalized_time_matrix, adjacency_matrix, routes = load_data()

    # Map stop IDs to indices
    routes, stop_id_to_index, index_to_stop_id = map_stop_ids(adjacency_matrix, routes)

    # Parameters
    BUS_CAPACITY = 50
    ALPHA = 0.5

    # Compute weight matrix
    weight_matrix = compute_weight_matrix(normalized_time_matrix, adjacency_matrix, BUS_CAPACITY, ALPHA)

    # Find alternative routes
    alternative_routes = find_alternative_routes(routes, weight_matrix)

    # Output alternative routes (convert indices back to stop IDs)
    for i, alt_route in enumerate(alternative_routes):
        readable_route = [index_to_stop_id[idx] for idx in alt_route]
        print(f"Alternative Route {i + 1}: {readable_route}")
