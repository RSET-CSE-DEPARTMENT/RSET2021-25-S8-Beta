import pandas as pd

# Load data
adjacency_matrix = pd.read_csv('adjacency_matrix.csv', index_col=0)
routes_with_stop_sequences = pd.read_csv('final_unique_routes_with_stop_sequences.csv')

# Clean up column names to remove any extra whitespace
routes_with_stop_sequences.columns = routes_with_stop_sequences.columns.str.strip()

# Ensure all indices and columns in adjacency_matrix are strings and stripped of whitespace
adjacency_matrix.index = adjacency_matrix.index.astype(str).str.strip()
adjacency_matrix.columns = adjacency_matrix.columns.astype(str).str.strip()

# Define bus capacity
MAX_BUS_CAPACITY = 50  # Adjust according to actual bus capacity

def assign_buses_to_routes(adjacency_matrix, routes_with_stop_sequences, max_capacity):
    # Dictionary to store bus assignments
    bus_assignments = {}

    # Loop through each route
    for _, route in routes_with_stop_sequences.iterrows():
        route_no = route['route_no']  # Get route number
        stops = [str(stop).strip() for stop in eval(route['stop_id'])]  # Ensure stops are strings and stripped

        print(f"\nCalculating for Route: {route_no}")
        print(f"Stops in Route: {stops}")

        # Initialize total passenger flow
        total_passenger_flow = 0
        
        # Calculate total passenger flow for the route
        for i in range(len(stops) - 1):
            stop_a, stop_b = stops[i], stops[i + 1]
            if stop_a in adjacency_matrix.index and stop_b in adjacency_matrix.columns:
                flow = adjacency_matrix.loc[stop_a, stop_b]
                total_passenger_flow += flow
                print(f"Passenger flow from {stop_a} to {stop_b}: {flow}")
            else:
                print(f"Stops {stop_a} or {stop_b} not found in adjacency matrix")

        print(f"Total passenger flow for route {route_no}: {total_passenger_flow}")
        
        # Calculate the number of buses required for this route
        buses_needed = (total_passenger_flow // max_capacity) + (total_passenger_flow % max_capacity > 0)
        bus_assignments[route_no] = buses_needed

    return bus_assignments

# Run the function to get bus assignments
bus_assignments = assign_buses_to_routes(adjacency_matrix, routes_with_stop_sequences, MAX_BUS_CAPACITY)

# Display the bus requirements for each route
for route, buses in bus_assignments.items():
    print(f"Route {route}: {buses} bus(es) required")
