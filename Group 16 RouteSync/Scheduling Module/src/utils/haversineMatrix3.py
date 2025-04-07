import pandas as pd
import numpy as np
import math
from itertools import combinations
from multiprocessing import Pool, cpu_count

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

# Compute distances for a chunk of stop pairs
def compute_distances_chunk(chunk):
    stop_pairs = np.array(chunk)
    lat1, lon1 = stop_pairs[:, 1], stop_pairs[:, 2]
    lat2, lon2 = stop_pairs[:, 4], stop_pairs[:, 5]

    distances = haversine_vectorized(lat1, lon1, lat2, lon2)
    results = [
        [stop_pairs[i, 0], stop_pairs[i, 3], distances[i]]
        for i in range(len(stop_pairs))
    ]
    return results

# Function to generate the Haversine distance CSV in parallel
def generate_haversine_distance_csv(stops_df, output_filename="haversine_distances.csv", chunk_size=5000):
    # Extract relevant data into a list of tuples
    stops_data = stops_df[['stop_id', 'stop_lat', 'stop_lon']].values

    # Generate all unique pairs of stops
    stop_pairs = [
        (stop1[0], stop1[1], stop1[2], stop2[0], stop2[1], stop2[2])
        for stop1, stop2 in combinations(stops_data, 2)
    ]
    
    print(f"Total pairs to process: {len(stop_pairs)}")

    # Split stop_pairs into chunks for parallel processing
    stop_pairs_chunks = [
        stop_pairs[i:i + chunk_size] for i in range(0, len(stop_pairs), chunk_size)
    ]

    # Use multiprocessing Pool for parallel computation
    with Pool(processes=cpu_count()) as pool:
        results = pool.map(compute_distances_chunk, stop_pairs_chunks)

    # Flatten the results list
    distances = [item for sublist in results for item in sublist]

    # Convert distances list to a DataFrame
    distances_df = pd.DataFrame(distances, columns=['stop_id_1', 'stop_id_2', 'distance_km'])

    # Save the DataFrame to a CSV file
    distances_df.to_csv(output_filename, index=False)
    print(f"Haversine distance CSV generated: {output_filename}")

# Function to import the stops data from a file (stops.txt)
def import_stops_data(filename="All_Data/stops.txt"):
    stops_df = pd.read_csv(filename)
    return stops_df

# Example usage:
if __name__ == "__main__":
    # Import stops data from 'stops.txt'
    stops_df = import_stops_data("All_Data/stops.txt")

    # Generate the Haversine distance CSV file
    generate_haversine_distance_csv(stops_df, "haversine_distances.csv")
