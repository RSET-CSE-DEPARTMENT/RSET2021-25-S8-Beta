import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import logging
from pathlib import Path

def load_schedule(schedule_file: str) -> pd.DataFrame:
    """Load the bus schedule from CSV file."""
    df = pd.read_csv(schedule_file)
    df['start_time'] = pd.to_datetime(df['start_time'])
    df['end_time'] = pd.to_datetime(df['end_time'])
    return df

def calculate_shift_duration(start_time: datetime, end_time: datetime) -> float:
    """Calculate shift duration in hours."""
    return (end_time - start_time).total_seconds() / 3600

def needs_break(shift_duration: float) -> bool:
    """Check if a shift needs a break based on duration."""
    return shift_duration > 4  # Break needed after 4 hours

def calculate_break_duration(shift_duration: float) -> float:
    """Calculate required break duration in hours."""
    if shift_duration <= 4:
        return 0
    elif shift_duration <= 6:
        return 0.5  # 30 minutes break
    else:
        return 1.0  # 1 hour break

def allocate_drivers(schedule_df: pd.DataFrame, max_shift_duration: float = 8.0) -> pd.DataFrame:
    """
    Allocate drivers to buses while respecting working hours and break requirements.
    
    Args:
        schedule_df: DataFrame containing bus schedule
        max_shift_duration: Maximum shift duration in hours (default: 8)
        
    Returns:
        DataFrame with driver assignments
    """
    # Sort buses by start time
    bus_schedules = schedule_df.groupby('bus_id').apply(
        lambda x: x.sort_values('start_time')
    ).reset_index(drop=True)
    
    # Initialize driver assignments
    driver_assignments = []
    current_driver = 1
    driver_shifts = {}  # Track driver shifts
    
    for bus_id in bus_schedules['bus_id'].unique():
        bus_trips = bus_schedules[bus_schedules['bus_id'] == bus_id]
        
        # Calculate total duration for this bus
        total_duration = calculate_shift_duration(
            bus_trips['start_time'].min(),
            bus_trips['end_time'].max()
        )
        
        # Check if we need to split into multiple shifts
        if total_duration > max_shift_duration:
            # Split into multiple shifts
            current_time = bus_trips['start_time'].min()
            shift_start = current_time
            
            while current_time < bus_trips['end_time'].max():
                # Find trips that fit in current shift
                shift_end = min(
                    shift_start + timedelta(hours=max_shift_duration),
                    bus_trips['end_time'].max()
                )
                
                shift_trips = bus_trips[
                    (bus_trips['start_time'] >= shift_start) &
                    (bus_trips['end_time'] <= shift_end)
                ]
                
                if not shift_trips.empty:
                    # Calculate break requirements
                    shift_duration = calculate_shift_duration(shift_start, shift_end)
                    break_duration = calculate_break_duration(shift_duration)
                    
                    # Assign driver
                    driver_shifts[current_driver] = {
                        'start_time': shift_start,
                        'end_time': shift_end,
                        'break_duration': break_duration
                    }
                    
                    for _, trip in shift_trips.iterrows():
                        driver_assignments.append({
                            'bus_id': bus_id,
                            'driver_id': current_driver,
                            'trip_id': trip['trip_id'],
                            'start_time': trip['start_time'],
                            'end_time': trip['end_time'],
                            'shift_start': shift_start,
                            'shift_end': shift_end,
                            'break_duration': break_duration
                        })
                    
                    current_driver += 1
                
                shift_start = shift_end
        
        else:
            # Single shift is sufficient
            shift_start = bus_trips['start_time'].min()
            shift_end = bus_trips['end_time'].max()
            shift_duration = calculate_shift_duration(shift_start, shift_end)
            break_duration = calculate_break_duration(shift_duration)
            
            driver_shifts[current_driver] = {
                'start_time': shift_start,
                'end_time': shift_end,
                'break_duration': break_duration
            }
            
            for _, trip in bus_trips.iterrows():
                driver_assignments.append({
                    'bus_id': bus_id,
                    'driver_id': current_driver,
                    'trip_id': trip['trip_id'],
                    'start_time': trip['start_time'],
                    'end_time': trip['end_time'],
                    'shift_start': shift_start,
                    'shift_end': shift_end,
                    'break_duration': break_duration
                })
            
            current_driver += 1
    
    # Create DataFrame with driver assignments
    driver_df = pd.DataFrame(driver_assignments)
    
    # Add shift statistics
    shift_stats = []
    for driver_id, shift in driver_shifts.items():
        shift_stats.append({
            'driver_id': driver_id,
            'shift_start': shift['start_time'],
            'shift_end': shift['end_time'],
            'shift_duration': calculate_shift_duration(shift['start_time'], shift['end_time']),
            'break_duration': shift['break_duration']
        })
    
    shift_stats_df = pd.DataFrame(shift_stats)
    
    return driver_df, shift_stats_df

def analyze_driver_assignments(driver_df: pd.DataFrame, shift_stats_df: pd.DataFrame) -> Dict:
    """Analyze driver assignments and generate statistics."""
    stats = {
        'total_drivers': driver_df['driver_id'].nunique(),
        'total_shifts': len(shift_stats_df),
        'avg_shift_duration': shift_stats_df['shift_duration'].mean(),
        'max_shift_duration': shift_stats_df['shift_duration'].max(),
        'total_break_time': shift_stats_df['break_duration'].sum(),
        'buses_with_multiple_shifts': driver_df.groupby('bus_id')['driver_id'].nunique().gt(1).sum()
    }
    
    # Calculate driver utilization
    total_time = (shift_stats_df['shift_end'] - shift_stats_df['shift_start']).sum().total_seconds() / 3600
    total_break_time = shift_stats_df['break_duration'].sum()
    stats['driver_utilization'] = (total_time - total_break_time) / total_time
    
    return stats

def main():
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Load best schedule
        schedule_file = "best_schedule.csv"
        logging.info(f"Loading schedule from {schedule_file}")
        schedule_df = load_schedule(schedule_file)
        
        # Allocate drivers
        logging.info("Allocating drivers to buses...")
        driver_df, shift_stats_df = allocate_drivers(schedule_df)
        
        # Analyze assignments
        logging.info("Analyzing driver assignments...")
        stats = analyze_driver_assignments(driver_df, shift_stats_df)
        
        # Create output directory
        output_dir = Path("driver_assignments")
        output_dir.mkdir(exist_ok=True)
        
        # Save results
        driver_df.to_csv(output_dir / "driver_assignments.csv", index=False)
        shift_stats_df.to_csv(output_dir / "shift_statistics.csv", index=False)
        
        # Print summary
        print("\nDriver Assignment Summary")
        print("=" * 50)
        print(f"Total drivers needed: {stats['total_drivers']}")
        print(f"Total shifts: {stats['total_shifts']}")
        print(f"Average shift duration: {stats['avg_shift_duration']:.2f} hours")
        print(f"Maximum shift duration: {stats['max_shift_duration']:.2f} hours")
        print(f"Total break time: {stats['total_break_time']:.2f} hours")
        print(f"Driver utilization: {stats['driver_utilization']:.2%}")
        print(f"Buses requiring multiple shifts: {stats['buses_with_multiple_shifts']}")
        
        logging.info("Driver allocation completed successfully")
        
    except Exception as e:
        logging.error(f"Error in driver allocation: {str(e)}")
        raise

if __name__ == "__main__":
    main() 