import pandas as pd
from pathlib import Path
from typing import List, Tuple, Set, Dict
import argparse
import os

def find_overlapping_trips(schedule: pd.DataFrame, bus_id: int) -> List[Tuple[int, int]]:
    """Find pairs of overlapping trip IDs for a given bus."""
    bus_trips = schedule[schedule['bus_id'] == bus_id].sort_values('start_time')
    overlaps = []
    
    if len(bus_trips) <= 1:
        return overlaps
    
    # Check for overlaps between consecutive trips
    for i in range(len(bus_trips) - 1):
        current_trip = bus_trips.iloc[i]
        next_trip = bus_trips.iloc[i + 1]
        
        # Calculate idle time between trips
        idle_time = (next_trip['start_time'] - current_trip['end_time']).total_seconds() / 60
        
        if idle_time < 0:  # Overlap exists
            overlaps.append((current_trip.name, next_trip.name))
    
    return overlaps

def verify_schedule(schedule: pd.DataFrame) -> Dict[str, int]:
    """Verify that there are no overlapping trips in the schedule."""
    total_overlaps = 0
    buses_with_overlaps = set()
    
    for bus_id in schedule['bus_id'].unique():
        overlaps = find_overlapping_trips(schedule, bus_id)
        if overlaps:
            total_overlaps += len(overlaps)
            buses_with_overlaps.add(bus_id)
            
    return {
        'remaining_overlaps': total_overlaps,
        'buses_with_overlaps': len(buses_with_overlaps)
    }

def can_assign_to_bus(trip: pd.Series, bus_trips: pd.DataFrame) -> bool:
    """Check if a trip can be assigned to a bus without causing overlaps."""
    if len(bus_trips) == 0:
        return True
        
    # Check for overlaps with existing trips
    for _, existing_trip in bus_trips.iterrows():
        if not (trip['end_time'] <= existing_trip['start_time'] or 
                trip['start_time'] >= existing_trip['end_time']):
            return False
    
    return True

def find_available_bus(trip: pd.Series, schedule: pd.DataFrame, used_buses: Set[int]) -> int:
    """Find a bus that can accommodate the trip without overlaps."""
    # First try existing buses
    for bus_id in sorted(schedule['bus_id'].unique()):  # Sort to try lower numbered buses first
        if bus_id in used_buses:
            continue
        
        bus_trips = schedule[schedule['bus_id'] == bus_id]
        if can_assign_to_bus(trip, bus_trips):
            return bus_id
    
    # If no existing bus works, create a new one
    return max(schedule['bus_id'].max() + 1, max(used_buses, default=0) + 1)

def fix_overlaps(schedule: pd.DataFrame) -> pd.DataFrame:
    """Fix overlapping trips by reallocating them to different buses."""
    fixed_schedule = schedule.copy()
    used_buses = set()  # Track buses we've already tried to fix
    changes_made = 0
    max_iterations = 10  # Prevent infinite loops
    iteration = 0
    
    while iteration < max_iterations:
        all_overlaps = []
        
        # Find all overlapping trips
        for bus_id in fixed_schedule['bus_id'].unique():
            if bus_id in used_buses:
                continue
                
            overlaps = find_overlapping_trips(fixed_schedule, bus_id)
            if overlaps:
                all_overlaps.extend(overlaps)
                used_buses.add(bus_id)
        
        if not all_overlaps:
            break
            
        # Fix each overlap
        for trip1_idx, trip2_idx in all_overlaps:
            # Get the later trip to reallocate
            trip_to_move = fixed_schedule.loc[trip2_idx]
            
            # Find a new bus for the trip
            new_bus_id = find_available_bus(trip_to_move, fixed_schedule, used_buses)
            
            # Reallocate the trip
            fixed_schedule.loc[trip2_idx, 'bus_id'] = new_bus_id
            changes_made += 1
        
        iteration += 1
    
    return fixed_schedule, changes_made

