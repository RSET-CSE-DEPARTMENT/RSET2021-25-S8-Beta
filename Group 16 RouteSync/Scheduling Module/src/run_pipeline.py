import os
import sys
import time
import pandas as pd
from pathlib import Path
from datetime import datetime
import logging
from tqdm import tqdm

# Import the required modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.format_dmrc_trips import format_dmrc_trips
from core.optimized_allocation import main as run_optimization
from utils.fix_overlaps import main as fix_overlaps
from utils.analyze_schedules import main as analyze_schedules
from core.driverAllocation import genetic_algorithm, load_data, fix_time_format

def setup_logging():
    """Setup logging configuration"""
    log_file = f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return log_file

def wait_for_file(file_path: str, timeout: int = 300):
    """Wait for a file to be created with a timeout"""
    start_time = time.time()
    while not os.path.exists(file_path):
        if time.time() - start_time > timeout:
            raise TimeoutError(f"Timeout waiting for {file_path} to be created")
        time.sleep(1)

def select_best_schedule(fixed_schedules_dir: str) -> str:
    """Select the best schedule based on metrics"""
    # Read the analysis report
    report_path = os.path.join(fixed_schedules_dir, "fix_overlaps_report.csv")
    report_df = pd.read_csv(report_path)
    
    # Filter schedules with no remaining overlaps
    valid_schedules = report_df[report_df['remaining_overlaps'] == 0]
    
    if len(valid_schedules) == 0:
        logging.warning("No schedules found without overlaps!")
        valid_schedules = report_df  # Use all schedules if none are perfect
    
    # Score each schedule (lower is better)
    valid_schedules['score'] = (
        0.5 * (valid_schedules['fixed_buses'] / valid_schedules['fixed_buses'].max()) +
        0.3 * (valid_schedules['remaining_overlaps'] / (valid_schedules['remaining_overlaps'].max() + 1)) +
        0.2 * (valid_schedules['additional_buses'] / (valid_schedules['additional_buses'].max() + 1))
    )
    
    # Get the best schedule
    best_schedule = valid_schedules.loc[valid_schedules['score'].idxmin()]
    return best_schedule['filename']

def copy_best_schedule(best_filename: str):
    """Copy the best schedule to the root directory"""
    source_path = os.path.join("fixed_schedules", best_filename)
    dest_path = "best_schedule.csv"
    
    import shutil
    shutil.copy2(source_path, dest_path)
    logging.info(f"Best schedule copied to {dest_path}")

def run_driver_allocation(schedule_file: str):
    """Run the driver allocation genetic algorithm"""
    logging.info("Starting driver allocation process...")
    
    # Load and preprocess schedule
    schedule, stops = load_data()
    print(len(schedule), len(stops))
    print(stops.columns)
    logging.info("Preprocessing schedule to fix time format...")
    # schedule['start_time'] = schedule['start_time'].apply(fix_time_format)
    # schedule['end_time'] = schedule['end_time'].apply(fix_time_format)
    # schedule['start_time'] = pd.to_datetime(schedule['start_time'], format=datetime_format).astype(int)
    # schedule['end_time'] = pd.to_datetime(schedule['end_time'], format=datetime_format).astype(int)

    schedule.sort_values(by='start_time', inplace=True)
    
    # Convert times to timestamps
    datetime_format = "%H:%M:%S"
    # schedule['start_time'] = pd.to_datetime(schedule['start_time'], format=datetime_format).astype(int)
    # schedule['end_time'] = pd.to_datetime(schedule['end_time'], format=datetime_format).astype(int)
    
    schedule['start_time'] = pd.to_datetime(schedule['start_time'], format=datetime_format).view('int64') // 10**9
    schedule['end_time'] = pd.to_datetime(schedule['end_time'], format=datetime_format).view('int64') // 10**9

    
    # Define driver configurations to try
    max_drivers_list = [200, 400, 600]
    best_allocation = None
    best_fitness = float('inf')
    
    # Create output directory
    os.makedirs("driver_schedules", exist_ok=True)
    
    # Try different driver configurations
    for max_drivers in max_drivers_list:
        logging.info(f"\nTrying configuration with {max_drivers} drivers...")
        current_allocation = genetic_algorithm(schedule, max_drivers, generations=15, stops=stops)
        
        # Save the allocation
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"driver_schedules/driver_schedule_{max_drivers}drivers_{timestamp}.csv"
        
        # Prepare data for CSV
        allocation_data = []
        for i, driver_schedule in enumerate(current_allocation):
            for bus in driver_schedule:
                allocation_data.append({
                    'driver': i + 1,
                    'bus': bus
                })
        
        # Save to CSV
        allocation_df = pd.DataFrame(allocation_data)
        allocation_df.to_csv(output_file, index=False)
        logging.info(f"Saved allocation to {output_file}")
    
    logging.info("Driver allocation completed")

def main():
    # Setup logging
    log_file = setup_logging()
    logging.info("Starting DMRC bus allocation pipeline")
    print("\n" + "="*50)
    print("DMRC Bus Allocation Pipeline")
    print("="*50 + "\n")
    
    try:
        # # Step 1: Format DMRC trips
        # print("\nStep 1: Formatting DMRC trips")
        # print("-"*30)
        # format_dmrc_trips()
        # wait_for_file("formatted_DMRC_trips.csv")
        # logging.info("DMRC trips formatting completed")
        
        # # Step 2: Run optimization
        # print("\nStep 2: Running optimization")
        # print("-"*30)
        # run_optimization()
        # wait_for_file("optimized_schedules")
        # logging.info("Optimization completed")
        
        # # Step 3: Fix overlaps
        # print("\nStep 3: Fixing overlaps")
        # print("-"*30)
        # fix_overlaps()
        # wait_for_file("fixed_schedules")
        # logging.info("Overlap fixing completed")
        
        # # Step 4: Analyze schedules
        # print("\nStep 4: Analyzing schedules")
        # print("-"*30)
        # analyze_schedules()
        # logging.info("Schedule analysis completed")
        
        # # Step 5: Select best schedule
        # print("\nStep 5: Selecting best schedule")
        # print("-"*30)
        # best_schedule = select_best_schedule("fixed_schedules")
        # logging.info(f"Selected best schedule: {best_schedule}")
        
        # # Copy best schedule to root directory
        # copy_best_schedule(best_schedule)
        
        # Step 6: Allocate drivers
        print("\nStep 6: Allocating drivers")
        print("-"*30)
        run_driver_allocation("best_schedule.csv")
        logging.info("Driver allocation completed")
        
        print("\nPipeline completed successfully!")
        print(f"Logs saved to: {log_file}")
        print(f"Best schedule saved as: best_schedule.csv")
        print(f"Driver schedules saved in: driver_schedules/")
        print("\nFinal metrics:")
        print("-"*30)
        
        # Display metrics for best schedule
        report_df = pd.read_csv(os.path.join("fixed_schedules", "fix_overlaps_report.csv"))
        best_metrics = report_df[report_df['filename'] == best_schedule].iloc[0]
        print(f"Number of buses: {best_metrics['fixed_buses']}")
        print(f"Overlaps: {best_metrics['remaining_overlaps']}")
        print(f"Additional buses needed: {best_metrics['additional_buses']}")
        
    except Exception as e:
        logging.error(f"Pipeline failed: {str(e)}")
        print(f"\nError: Pipeline failed. Check {log_file} for details.")
        raise

if __name__ == "__main__":
    main() 