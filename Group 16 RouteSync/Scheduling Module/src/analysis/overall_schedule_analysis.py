import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt
import re

# Define columns to ensure consistency
columns = [
    'Schedule', 'Generation', 'Total Distance (km)', 'Min Distance (km)', 'Max Distance (km)', 'Avg Distance (km)',
    'Total Trips', 'Min Trips', 'Max Trips', 'Avg Trips',
    'Total Travel Time (hrs)', 'Min Travel Time (hrs)', 'Max Travel Time (hrs)', 'Avg Travel Time (hrs)',
    'Total Petrol Cost (INR)', 'Min Petrol Cost (INR)', 'Max Petrol Cost (INR)', 'Avg Petrol Cost (INR)',
    'Total Carbon Emissions (kg CO2)', 'Min Carbon Emissions (kg CO2)', 'Max Carbon Emissions (kg CO2)', 'Avg Carbon Emissions (kg CO2)'
]

# Initialize empty DataFrame with predefined columns
comparison_df = pd.DataFrame(columns=columns)

# Directory containing bus statistics files
directory = './collected_schedules4/600processed/'
stats_files = [f for f in os.listdir(directory) if f.endswith('_bus_statistics.csv')]

# Function to extract generation number from schedule name
def extract_generation(schedule_name):
    match = re.search(r'gen(\d+)', schedule_name)  # Looks for 'gen<number>'
    return int(match.group(1)) if match else float('inf')  # Default to inf if no match

# Process each schedule statistics file
for file in stats_files:
    print(f"Processing {file}...")
    
    schedule_name = file.replace('_bus_statistics.csv', '')
    generation_number = extract_generation(schedule_name)
    
    file_path = os.path.join(directory, file)
    bus_stats = pd.read_csv(file_path)

    # Compute required metrics
    total_distance = bus_stats['shape_dist_traveled'].sum()
    min_distance = bus_stats['shape_dist_traveled'].min()
    max_distance = bus_stats['shape_dist_traveled'].max()
    avg_distance = bus_stats['shape_dist_traveled'].mean()
    
    total_trips = bus_stats['trip_count'].sum()
    min_trips = bus_stats['trip_count'].min()
    max_trips = bus_stats['trip_count'].max()
    avg_trips = bus_stats['trip_count'].mean()
    
    total_travel_time = bus_stats['travel_time'].sum()
    min_travel_time = bus_stats['travel_time'].min()
    max_travel_time = bus_stats['travel_time'].max()
    avg_travel_time = bus_stats['travel_time'].mean()
    
    total_petrol_cost = bus_stats['petrol_charges'].sum()
    min_petrol_cost = bus_stats['petrol_charges'].min()
    max_petrol_cost = bus_stats['petrol_charges'].max()
    avg_petrol_cost = bus_stats['petrol_charges'].mean()
    
    total_carbon_emission = bus_stats['carbon_emissions'].sum()
    min_carbon_emission = bus_stats['carbon_emissions'].min()
    max_carbon_emission = bus_stats['carbon_emissions'].max()
    avg_carbon_emission = bus_stats['carbon_emissions'].mean()

    # Create a new row as a dictionary
    new_row = {
        'Schedule': schedule_name, 'Generation': generation_number,
        'Total Distance (km)': total_distance, 'Min Distance (km)': min_distance,
        'Max Distance (km)': max_distance, 'Avg Distance (km)': avg_distance,
        'Total Trips': total_trips, 'Min Trips': min_trips,
        'Max Trips': max_trips, 'Avg Trips': avg_trips,
        'Total Travel Time (hrs)': total_travel_time, 'Min Travel Time (hrs)': min_travel_time,
        'Max Travel Time (hrs)': max_travel_time, 'Avg Travel Time (hrs)': avg_travel_time,
        'Total Petrol Cost (INR)': total_petrol_cost, 'Min Petrol Cost (INR)': min_petrol_cost,
        'Max Petrol Cost (INR)': max_petrol_cost, 'Avg Petrol Cost (INR)': avg_petrol_cost,
        'Total Carbon Emissions (kg CO2)': total_carbon_emission, 'Min Carbon Emissions (kg CO2)': min_carbon_emission,
        'Max Carbon Emissions (kg CO2)': max_carbon_emission, 'Avg Carbon Emissions (kg CO2)': avg_carbon_emission
    }

    # Append the new row to the DataFrame
    comparison_df = pd.concat([comparison_df, pd.DataFrame([new_row])], ignore_index=True)

# Sort schedules by generation number
comparison_df = comparison_df.sort_values(by='Generation', ascending=True)

# Save the aggregated comparison data
comparison_df.to_csv("./collected_schedules4/600processed/comparison_summary.csv", index=False)

# Convert 'Generation' column to string for proper labeling
comparison_df['Generation'] = comparison_df['Generation'].astype(str)

# Plot comparison metrics
metrics = ['Total Distance (km)', 'Total Trips', 'Total Travel Time (hrs)', 'Total Petrol Cost (INR)', 'Total Carbon Emissions (kg CO2)']
for metric in metrics:
    plt.figure(figsize=(10, 5))
    sns.barplot(x='Generation', y=metric, data=comparison_df, order=comparison_df['Generation'])
    plt.xticks(rotation=45)
    plt.title(f"Comparison of {metric} Across Generations")
    plt.ylabel(metric)
    plt.xlabel("Generation")
    plt.tight_layout()
    plt.show()
