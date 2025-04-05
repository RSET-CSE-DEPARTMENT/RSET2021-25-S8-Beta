import pandas as pd
import logging
import os
import glob

def process_schedule(file_name, max_buses):
    if 'bus' + str(max_buses) not in file_name:
        print(f"Skipping: {file_name} (does not contain {max_buses})")
        return
    
    schedule_data = pd.read_csv(file_name)
    schedule_data = schedule_data.rename(columns={'Bus': 'bus', 'Trip ID': 'trip_id'})
    
    trips = pd.read_csv('formatted_DMRC_trips.csv')
    stops = pd.read_csv('DMRC_Data/stops.txt')
    
    schedule = pd.merge(schedule_data, trips, on='trip_id')
    
    def fix_time_format(time_str):
        try:
            hours, minutes, seconds = map(int, time_str.split(":"))
            if hours >= 24:
                hours -= 24
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        except ValueError:
            logging.warning(f"Invalid time format encountered: {time_str}")
            return time_str

    schedule = schedule.drop(columns=['Unnamed: 0', 'trip_headsign', 'trip_short_name',
                             'direction_id', 'block_id', 'wheelchair_accessible', 'bikes_allowed'])
    schedule = schedule.rename(columns={'start_time_y': 'start_time', 'end_time_y': 'end_time',
                                         'start_stop_y': 'start_stop', 'end_stop_y': 'end_stop'})

    schedule = schedule.merge(stops.drop(columns=['stop_code', 'stop_desc']),
                              left_on='start_stop', right_on='stop_id')
    schedule = schedule.rename(columns={'stop_name': 'start_stop_name',
                                        'stop_lat': 'start_stop_lat',
                                        'stop_lon': 'start_stop_lon'}).drop(columns='stop_id')

    schedule = schedule.merge(stops.drop(columns=['stop_code', 'stop_desc']),
                              left_on='end_stop', right_on='stop_id')
    schedule = schedule.rename(columns={'stop_name': 'end_stop_name',
                                        'stop_lat': 'end_stop_lat',
                                        'stop_lon': 'end_stop_lon'}).drop(columns='stop_id')
    
    schedule['start_time'] = schedule['start_time'].apply(fix_time_format)
    schedule['end_time'] = schedule['end_time'].apply(fix_time_format)
    
    def haversine(lat1, lon1, lat2, lon2):
        from math import radians, cos, sin, sqrt, atan2
        R = 6371  
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c

    all_buses = [i + 1 for i in range(max_buses + 100)]
    available_buses = list(set(all_buses) - set(schedule['bus'].dropna().unique()))
    
    output_file = file_name.replace('best', 'fixed')
    schedule.to_csv(output_file, index=False)
    print(f"Processed: {file_name} -> {output_file}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Process bus schedules in a folder.")
    parser.add_argument("folder_path", type=str, help="Path to the folder containing schedule CSV files.")
    parser.add_argument("max_buses", type=int, help="Maximum number of buses available.")
    
    args = parser.parse_args()
    
    csv_files = glob.glob(os.path.join(args.folder_path, "*.csv"))
    
    for csv_file in csv_files:
        if 'best_schedule' in csv_file:
            process_schedule(csv_file, args.max_buses)
