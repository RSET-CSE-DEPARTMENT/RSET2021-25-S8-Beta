import pandas as pd
import numpy as np
import os
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.dates import date2num, DateFormatter, HourLocator
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Tuple

def load_schedule(file_path: str) -> pd.DataFrame:
    """Load a schedule from CSV file and parse timestamps."""
    df = pd.read_csv(file_path)
    df['start_time'] = pd.to_datetime(df['start_time'])
    df['end_time'] = pd.to_datetime(df['end_time'])
    return df

def calculate_metrics(schedule: pd.DataFrame) -> Dict[str, float]:
    """Calculate various metrics for a schedule with enhanced measurements."""
    metrics = {}
    total_buses = schedule['bus_id'].nunique()
    total_trips = len(schedule)
    total_distance = schedule['distance'].sum()
    
    idle_times = []
    overlaps = 0
    bus_utilizations = []
    trips_per_bus = []
    buses_with_zero_overlaps = 0
    bus_overlaps = []

    for bus_id in schedule['bus_id'].unique():
        bus_trips = schedule[schedule['bus_id'] == bus_id].sort_values('start_time')
        trips_count = len(bus_trips)
        trips_per_bus.append(trips_count)
        
        if trips_count == 0:
            continue
        
        # Calculate trip durations and utilization
        trip_durations = (bus_trips['end_time'] - bus_trips['start_time']).dt.total_seconds() / 60
        total_active_time = trip_durations.sum()
        time_window = (bus_trips['end_time'].max() - bus_trips['start_time'].min()).total_seconds() / 60
        utilization = total_active_time / time_window if time_window > 0 else 0
        bus_utilizations.append(utilization)
        
        # Calculate time gaps and overlaps
        if trips_count > 1:
            end_times = bus_trips['end_time'].iloc[:-1]
            start_times = bus_trips['start_time'].iloc[1:]
            gaps = [(st - et).total_seconds() / 60 for st, et in zip(start_times, end_times)]
            
            bus_overlap = sum(1 for gap in gaps if gap < 0)
            overlaps += bus_overlap
            bus_overlaps.append(bus_overlap)
            idle_times.extend([gap for gap in gaps if gap > 0])
            
            if bus_overlap == 0:
                buses_with_zero_overlaps += 1
        else:
            bus_overlaps.append(0)
            buses_with_zero_overlaps += 1

    # Calculate derived metrics
    total_idle_time = sum(idle_times) if idle_times else 0
    avg_idle_time = np.mean(idle_times) if idle_times else 0
    max_idle_time = max(idle_times) if idle_times else 0
    avg_utilization = np.mean(bus_utilizations) if bus_utilizations else 0
    std_trips = np.std(trips_per_bus) if trips_per_bus else 0
    
    efficiency_score = total_distance / (total_idle_time + 1)
    fitness_value = 0.4*(total_buses/(total_buses+100)) + 0.3*(1/(total_trips/total_buses+1)) + \
                    0.2*(1/(efficiency_score+1)) + 0.1*(overlaps/(total_trips+1))

    return {
        'total_buses': total_buses,
        'total_trips': total_trips,
        'total_distance': total_distance,
        'total_idle_time': total_idle_time,
        'avg_idle_time': avg_idle_time,
        'max_idle_time': max_idle_time,
        'overlaps': overlaps,
        'buses_with_zero_overlaps': buses_with_zero_overlaps,
        'avg_utilization': avg_utilization,
        'std_trips_per_bus': std_trips,
        'efficiency_score': efficiency_score,
        'fitness_score': fitness_value
    }

def analyze_schedules(directory: str = "optimized_schedules") -> pd.DataFrame:
    """Analyze all schedules and return metrics with file paths."""
    results = []
    for file_path in Path(directory).glob("*.csv"):
        if "gen-1" in file_path.name:
            continue
            
        parts = file_path.name.split('_')
        metrics = calculate_metrics(load_schedule(str(file_path)))
        metrics.update({
            'filename': file_path.name,
            'file_path': str(file_path),
            'buses': int(parts[1].replace('buses', '')),
            'generation': int(parts[2].replace('gen', '')),
            'timestamp': datetime.strptime(parts[3].split('.')[0], '%Y%m%d')
        })
        results.append(metrics)
    return pd.DataFrame(results)

