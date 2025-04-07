import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

directory = './collected_schedules4/'
schedule_files = [f for f in os.listdir(directory) if f.startswith('fixed_schedule_bus') and f.endswith('.csv')]

trips = pd.read_csv('formatted_DMRC_trips.csv')
stops = pd.read_csv('DMRC_Data/stops.txt').drop(columns=['stop_code', 'stop_desc'])
times = pd.read_csv('DMRC_Data/stop_times.txt').drop(columns=['stop_headsign', 'pickup_type', 'drop_off_type', 'timepoint', 'continuous_pickup', 'continuous_drop_off'])

def adjust_time_to_next_day(time_str):
    try:
        time_parts = time_str.split(':')
        hour = int(time_parts[0])
        if hour >= 24:
            adjusted_hour = hour - 24
            adjusted_time_str = f"{adjusted_hour:02}:{time_parts[1]}:{time_parts[2]}"
            return pd.to_datetime(adjusted_time_str) + pd.Timedelta(days=1)
        return pd.to_datetime(time_str)
    except Exception as e:
        print(f"Error adjusting time: {time_str}, {e}")
        return None

for file in schedule_files:
    print(f"Processing {file}...")
    schedule = pd.read_csv(os.path.join(directory, file))
    schedule_trips_merge = pd.merge(schedule, trips, on='trip_id').drop(
        columns=['service_id', 'trip_headsign', 'trip_short_name', 'direction_id', 'block_id', 
                 'wheelchair_accessible', 'bikes_allowed', 'Unnamed: 0'], errors='ignore')
    stops_times_merge = pd.merge(times, stops)
    trip_distances = stops_times_merge.groupby('trip_id')['shape_dist_traveled'].last() / 1000
    schedule_combined = pd.merge(schedule_trips_merge, trip_distances, on='trip_id')
    
    bus_statistics = schedule_combined.groupby('bus')['shape_dist_traveled'].agg('sum').to_frame()
    bus_statistics['trip_count'] = schedule_combined.groupby('bus').size()
    schedule_combined_sorted = schedule_combined.sort_values(by=['bus', 'start_time_y'])
    bus_statistics['travel_time'] = (
        pd.to_datetime(schedule_combined_sorted.groupby('bus')['end_time_y'].last().apply(adjust_time_to_next_day)) -
        pd.to_datetime(schedule_combined_sorted.groupby('bus')['start_time_y'].first().apply(adjust_time_to_next_day))
    ).dt.total_seconds() / 3600
    
    mileage = 3.7
    petrol_price = 94.77
    co2_emission_factor = 2.31
    bus_statistics['petrol_charges'] = bus_statistics['shape_dist_traveled'] / mileage * petrol_price
    bus_statistics['carbon_emissions'] = bus_statistics['shape_dist_traveled'] * mileage * co2_emission_factor
    
    output_prefix = file.replace('.csv', '')
    schedule_combined.to_csv(f"./collected_schedules4/{output_prefix}_combined.csv", index=False)
    bus_statistics.to_csv(f"./collected_schedules4/{output_prefix}_bus_statistics.csv")
    
    print(f"Completed processing {file}\n")
