import pandas as pd
import numpy as np
import math
from itertools import combinations

# Vectorized Haversine formula using NumPy
def haversine_vectorized(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    # Earth radius in kilometers
    radius = 6371.0
    return radius * c

# Function to generate Haversine distances in batches and append to a CSV
def generate_haversine_distance_csv_in_batches(stops_df, output_filename="haversine_distances.csv", batch_size=10000):
    print("Starting Haversine distance computation...")

    # Extract relevant data into a list of tuples
    stops_data = stops_df[['stop_id', 'stop_lat', 'stop_lon']].values

    # Generate all unique pairs of stops
    stop_pairs = np.array([
        (stop1[0], stop1[1], stop1[2], stop2[0], stop2[1], stop2[2])
        for stop1, stop2 in combinations(stops_data, 2)
    ])

    total_pairs = len(stop_pairs)
    print(f"Total pairs to process: {total_pairs}")

    # Write the CSV header
    with open(output_filename, 'w') as f:
        f.write("stop_id_1,stop_id_2,distance_km\n")
    print(f"CSV file initialized: {output_filename}")

    # Process pairs in batches
    for i in range(0, total_pairs, batch_size):
        print(f"Processing batch {i // batch_size + 1}...")
        batch_pairs = stop_pairs[i:i + batch_size]
        lat1, lon1 = batch_pairs[:, 1], batch_pairs[:, 2]
        lat2, lon2 = batch_pairs[:, 4], batch_pairs[:, 5]

        # Compute distances for the batch
        distances = haversine_vectorized(lat1, lon1, lat2, lon2)

        # Create a DataFrame for the batch
        batch_df = pd.DataFrame({
            'stop_id_1': batch_pairs[:, 0],
            'stop_id_2': batch_pairs[:, 3],
            'distance_km': distances
        })

        # Append the batch to the CSV file
        batch_df.to_csv(output_filename, mode='a', header=False, index=False)
        print(f"Batch {i // batch_size + 1} processed and appended to CSV.")

    print(f"Haversine distance CSV generation completed: {output_filename}")

# Function to import the stops data from a file (stops.txt)
def import_stops_data(filename="All_Data/stops.txt"):
    print(f"Loading stops data from: {filename}")
    stops_df = pd.read_csv(filename)
    print(f"Loaded {len(stops_df)} stops from the file.")
    return stops_df

# Example usage:
if __name__ == "__main__":
    # Import stops data from 'stops.txt'
    stops_df = import_stops_data("All_Data/stops.txt")

    # Generate the Haversine distance CSV file in batches
    generate_haversine_distance_csv_in_batches(stops_df, "haversine_distances.csv", batch_size=10000)
