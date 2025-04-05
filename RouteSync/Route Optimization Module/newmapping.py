import pandas as pd

# File paths
trips_file_path = "trips.csv"
trip_stop_mapping_file_path = "trip_stop_mapping.csv"
output_file_path = "route_stop_mapping.csv"

# Load the data
trips = pd.read_csv(trips_file_path)
trip_stop_mapping = pd.read_csv(trip_stop_mapping_file_path)

# Merge the datasets on trip_id to associate route_id with stop_id
merged_data = pd.merge(trip_stop_mapping, trips[['trip_id', 'route_id']], on='trip_id')

# Group by route_id and combine stop lists into unique sets
def process_stops(stop_list):
    # Flatten and deduplicate stops, regardless of their initial format
    flat_list = []
    for stops in stop_list:
        if isinstance(stops, str):  # Handle string representation of lists
            try:
                stops = eval(stops)
            except Exception as e:
                print(f"Skipping invalid entry: {stops}")
                continue
        if isinstance(stops, list):
            flat_list.extend(stops)
        else:
            flat_list.append(stops)
    return sorted(set(flat_list))

route_stop_mapping = (
    merged_data.groupby('route_id')['stop_id']
    .apply(process_stops)
    .reset_index()
)

# Rename columns for clarity
route_stop_mapping.columns = ['route_id', 'stops']

# Save the result to a CSV file
route_stop_mapping.to_csv(output_file_path, index=False)

print(f"Route-stop mapping saved to {output_file_path}")
