import pandas as pd

adjacency_matrix = pd.read_csv('adjacency_matrix.csv', index_col=0)
routes_with_stop_sequences = pd.read_csv('final_unique_routes_with_stop_sequences.csv')

routes_with_stop_sequences.columns = routes_with_stop_sequences.columns.str.strip()

adjacency_matrix.index = adjacency_matrix.index.astype(str).str.strip()
adjacency_matrix.columns = adjacency_matrix.columns.astype(str).str.strip()

MAX_BUS_CAPACITY = 50  # Capacity of each bus
TOTAL_FLEET_SIZE = 500  # Available buses in the fleet

def assign_buses_to_routes(adjacency_matrix, routes_with_stop_sequences, max_capacity):
    bus_assignments = {}  # to store the number of buses needed per route
    total_passenger_flow_per_route = {}  # to store total passenger flow for each route

    for _, route in routes_with_stop_sequences.iterrows():
        route_no = route['route_no']  
        stops = [str(stop).strip() for stop in eval(route['stop_id'])]  

        print(f"\nCalculating for Route: {route_no}")
        print(f"Stops in Route: {stops}")

        total_passenger_flow = 0
        
        for i in range(len(stops) - 1):
            stop_a, stop_b = stops[i], stops[i + 1]
            if stop_a in adjacency_matrix.index and stop_b in adjacency_matrix.columns:
                flow = adjacency_matrix.loc[stop_a, stop_b]  
                total_passenger_flow += flow  
                print(f"Passenger flow from {stop_a} to {stop_b}: {flow}")
            else:
                print(f"Stops {stop_a} or {stop_b} not found in adjacency matrix")

        print(f"Total passenger flow for route {route_no}: {total_passenger_flow}")
        
        buses_needed = (total_passenger_flow // max_capacity) + (total_passenger_flow % max_capacity > 0)
        
        bus_assignments[route_no] = buses_needed
        total_passenger_flow_per_route[route_no] = total_passenger_flow

    return bus_assignments, total_passenger_flow_per_route

def normalize_bus_assignments(bus_assignments, total_passenger_flow_per_route, max_capacity, total_fleet_size):
    total_buses_needed = sum(bus_assignments.values())
    print(f"\nTotal buses initially needed: {total_buses_needed}")

    if total_buses_needed <= total_fleet_size:
        print("Fleet size is sufficient; no normalization needed.")
        return bus_assignments

    print("Fleet size insufficient. Normalizing passenger flows...")

    scaling_factor = total_fleet_size / total_buses_needed
    print(f"Scaling factor applied: {scaling_factor}")

    normalized_bus_assignments = {}
    for route_no, original_buses in bus_assignments.items():
        normalized_flow = total_passenger_flow_per_route[route_no] * scaling_factor
        print(f"Normalized passenger flow for route {route_no}: {normalized_flow}")
        
        normalized_buses_needed = (normalized_flow // max_capacity) + (normalized_flow % max_capacity > 0)
        normalized_bus_assignments[route_no] = normalized_buses_needed
        print(f"Route {route_no}: {normalized_buses_needed} bus(es) required after normalization")

    return normalized_bus_assignments

bus_assignments, total_passenger_flow_per_route = assign_buses_to_routes(adjacency_matrix, routes_with_stop_sequences, MAX_BUS_CAPACITY)

final_bus_assignments = normalize_bus_assignments(bus_assignments, total_passenger_flow_per_route, MAX_BUS_CAPACITY, TOTAL_FLEET_SIZE)

print("\nFinal bus assignments after considering fleet size:")
for route, buses in final_bus_assignments.items():
    print(f"Route {route}: {buses} bus(es) required")
