import pandas as pd
import ast
import random
from datetime import datetime, timedelta

def generate_stop_times(trips_file, routes_file, distance_file, output_file):
    # Load data
    trips_df = pd.read_csv(trips_file)
    routes_df = pd.read_csv(routes_file)
    distances_df = pd.read_csv(distance_file, index_col=0)

    # Convert stop IDs to integers for consistency
    distances_df.index = distances_df.index.astype(int)
    distances_df.columns = distances_df.columns.astype(int)

    # Convert 'stops' column from string representation of a list to an actual list
    routes_df["stops"] = routes_df["stops"].apply(ast.literal_eval)

    # Create a dictionary mapping route_id to its list of stops
    route_stop_dict = dict(zip(routes_df["route_id"], routes_df["stops"]))

    # Initialize stop_times list with headers
    stop_times_data = []

    # Define time constraints
    time_gap = timedelta(minutes=2)  # Time gap between stops
    max_time = datetime.strptime("22:00:00", "%H:%M:%S")  # Last trip start time (10 PM)

    # Generate stop_times.csv data
    for _, row in trips_df.iterrows():
        route_id = row["route_id"]
        trip_id = row["trip_id"]

        if route_id in route_stop_dict:
            stops = route_stop_dict[route_id]

            # Decide start time: usually 6 AM, but sometimes between 1 PM and 4 PM
            if random.random() < 0.2:  # 20% chance to start between 1 PM and 4 PM
                start_hour = random.randint(13, 16)
                base_time = datetime.strptime(f"{start_hour}:00:00", "%H:%M:%S")
            else:
                base_time = datetime.strptime("06:00:00", "%H:%M:%S")

            trip_start_time = base_time  # Each trip starts from base_time
            shape_dist_traveled = [0]  # First stop starts at 0

            for seq, stop_id in enumerate(stops, start=1):
                arrival_time = trip_start_time.strftime("%H:%M:%S")
                departure_time = (trip_start_time + timedelta(seconds=20)).strftime("%H:%M:%S")

                # Compute shape_dist_traveled
                if seq > 1:
                    prev_stop = stops[seq - 2]
                    curr_stop = stop_id

                    # Check if distance exists in the matrix
                    if prev_stop in distances_df.index and curr_stop in distances_df.columns:
                        distance = distances_df.loc[prev_stop, curr_stop]
                    else:
                        print(f"Warning: Missing distance from stop {prev_stop} to {curr_stop}, setting to 0.")
                        distance = 0  # Default to 0 if missing

                    shape_dist_traveled.append(shape_dist_traveled[-1] + distance)
                else:
                    shape_dist_traveled.append(0)

                # Append data
                stop_times_data.append([
                    trip_id, arrival_time, departure_time, stop_id, seq, 
                    "",  # stop_headsign
                    0,   # pickup_type
                    0,   # drop_off_type
                    shape_dist_traveled[-1],  # shape_dist_traveled
                    "",  # timepoint
                    "",  # continuous_pickup
                    ""   # continuous_drop_off
                ])

                # Increment time for next stop
                trip_start_time += time_gap

            # Increment base_time for the next trip to avoid overlapping
            base_time += timedelta(minutes=5)

    # Convert list to DataFrame
    stop_times_df = pd.DataFrame(stop_times_data, columns=[
        "trip_id", "arrival_time", "departure_time", "stop_id", "stop_sequence",
        "stop_headsign", "pickup_type", "drop_off_type",
        "shape_dist_traveled", "timepoint", "continuous_pickup",
        "continuous_drop_off"
    ])

    # Save to CSV
    stop_times_df.to_csv(output_file, index=False)
    print(f"Generated {output_file}")

# Example usage
generate_stop_times("new_trips.csv", "route_stop_mapping.csv", "stops_distance.csv", "new_stop_times.csv")
