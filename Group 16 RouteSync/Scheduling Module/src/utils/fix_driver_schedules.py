import pandas as pd
from pathlib import Path
from typing import List, Tuple, Set, Dict
import logging
import os
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def find_overlapping_trips(schedule: pd.DataFrame, driver: int) -> List[Tuple[int, int]]:
    """Find pairs of overlapping trip IDs for a given driver."""
    driver_trips = schedule[schedule['driver'] == driver].sort_values('start_time')
    overlaps = []
    
    if len(driver_trips) <= 1:
        return overlaps
    
    # Check for overlaps between consecutive trips
    for i in range(len(driver_trips) - 1):
        current_trip = driver_trips.iloc[i]
        next_trip = driver_trips.iloc[i + 1]
        
        # Calculate idle time between trips
        idle_time = (next_trip['start_time'] - current_trip['end_time']).total_seconds() / 60
        
        if idle_time < 0:  # Overlap exists
            overlaps.append((current_trip['bus_id'], next_trip['bus_id']))
    
    return overlaps

def verify_schedule(schedule: pd.DataFrame) -> Dict[str, int]:
    """Verify that there are no overlapping trips in the schedule."""
    total_overlaps = 0
    drivers_with_overlaps = set()
    
    for driver in schedule['driver'].unique():
        overlaps = find_overlapping_trips(schedule, driver)
        if overlaps:
            total_overlaps += len(overlaps)
            drivers_with_overlaps.add(driver)
            
    return {
        'remaining_overlaps': total_overlaps,
        'drivers_with_overlaps': len(drivers_with_overlaps)
    }

def can_assign_to_driver(trip: pd.Series, driver_trips: pd.DataFrame) -> bool:
    """Check if a trip can be assigned to a driver without causing overlaps."""
    if len(driver_trips) == 0:
        return True
        
    # Check for overlaps with existing trips
    for _, existing_trip in driver_trips.iterrows():
        if not (trip['end_time'] <= existing_trip['start_time'] or 
                trip['start_time'] >= existing_trip['end_time']):
            return False
    
    return True

def find_available_driver(trip: pd.Series, schedule: pd.DataFrame, used_drivers: Set[int]) -> int:
    """Find a driver that can accommodate the trip without overlaps."""
    # First try existing drivers
    for driver in sorted(schedule['driver'].unique()):  # Sort to try lower numbered drivers first
        if driver in used_drivers:
            continue
        
        driver_trips = schedule[schedule['driver'] == driver]
        if can_assign_to_driver(trip, driver_trips):
            return driver
    
    # If no existing driver works, create a new one
    return max(schedule['driver'].max() + 1, max(used_drivers, default=0) + 1)

def fix_overlaps(schedule: pd.DataFrame, pbar: tqdm = None) -> pd.DataFrame:
    """Fix overlapping trips by reallocating them to different drivers."""
    fixed_schedule = schedule.copy()
    used_drivers = set()  # Track drivers we've already tried to fix
    changes_made = 0
    max_iterations = 10  # Prevent infinite loops
    iteration = 0
    
    while iteration < max_iterations:
        all_overlaps = []
        
        # Find all overlapping trips
        for driver in fixed_schedule['driver'].unique():
            if driver in used_drivers:
                continue
                
            overlaps = find_overlapping_trips(fixed_schedule, driver)
            if overlaps:
                all_overlaps.extend(overlaps)
                used_drivers.add(driver)
        
        if not all_overlaps:
            break
            
        # Fix each overlap
        for trip1_id, trip2_id in all_overlaps:
            # Get the later trip to reallocate
            trip_mask = fixed_schedule['bus_id'] == trip2_id
            if not trip_mask.any():
                continue
                
            trip_to_move = fixed_schedule[trip_mask].iloc[0]
            
            # Find a new driver for the trip
            new_driver = find_available_driver(trip_to_move, fixed_schedule, used_drivers)
            
            # Reallocate the trip
            fixed_schedule.loc[trip_mask, 'driver'] = new_driver
            changes_made += 1
            
            if pbar:
                pbar.update(1)
                pbar.set_postfix({'changes': changes_made})
        
        iteration += 1
    
    return fixed_schedule, changes_made

