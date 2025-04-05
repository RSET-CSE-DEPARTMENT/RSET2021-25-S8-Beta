import pandas as pd
import numpy as np

# Load the combined.xlsx file
file_path = 'combined.xlsx'
xls = pd.ExcelFile(file_path)

# Inspect the sheet names to understand the data
print(xls.sheet_names)

# Load relevant sheets (assuming 'stops', 'stop_times', 'routes' are available)
stops_df = pd.read_excel(xls, 'stops')
stop_times_df = pd.read_excel(xls, 'stop_times')
routes_df = pd.read_excel(xls, 'routes')

# Step 1: Calculate stop popularity based on how many routes serve each stop
stop_route_count = stop_times_df.groupby('stop_id')['trip_id'].nunique()
stops_df['route_count'] = stops_df['stop_id'].map(stop_route_count)

# Normalize the route count to estimate popularity (0 to 1 scale)
stops_df['popularity'] = stops_df['route_count'] / stops_df['route_count'].max()

# Step 2: Assign boarding rates based on stop popularity
# Assuming the more popular stops have a higher boarding rate
# Use a base boarding rate and adjust it using stop popularity
base_boarding_rate = 0.2  # Assume a base boarding rate
stops_df['boarding_rate'] = base_boarding_rate + (0.5 * stops_df['popularity'])  # Scaled boarding rate

# Step 3: Assign alighting rates based on stop characteristics
# Assume alighting is more likely to occur at less popular stops or stops near points of interest
# You can create an arbitrary factor for stops near the end of routes to increase alighting

# Identify end stops (assuming 'stop_sequence' column exists and max sequence implies the end stop)
stop_times_df['is_end_stop'] = stop_times_df.groupby('trip_id')['stop_sequence'].transform(max) == stop_times_df['stop_sequence']

# Map end stops to stops_df
end_stop_ids = stop_times_df[stop_times_df['is_end_stop']]['stop_id'].unique()
stops_df['is_end_stop'] = stops_df['stop_id'].isin(end_stop_ids).astype(int)

# Alighting rate based on stop popularity (inverse of popularity) and whether it's an end stop
base_alighting_rate = 0.2  # Assume a base alighting rate
stops_df['alighting_rate'] = base_alighting_rate + (0.5 * (1 - stops_df['popularity'])) + (0.3 * stops_df['is_end_stop'])

# Ensure the boarding and alighting rates do not exceed 1
stops_df['boarding_rate'] = stops_df['boarding_rate'].clip(0, 1)
stops_df['alighting_rate'] = stops_df['alighting_rate'].clip(0, 1)

# Step 4: Output the optimized boarding and alighting rates
optimized_rates = stops_df[['stop_id', 'boarding_rate', 'alighting_rate']]
print(optimized_rates.head())

# Save the optimized rates to a new Excel sheet
output_path = 'optimized_rates.xlsx'
with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
    optimized_rates.to_excel(writer, sheet_name='Optimized_Rates', index=False)

print(f'Optimized boarding and alighting rates saved to {output_path}')
