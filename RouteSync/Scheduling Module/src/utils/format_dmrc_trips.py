import pandas as pd
import logging
import os
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dmrc_formatting.log'),
        logging.StreamHandler()
    ]
)

def load_dmrc_data(data_dir: str = "DMRC_Data") -> tuple:
    """
    Load DMRC data files from the specified directory.
    
    Args:
        data_dir (str): Directory containing DMRC data files
        
    Returns:
        tuple: (routes_df, trips_df, stops_df, stop_times_df)
    """
    try:
        logging.info("Loading DMRC data files...")
        
        # Ensure data directory exists
        if not os.path.exists(data_dir):
            raise FileNotFoundError(f"Data directory '{data_dir}' not found")
        
        # Load all required files
        routes = pd.read_csv(os.path.join(data_dir, "routes.txt"))
        trips = pd.read_csv(os.path.join(data_dir, "trips.txt"))
        stops = pd.read_csv(os.path.join(data_dir, "stops.txt"))
        stop_times = pd.read_csv(os.path.join(data_dir, "stop_times.txt"))
        
        logging.info("Successfully loaded all DMRC data files")
        return routes, trips, stops, stop_times
        
    except FileNotFoundError as e:
        logging.error(f"File not found error: {str(e)}")
        raise
    except pd.errors.EmptyDataError:
        logging.error("One or more data files are empty")
        raise
    except Exception as e:
        logging.error(f"Error loading data files: {str(e)}")
        raise

def process_trip_times(trips_df: pd.DataFrame, stop_times_df: pd.DataFrame) -> pd.DataFrame:
    """
    Process trip times by merging trip data with stop times.
    Matches exactly the logic from test1.ipynb.
    
    Args:
        trips_df (pd.DataFrame): Trips dataframe
        stop_times_df (pd.DataFrame): Stop times dataframe
        
    Returns:
        pd.DataFrame: Processed trips dataframe with start/end times and stops
    """
    try:
        logging.info("Processing trip times...")
        
        # Initialize new columns in trips DataFrame
        trips_df['start_time'] = None
        trips_df['end_time'] = None
        trips_df['start_stop'] = None
        trips_df['end_stop'] = None
        
        # Group stop_times by trip_id to get first and last stops
        grouped_stop_times = stop_times_df.groupby('trip_id').agg(
            start_time=('arrival_time', 'first'),
            end_time=('departure_time', 'last'),
            start_stop=('stop_id', 'first'),
            end_stop=('stop_id', 'last')
        ).reset_index()
        
        # Merge with trips dataframe
        merged_trips = trips_df.merge(grouped_stop_times, on='trip_id', how='left')
        
        # Drop redundant columns if they exist
        columns_to_drop = []
        for col in merged_trips.columns:
            if col.endswith('_x') and col.replace('_x', '') in ['start_time', 'end_time', 'start_stop', 'end_stop']:
                columns_to_drop.append(col)
                # Rename the corresponding _y column
                y_col = col.replace('_x', '_y')
                if y_col in merged_trips.columns:
                    merged_trips = merged_trips.rename(columns={y_col: col.replace('_x', '')})
        
        if columns_to_drop:
            merged_trips = merged_trips.drop(columns=columns_to_drop)
        
        logging.info(f"Successfully processed {len(merged_trips)} trips")
        return merged_trips
        
    except Exception as e:
        logging.error(f"Error processing trip times: {str(e)}")
        raise

def validate_processed_data(df: pd.DataFrame) -> bool:
    """
    Validate the processed data for completeness.
    
    Args:
        df (pd.DataFrame): Processed trips dataframe
        
    Returns:
        bool: True if validation passes, False otherwise
    """
    required_columns = [
        'trip_id', 'start_time', 'end_time',
        'start_stop', 'end_stop'
    ]
    
    # Check for required columns
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        logging.error(f"Missing required columns: {missing_columns}")
        return False
    
    # Check for null values in critical columns
    null_counts = df[required_columns].isnull().sum()
    if null_counts.any():
        logging.warning(f"Found null values in columns:\n{null_counts[null_counts > 0]}")
        return False
    
    logging.info("Data validation passed successfully")
    return True

def format_dmrc_trips(output_dir: str = ".") -> None:
    """
    Main function to format DMRC trips data and save to CSV.
    Matches exactly the logic from test1.ipynb.
    
    Args:
        output_dir (str): Directory to save the formatted CSV file
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Load data
        routes, trips, stops, stop_times = load_dmrc_data()
        
        # Process trip times
        processed_trips = process_trip_times(trips, stop_times)
        
        # Validate processed data
        if not validate_processed_data(processed_trips):
            logging.error("Data validation failed. Please check the logs for details.")
            return
        
        # Save to CSV
        output_path = os.path.join(output_dir, "formatted_DMRC_trips.csv")
        processed_trips.to_csv(output_path, index=False)
        logging.info(f"Successfully saved formatted trips to {output_path}")
        
        # Save a backup copy without time columns (as in the notebook)
        backup_path = os.path.join(output_dir, "formatted_trips.csv")
        time_columns = ['start_time', 'end_time', 'start_stop', 'end_stop']
        processed_trips.drop(columns=time_columns).to_csv(backup_path, index=False)
        logging.info(f"Saved backup copy without time columns to {backup_path}")
        
    except Exception as e:
        logging.error(f"Error in format_dmrc_trips: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        format_dmrc_trips()
    except Exception as e:
        logging.error(f"Script execution failed: {str(e)}")
        exit(1) 