def process_schedule(input_file: Path, output_dir: Path) -> dict:
    """Process a single schedule file and return statistics."""
    logging.info(f"\nProcessing {input_file.name}...")
    
    # Load schedule
    schedule = pd.read_csv(input_file)
    
    # Rename 'Trip ID' to 'bus_id' if it exists
    if 'Trip ID' in schedule.columns:
        schedule = schedule.rename(columns={'Trip ID': 'bus_id'})
    
    # Load trip data to get start and end times
    trip_data = pd.read_csv("best_schedule.csv")
    
    # Setup progress bar for time conversions
    with tqdm(total=4, desc="Preprocessing", unit="step") as pbar:
        # Convert time strings to datetime
        trip_data['start_time'] = pd.to_datetime(trip_data['start_time']).dt.time
        pbar.update(1)
        
        trip_data['end_time'] = pd.to_datetime(trip_data['end_time']).dt.time
        pbar.update(1)
        
        # Convert time objects back to datetime for calculations
        base_date = pd.Timestamp('2024-01-01')
        trip_data['start_time'] = trip_data['start_time'].apply(lambda x: pd.Timestamp.combine(base_date, x))
        pbar.update(1)
        
        trip_data['end_time'] = trip_data['end_time'].apply(lambda x: pd.Timestamp.combine(base_date, x))
        pbar.update(1)
    
    # Merge trip times into schedule
    schedule = schedule.merge(
        trip_data[['bus_id', 'start_time', 'end_time']], 
        on='bus_id', 
        how='left'
    )
    
    # Check initial overlaps
    initial_check = verify_schedule(schedule)
    
    # Setup progress bar for overlap fixing
    with tqdm(total=initial_check['remaining_overlaps'], 
              desc="Fixing overlaps", 
              unit="overlap") as pbar:
        # Fix overlaps
        fixed_schedule, changes_made = fix_overlaps(schedule, pbar)
    
    # Verify the fix
    final_check = verify_schedule(fixed_schedule)
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save fixed schedule (only driver and bus_id columns)
    output_file = output_dir / input_file.name
    fixed_schedule[['driver', 'bus_id']].to_csv(output_file, index=False)
    
    return {
        'filename': input_file.name,
        'original_drivers': schedule['driver'].nunique(),
        'fixed_drivers': fixed_schedule['driver'].nunique(),
        'initial_overlaps': initial_check['remaining_overlaps'],
        'overlaps_fixed': changes_made,
        'remaining_overlaps': final_check['remaining_overlaps'],
        'drivers_with_overlaps': final_check['drivers_with_overlaps']
    }

def main():
    # Setup directories
    input_dir = Path("driver_schedules")
    output_dir = Path("fixed_driver_schedules")
    
    if not input_dir.exists():
        logging.error(f"Error: {input_dir} directory not found!")
        return
    
    # Get list of files to process
    files = list(input_dir.glob("*.csv"))
    
    # Process all CSV files with overall progress bar
    logging.info(f"Processing schedules from {input_dir}...")
    results = []
    
    with tqdm(total=len(files), desc="Processing files", unit="file") as file_pbar:
        for file_path in files:
            try:
                stats = process_schedule(file_path, output_dir)
                results.append(stats)
                logging.info(f"\nResults for {file_path.name}:")
                logging.info(f"- Initial overlaps: {stats['initial_overlaps']}")
                logging.info(f"- Overlaps fixed: {stats['overlaps_fixed']}")
                logging.info(f"- Remaining overlaps: {stats['remaining_overlaps']}")
                logging.info(f"- Original drivers: {stats['original_drivers']}")
                logging.info(f"- Final drivers: {stats['fixed_drivers']}")
                logging.info(f"- Additional drivers: {stats['fixed_drivers'] - stats['original_drivers']}")
                logging.info(f"- Drivers with remaining overlaps: {stats['drivers_with_overlaps']}")
                
                if stats['remaining_overlaps'] > 0:
                    logging.warning("WARNING: Some overlaps could not be fixed!")
                    
                file_pbar.update(1)
                file_pbar.set_postfix({'current': file_path.name})
            except Exception as e:
                logging.error(f"Error processing {file_path.name}: {str(e)}")
                file_pbar.update(1)
    
    # Create summary report
    if results:
        logging.info("\nSummary Report:")
        logging.info("=" * 50)
        total_initial = sum(r['initial_overlaps'] for r in results)
        total_fixed = sum(r['overlaps_fixed'] for r in results)
        total_remaining = sum(r['remaining_overlaps'] for r in results)
        total_new_drivers = sum(r['fixed_drivers'] - r['original_drivers'] for r in results)
        
        logging.info(f"Total files processed: {len(results)}")
        logging.info(f"Total initial overlaps: {total_initial}")
        logging.info(f"Total overlaps fixed: {total_fixed}")
        logging.info(f"Total remaining overlaps: {total_remaining}")
        logging.info(f"Total additional drivers needed: {total_new_drivers}")
        
        if total_remaining > 0:
            logging.warning("\nWARNING: Some schedules still have overlapping trips!")
        
        # Save detailed report
        report_df = pd.DataFrame(results)
        report_df['additional_drivers'] = report_df['fixed_drivers'] - report_df['original_drivers']
        report_file = output_dir / "fix_driver_overlaps_report.csv"
        report_df.to_csv(report_file, index=False)
        logging.info(f"\nDetailed report saved to {report_file}")
    else:
        logging.warning("No schedule files found to process!")

if __name__ == "__main__":
    main() 