def process_schedule(input_file: Path, output_dir: Path) -> dict:
    """Process a single schedule file and return statistics."""
    # Load schedule
    schedule = pd.read_csv(input_file)
    
    # Convert datetime strings to pandas datetime objects and extract time component
    schedule['start_time'] = pd.to_datetime(schedule['start_time']).dt.time
    schedule['end_time'] = pd.to_datetime(schedule['end_time']).dt.time
    
    # Convert time objects back to datetime for calculations
    base_date = pd.Timestamp('2024-01-01')  # Use any date as base
    schedule['start_time'] = schedule['start_time'].apply(lambda x: pd.Timestamp.combine(base_date, x))
    schedule['end_time'] = schedule['end_time'].apply(lambda x: pd.Timestamp.combine(base_date, x))
    
    # Check initial overlaps
    initial_check = verify_schedule(schedule)
    
    # Fix overlaps
    fixed_schedule, changes_made = fix_overlaps(schedule)
    
    # Verify the fix
    final_check = verify_schedule(fixed_schedule)
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Before saving, convert back to time format
    fixed_schedule['start_time'] = fixed_schedule['start_time'].dt.time
    fixed_schedule['end_time'] = fixed_schedule['end_time'].dt.time
    
    # Save fixed schedule
    output_file = output_dir / input_file.name
    fixed_schedule.to_csv(output_file, index=False)
    
    return {
        'filename': input_file.name,
        'original_buses': schedule['bus_id'].nunique(),
        'fixed_buses': fixed_schedule['bus_id'].nunique(),
        'initial_overlaps': initial_check['remaining_overlaps'],
        'overlaps_fixed': changes_made,
        'remaining_overlaps': final_check['remaining_overlaps'],
        'buses_with_overlaps': final_check['buses_with_overlaps']
    }

def main():
    # Setup directories
    input_dir = Path("optimized_schedules")
    output_dir = Path("fixed_schedules")
    
    if not input_dir.exists():
        print(f"Error: {input_dir} directory not found!")
        return
    
    # Process all CSV files
    print(f"Processing schedules from {input_dir}...")
    results = []
    
    for file_path in input_dir.glob("*.csv"):
        print(f"\nProcessing {file_path.name}...")
        stats = process_schedule(file_path, output_dir)
        results.append(stats)
        print(f"- Initial overlaps: {stats['initial_overlaps']}")
        print(f"- Overlaps fixed: {stats['overlaps_fixed']}")
        print(f"- Remaining overlaps: {stats['remaining_overlaps']}")
        print(f"- Original buses: {stats['original_buses']}")
        print(f"- Final buses: {stats['fixed_buses']}")
        print(f"- Additional buses: {stats['fixed_buses'] - stats['original_buses']}")
        print(f"- Buses with remaining overlaps: {stats['buses_with_overlaps']}")
        
        if stats['remaining_overlaps'] > 0:
            print("WARNING: Some overlaps could not be fixed!")
    
    # Create summary report
    if results:
        print("\nSummary Report:")
        print("=" * 50)
        total_initial = sum(r['initial_overlaps'] for r in results)
        total_fixed = sum(r['overlaps_fixed'] for r in results)
        total_remaining = sum(r['remaining_overlaps'] for r in results)
        total_new_buses = sum(r['fixed_buses'] - r['original_buses'] for r in results)
        
        print(f"Total files processed: {len(results)}")
        print(f"Total initial overlaps: {total_initial}")
        print(f"Total overlaps fixed: {total_fixed}")
        print(f"Total remaining overlaps: {total_remaining}")
        print(f"Total additional buses needed: {total_new_buses}")
        
        if total_remaining > 0:
            print("\nWARNING: Some schedules still have overlapping trips!")
        
        # Save detailed report
        report_df = pd.DataFrame(results)
        report_df['additional_buses'] = report_df['fixed_buses'] - report_df['original_buses']
        report_file = output_dir / "fix_overlaps_report.csv"
        report_df.to_csv(report_file, index=False)
        print(f"\nDetailed report saved to {report_file}")
    else:
        print("No schedule files found to process!")

if __name__ == "__main__":
    main() 