def plot_gantt_chart(schedule: pd.DataFrame, buses: int, gen: int):
    """Generate a clean Gantt chart visualization with proper formatting."""
    plt.figure(figsize=(15, max(6, buses * 0.5)))  # Dynamic height based on bus count
    schedule = schedule.sort_values(['bus_id', 'start_time'])
    unique_buses = sorted(schedule['bus_id'].unique())
    y_ticks = list(range(len(unique_buses)))
    bus_id_map = {bus: idx for idx, bus in enumerate(unique_buses)}

    # Create color palette
    colors = plt.cm.tab20.colors
    max_color = len(colors)

    for idx, (_, trip) in enumerate(schedule.iterrows()):
        bus_idx = bus_id_map[trip['bus_id']]
        duration = (trip['end_time'] - trip['start_time']).total_seconds()/3600
        plt.barh(
            y=bus_idx,
            width=duration,
            left=trip['start_time'],
            color=colors[idx % max_color],
            edgecolor='black',
            linewidth=0.5,
            height=0.8  # Reduced bar height for spacing
        )

    # Format time axis
    plt.gca().xaxis.set_major_formatter(DateFormatter('%H:%M'))
    plt.gca().xaxis.set_major_locator(HourLocator(interval=2))
    plt.gcf().autofmt_xdate()

    # Configure y-axis
    plt.yticks(y_ticks, unique_buses)
    plt.ylim(-0.5, len(unique_buses) - 0.5)
    plt.ylabel('Bus ID')

    # Add grid and title
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.title(f'Bus Schedule Gantt Chart - {buses} Buses (Gen {gen})')
    plt.tight_layout()
    plt.savefig(f'gantt_{buses}_gen{gen}.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_advanced_metrics(analysis_df: pd.DataFrame):
    """Generate advanced visualizations including heatmaps and scatter plots."""
    plt.figure(figsize=(12, 8))
    sns.scatterplot(data=analysis_df, x='buses', y='efficiency_score', 
                    hue='generation', size='fitness_score', palette='viridis')
    plt.title('Efficiency vs Bus Configuration')
    plt.savefig('efficiency_scatter.png')
    plt.close()

    plt.figure(figsize=(10, 6))
    heatmap_data = analysis_df.pivot_table(
        index='buses', 
        columns='generation', 
        values='overlaps', 
        aggfunc='sum'  # Changed from default 'mean'
    )
    sns.heatmap(heatmap_data, annot=True, fmt="d", cmap="YlGnBu")
    plt.title('Overlaps Heatmap by Configuration and Generation')
    plt.savefig('overlaps_heatmap.png')
    plt.close()

def print_detailed_summary(analysis_df: pd.DataFrame):
    """Enhanced summary with statistical analysis."""
    print("\nAdvanced Statistical Summary")
    print("=" * 50)
    for buses in analysis_df['buses'].unique():
        subset = analysis_df[analysis_df['buses'] == buses]
        print(f"\nConfiguration: {buses} Buses")
        print(f"Average Utilization: {subset['avg_utilization'].mean():.1%}")
        print(f"Median Efficiency: {subset['efficiency_score'].median():.2f}")
        print(f"Max Idle Time Range: {subset['max_idle_time'].max():.1f} mins")

def main():
    analysis_df = analyze_schedules()
    
    if analysis_df.empty:
        print("No schedules found!")
        return

    # Generate core visualizations
    plot_advanced_metrics(analysis_df)
    
    # Generate detailed plots for best configurations
    best_configs = analysis_df.loc[analysis_df.groupby('buses')['fitness_score'].idxmin()]
    for _, row in best_configs.iterrows():
        schedule = load_schedule(row['file_path'])
        plot_gantt_chart(schedule, row['buses'], row['generation'])
        
        plt.figure()
        sns.histplot(schedule.groupby('bus_id').size(), bins=15)
        plt.title(f'Trips per Bus Distribution - {row["buses"]} Buses')
        plt.savefig(f'trips_dist_{row["buses"]}.png')
        plt.close()

    # Save and display results
    analysis_df.to_csv('advanced_analysis.csv', index=False)
    print_detailed_summary(analysis_df)
    print("\nAnalysis complete. Check generated plots and CSV file.")

if __name__ == "__main__":
    main()