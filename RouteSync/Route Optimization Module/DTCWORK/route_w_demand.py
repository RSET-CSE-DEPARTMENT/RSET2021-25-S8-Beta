import pandas as pd
import numpy as np
import ast

def create_stop_mapping(routes):
    """Create mappings between stop IDs and indices."""
    stop_ids = set()
    for stop_sequence in routes["stops"]:
        stop_ids.update(stop_sequence)

    stop_ids = sorted(stop_ids)
    stop_id_to_index = {stop_id: idx for idx, stop_id in enumerate(stop_ids)}
    index_to_stop_id = {idx: stop_id for stop_id, idx in stop_id_to_index.items()}
    return stop_id_to_index, index_to_stop_id

def load_data(matrix_path, route_file_path):
    """Load the passenger demand matrix and route data."""
    # Load the shortest path matrix
    demand_matrix = pd.read_csv(matrix_path, header=None).values

    # Load route data
    routes = pd.read_csv(route_file_path)
    routes["stops"] = routes["stops"].apply(ast.literal_eval)  # Convert string to list

    return demand_matrix, routes

def calculate_total_demand(routes, demand_matrix, stop_id_to_index):
    """Calculate the total passenger demand for each route."""
    total_demand = []

    for _, row in routes.iterrows():
        stop_sequence = [stop_id_to_index[stop] for stop in row["stops"]]
        demand = 0

        # Iterate over all pairs of consecutive stops in the route
        for i in range(len(stop_sequence) - 1):
            src, dest = stop_sequence[i], stop_sequence[i + 1]
            try:
                value = demand_matrix[src, dest]  # Use mapped indices
                if np.isfinite(value):  # Ignore `inf` or invalid values
                    demand += value
            except IndexError:
                print(f"Index out of bounds for stops {src} -> {dest}")

        total_demand.append(demand)

    routes["total_demand"] = total_demand
    return routes

def assign_buses(routes, bus_capacity, total_trips_required):
    """Assign the number of buses required for each route based on total demand."""
    total_demand_sum = routes["total_demand"].sum()
    if total_demand_sum == 0:
        print("Total demand is zero, cannot assign trips.")
        return routes

    # Calculate the trip multiplier dynamically
    trip_multiplier = total_trips_required / (total_demand_sum / bus_capacity)
    print(f"Calculated Trip Multiplier: {trip_multiplier:.4f}")
    
    # Assign buses based on the calculated multiplier
    adjusted_demand = routes["total_demand"] * trip_multiplier
    routes["buses_assigned"] = np.ceil(adjusted_demand / bus_capacity).astype(int)

    # Print route and number of trips
    total_trips = routes["buses_assigned"].sum()
    for _, row in routes.iterrows():
        print(f"Route: {row['stops']}, Buses Assigned: {row['buses_assigned']}")
    
    print(f"Total Number of Trips Assigned: {total_trips}")
    return routes

def main():
    # File paths
    matrix_path = "shortest_path_matrix.csv"
    route_file_path = "route_stop_mapping.csv"
    
    # Parameters
    bus_capacity = 50
    total_trips_required = 5439  # Define the total trips required
    
    # Load data
    demand_matrix, routes = load_data(matrix_path, route_file_path)
    
    # Create mappings
    stop_id_to_index, index_to_stop_id = create_stop_mapping(routes)
    
    # Calculate total demand
    routes = calculate_total_demand(routes, demand_matrix, stop_id_to_index)
    
    # Assign buses dynamically
    routes = assign_buses(routes, bus_capacity, total_trips_required)
    
    # Save results
    output_path = "output_routes_with_demand.csv"
    routes.to_csv(output_path, index=False)
    print(f"Results saved to {output_path}")

if __name__ == "__main__":
    main()