import pandas as pd
import numpy as np
import ast

def load_routes(route_file_path):
    """Load route data from CSV and parse stop lists."""
    routes = pd.read_csv(route_file_path)
    routes["stops"] = routes["stops"].apply(ast.literal_eval)  # Convert string to list
    return routes


def assign_unique_trip_ids(routes):
    """Assign unique trip IDs for each trip and prepare data for export."""
    trip_data = []

    for route_id, row in routes.iterrows():
        num_trips = row['buses_assigned']  # Ensure 'buses_assigned' is already present in the data
        for trip_num in range(num_trips):
            trip_id = f"{route_id}_{trip_num}"
            trip_data.append([
                route_id,              # route_id
                "weekday",            # service_id (static as 'weekday')
                trip_id,               # trip_id
                "",                    # trip_headsign
                "",                    # trip_short_name
                "",                    # direction_id
                "",                    # block_id
                f"shp_1_{route_id}",  # shape_id
                0,                      # wheelchair_accessible
                0                       # bikes_allowed
            ])

    # Create DataFrame and return
    columns = ["route_id", "service_id", "trip_id", "trip_headsign", "trip_short_name", "direction_id", "block_id", "shape_id", "wheelchair_accessible", "bikes_allowed"]
    return pd.DataFrame(trip_data, columns=columns)


def save_trip_data(trip_df, output_file):
    """Save the trip data to a CSV file."""
    trip_df.to_csv(output_file, index=False)
    print(f"Trip data saved to {output_file}")


def main():
    # File paths
    route_file_path = "output_routes_with_demand.csv"
    output_file = "new_trips.csv"

    # Load routes with assigned bus trips
    routes = load_routes(route_file_path)

    # Ensure that 'buses_assigned' is in the dataset for assigning trips
    if 'buses_assigned' not in routes.columns:
        print("Error: 'buses_assigned' column not found in route data.")
        return

    # Generate trip data
    trip_df = assign_unique_trip_ids(routes)

    # Save to CSV
    save_trip_data(trip_df, output_file)


if __name__ == "__main__":
    main()
