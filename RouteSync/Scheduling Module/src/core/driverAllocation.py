import pandas as pd
import numpy as np
import random
import logging
from itertools import combinations
from scipy.spatial.distance import euclidean
from datetime import datetime
import random
import logging
from tqdm import tqdm
import heapq

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Load input data
def load_data():
    logging.info("Loading input data...")  # Log the action
    try:
        schedule = pd.read_csv("best_schedule.csv")
        stops = pd.read_csv("DMRC_Data/stops.txt")  # Load stops data
        if stops is None or stops.empty:
            logging.error("Failed to load stops data or file is empty")
            raise ValueError("Stops data is empty or None")
        logging.info("Data loaded successfully.")
        return schedule, stops
    except Exception as e:
        logging.error(f"Error loading data: {e}")
        raise

# Fix time format for arrival and departure times
def fix_time_format(time_str):
    try:
        # If the input is a datetime string (e.g., "2024-01-01 04:45:00")
        if ' ' in time_str:
            return time_str.split(' ')[1]  # Extract only the time part
        return time_str
    except (ValueError, AttributeError):
        logging.warning(f"Invalid time format encountered: {time_str}")
        return time_str

# Compute distance between two stops based on lat/lon
def haversine(lat1, lon1, lat2, lon2):
    from math import radians, cos, sin, sqrt, atan2

    R = 6371  # Earth's radius in km

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c

# Calculate travel time between stops
def travel_time(stop1, stop2, stops):
    # Ensure stops is not None
    if stops is None:
        logging.error("Stops data is None in travel_time function")
        return 0  # Default value if stops data is not available
        
    try:
        lat1, lon1 = stops.loc[stops['stop_id'] == stop1, ['stop_lat', 'stop_lon']].values[0]
        lat2, lon2 = stops.loc[stops['stop_id'] == stop2, ['stop_lat', 'stop_lon']].values[0]
        distance = haversine(lat1, lon1, lat2, lon2)
        return distance / 50 * 60  # Assume average speed of 50 km/h
    except Exception as e:
        logging.error(f"Error calculating travel time: {e}")
        return 0  # Default value in case of error

def initialize_population(schedule, max_drivers, stops=None):
    # Preprocess schedule into a dictionary for faster lookups
    trip_dict = {
        bus: {
            "start_time": row["start_time"],
            "end_time": row["end_time"]
        }
        for bus, row in schedule.set_index("bus_id").iterrows()
    }
    
    # Sort schedule by start time
    buses = sorted(trip_dict.keys(), key=lambda x: trip_dict[x]["start_time"])
    
    population = []
    
    for i in range(25):  # Population size
        allocation = [[] for _ in range(max_drivers)]
        unallocated = 0
        driver_heap = []  # Priority queue to track driver availability
        logging.info(f"Creating population {i}")

        
        for _ in range(max_drivers):
            driver = random.randint(0, max_drivers - 1)
            heapq.heappush(driver_heap, (0, driver))  # Initialize all drivers as available at time 0
        
        for trip in buses:
            trip_start = trip_dict[trip]["start_time"]
            trip_end = trip_dict[trip]["end_time"]
            
            allocated = False
            for _, driver in driver_heap:
                if allocation[driver] and trip_start < trip_dict[allocation[driver][-1]]["end_time"] + 50 * 60:
                    continue  # Skip if the trip overlaps with the last trip on this driver
                allocation[driver].append(trip)
                heapq.heappush(driver_heap, (trip_end, driver))
                allocated = True    
                break

            if not allocated:
                unallocated += 1

        logging.info(f"{unallocated} schedule not allocated...")
        population.append(allocation)
    
    logging.info("Population initialized.")
    return population

def fitness(allocation, schedule, stops):
    # Validate inputs
    if stops is None:
        logging.error("Stops data is None. Cannot calculate fitness.")
        return float('inf')  # Invalid solution with worst possible fitness
        
    # Initialize metrics
    total_drivers = len(allocation)
    active_drivers = 0
    total_trips_assigned = 0
    total_overlap_time = 0
    total_active_time = 0
    total_idle_time = 0
    total_distance = 0
    max_trips_per_driver = 0
    min_trips_per_driver = float('inf')
    
    # Break time and work hour constraints
    MIN_BREAK_TIME = 30  # Minimum break time in minutes
    MAX_WORK_HOURS = 8 * 60  # Maximum work hours in minutes (8 hours)
    break_violations = 0
    work_hour_violations = 0

    # Pre-fetch stop coordinates for faster access
    stop_coords = stops.set_index('stop_id')[['stop_lat', 'stop_lon']].to_dict('index')

    # Pre-fetch trip data for quick lookup
    trip_data = schedule.set_index('bus_id')[['start_stop', 'end_stop', 'start_time', 'end_time']]

    # Analyze each driver's schedule
    for driver_schedule in allocation:
        if not driver_schedule:  # Skip empty schedules
            continue
            
        active_drivers += 1
        trips_this_driver = len(driver_schedule)
        total_trips_assigned += trips_this_driver
        
        # Update min/max trips per driver
        max_trips_per_driver = max(max_trips_per_driver, trips_this_driver)
        min_trips_per_driver = min(min_trips_per_driver, trips_this_driver)

        # Track driver's work day
        driver_first_trip_start = None
        driver_last_trip_end = None
        driver_active_time = 0
        driver_breaks = []

        # Sort trips by start time to ensure correct sequence
        valid_trips = []
        for bus in driver_schedule:
            if bus in trip_data.index:
                # Get the start time as a scalar value using .iloc[0]
                start_time = trip_data.loc[[bus], 'start_time'].iloc[0]
                valid_trips.append((bus, start_time))
        
        # Sort by start time
        valid_trips.sort(key=lambda x: x[1])
        sorted_schedule = [trip[0] for trip in valid_trips]  # Extract just the bus IDs

        # Analyze consecutive trips
        for i in range(len(sorted_schedule)):
            bus = sorted_schedule[i]
            
            if bus not in trip_data.index:
                continue

            # Get current trip details
            trip = trip_data.loc[[bus]].iloc[0]
            start_stop = str(trip['start_stop'])
            end_stop = str(trip['end_stop'])
            trip_start_time = trip['start_time']
            trip_end_time = trip['end_time']

            # Update driver's work day tracking
            if driver_first_trip_start is None:
                driver_first_trip_start = trip_start_time
            driver_last_trip_end = trip_end_time

            # Calculate active time for this trip (in minutes)
            trip_duration = (trip_end_time - trip_start_time) / 60e9  # Convert nanoseconds to minutes
            driver_active_time += trip_duration
            total_active_time += trip_duration

            # Calculate distance for this trip
            try:
                if start_stop in stop_coords and end_stop in stop_coords:
                    lat1, lon1 = stop_coords[start_stop]['stop_lat'], stop_coords[start_stop]['stop_lon']
                    lat2, lon2 = stop_coords[end_stop]['stop_lat'], stop_coords[end_stop]['stop_lon']
                    distance = haversine(lat1, lon1, lat2, lon2)
                    total_distance += distance
            except Exception as e:
                logging.warning(f"Could not calculate distance for stops {start_stop} -> {end_stop}: {e}")

            # Check for overlaps and calculate idle time with next trip
            if i < len(sorted_schedule) - 1:
                next_bus = sorted_schedule[i + 1]
                if next_bus in trip_data.index:
                    next_trip = trip_data.loc[[next_bus]].iloc[0]
                    next_start_time = next_trip['start_time']
                    
                    # Calculate overlap time if any (in minutes)
                    if trip_end_time > next_start_time:
                        overlap_duration = (trip_end_time - next_start_time) / 60e9  # Convert nanoseconds to minutes
                        total_overlap_time += overlap_duration
                    else:
                        # Calculate break time between trips (in minutes)
                        break_time = (next_start_time - trip_end_time) / 60e9  # Convert nanoseconds to minutes
                        if break_time < MIN_BREAK_TIME:
                            break_violations += 1
                        driver_breaks.append(break_time)
                        total_idle_time += break_time

        # Check work hour violations (in minutes)
        if driver_first_trip_start is not None and driver_last_trip_end is not None:
            total_work_time = (driver_last_trip_end - driver_first_trip_start) / 60e9  # Convert nanoseconds to minutes
            if total_work_time > MAX_WORK_HOURS:
                work_hour_violations += 1

    # Calculate metrics
    if active_drivers == 0:
        return float('inf')  # Invalid solution

    avg_trips_per_driver = total_trips_assigned / active_drivers
    trip_distribution_score = 1 - (max_trips_per_driver - min_trips_per_driver) / max(max_trips_per_driver, 1)
    driver_utilization = active_drivers / total_drivers
    
    # Time efficiency metrics (ensure positive values)
    total_time = max(total_active_time + total_idle_time, 1)
    active_time_ratio = total_active_time / total_time if total_time > 0 else 0
    
    # Penalties
    overlap_penalty = total_overlap_time * 2.0        # Heavy penalty for overlaps
    break_penalty = break_violations * 3.0            # Very heavy penalty for insufficient breaks
    work_hour_penalty = work_hour_violations * 5.0    # Severe penalty for exceeding work hours
    idle_penalty = (total_idle_time / total_time) * 0.5 if total_time > 0 else 0  # Moderate penalty for idle time
    underutilization_penalty = (1 - driver_utilization) * 0.3  # Small penalty for unused drivers

    # Combine metrics into final fitness score (lower is better)
    fitness_value = (
        1.0 / (active_time_ratio + 0.1) +     # Maximize active time
        overlap_penalty +                      # Penalty for overlaps
        break_penalty +                        # Heavy penalty for break violations
        work_hour_penalty +                    # Severe penalty for work hour violations
        idle_penalty +                         # Penalty for idle time
        underutilization_penalty +             # Penalty for unused drivers
        (1.0 - trip_distribution_score)        # Encourage even trip distribution
    )

    logging.info(
        f"Fitness: {fitness_value:.6f}, "
        f"Active Drivers: {active_drivers}/{total_drivers}, "
        f"Trips/Driver: {avg_trips_per_driver:.2f}, "
        f"Break Violations: {break_violations}, "
        f"Work Hour Violations: {work_hour_violations}, "
        f"Overlaps: {total_overlap_time:.2f}min, "
        f"Active Ratio: {active_time_ratio:.2f}, "
        f"Distance: {total_distance:.2f}km"
    )

    return fitness_value

# Selection
def select(population, fitnesses):
    # Invert fitness values so that lower fitness has higher weight
    max_fitness = max(fitnesses) + 1  # Add 1 to avoid division by zero
    inverted_fitnesses = [max_fitness - fitness for fitness in fitnesses]
    
    # Handle the case where all fitness values are the same
    if sum(inverted_fitnesses) == 0:
        inverted_fitnesses = [1] * len(fitnesses)
    
    # Perform weighted random selection
    selected = random.choices(population, weights=inverted_fitnesses, k=len(population))
    return selected

# Crossover
def crossover(parent1, parent2):
    split = random.randint(0, len(parent1) - 1)
    child1 = parent1[:split] + parent2[split:]
    child2 = parent2[:split] + parent1[split:]
    return child1, child2

# Mutation
def mutate(allocation, buses):
    for _ in range(random.randint(1, 5)):
        if len(allocation) < 2:  # Need at least 2 drivers to swap
            break
        driver1, driver2 = random.sample(range(len(allocation)), 2)
        if allocation[driver1]:  # Ensure driver1 has trips to move
            trip = random.choice(allocation[driver1])
            allocation[driver1].remove(trip)
            allocation[driver2].append(trip)
    return allocation

# Genetic algorithm with periodic export
def genetic_algorithm(schedule, max_drivers, generations=100, export_interval=1, stops=None):
    # Validate inputs
    if stops is None:
        logging.error("Stops data is None in genetic_algorithm. Cannot proceed.")
        raise ValueError("Stops data is required for genetic_algorithm")
        
    logging.info("Initializing genetic algorithm...")
    population = initialize_population(schedule, max_drivers, stops)
    fitness_cache = {}
    best_allocation = None
    best_fitness = float('inf')
    
    def get_fitness(ind):
        key = tuple(tuple(driver) for driver in ind)  # Use tuple representation for caching
        if key not in fitness_cache:
            fitness_cache[key] = fitness(ind, schedule, stops)  # Pass stops to fitness
        return fitness_cache[key]

    for gen in range(generations):
        logging.info(f"Generation {gen + 1}/{generations}: Calculating fitness...")
        # Calculate fitness for each individual and keep track of the best
        current_gen_fitnesses = []
        for ind in population:
            current_fitness = get_fitness(ind)
            current_gen_fitnesses.append(current_fitness)
            # Update best if we found a better solution
            if current_fitness < best_fitness:
                best_fitness = current_fitness
                best_allocation = ind.copy()  # Make a copy to preserve the best

        logging.info(f"Generation {gen + 1}/{generations}: Selection and crossover...")
        
        # Selection and crossover
        population = select(population, current_gen_fitnesses)
        new_population = []
        for i in range(0, len(population) - 1, 2):
            parent1, parent2 = population[i], population[i + 1]
            child1, child2 = crossover(parent1, parent2)
            new_population.extend([child1, child2])
        
        logging.info(f"Generation {gen + 1}/{generations}: Mutation...")
        population = [mutate(ind, schedule['bus_id'].tolist()) for ind in new_population]

        # Log the best fitness of the current generation
        logging.info(f"Generation {gen + 1}/{generations}: Best fitness = {best_fitness:.4f}")

        # Export the best schedule every `export_interval` generations
        if (gen + 1) % export_interval == 0 and best_allocation is not None:
            logging.info(f"Exporting best schedule for generation {gen + 1}...")
            
            # Prepare data for export
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"driver_schedules/best_schedule_driver{max_drivers}_gen{gen + 1}_{timestamp}.csv"
            allocation_data = []
            for i, driver_schedule in enumerate(best_allocation):
                for bus in driver_schedule:
                    allocation_data.append({'driver': i, 'Trip ID': bus})
            
            best_schedule_df = pd.DataFrame(allocation_data)
            best_schedule_df.to_csv(output_file, index=False)
            logging.info(f"Best schedule exported to {output_file}.")

    # Return the best allocation found across all generations
    return best_allocation


if __name__ == "__main__":
    try:
        logging.info("Loading data...")
        schedule, stops = load_data()  # Get both schedule and stops
        
        if stops is None or stops.empty:
            logging.error("Stops data is None or empty after loading.")
            raise ValueError("Stops data is required but is None or empty")

        logging.info(f"Schedule columns: {schedule.columns}")
        logging.info(f"Stops columns: {stops.columns}")

        logging.info("Preprocessing schedule to fix time format...")
        # Extract time component from datetime strings
        schedule['start_time'] = schedule['start_time'].apply(fix_time_format)
        schedule['end_time'] = schedule['end_time'].apply(fix_time_format)
        schedule.sort_values(by='start_time', inplace=True)
        
        # Convert time strings to datetime objects
        schedule['start_time'] = pd.to_datetime(schedule['start_time'], format='%H:%M:%S')
        schedule['end_time'] = pd.to_datetime(schedule['end_time'], format='%H:%M:%S')
        
        # Convert to timestamps (nanoseconds since epoch)
        # First convert to int64 (nanoseconds) then to regular int
        schedule['start_time'] = schedule['start_time'].astype('int64').astype(int)
        schedule['end_time'] = schedule['end_time'].astype('int64').astype(int)
        
        logging.info("Preprocessing completed.")

        # Define ranges for max_drivers and generations
        max_drivers_list = [200, 400, 600]  # Example: different max drivers

        # Create driver_schedules directory if it doesn't exist
        import os
        if not os.path.exists("driver_schedules"):
            os.makedirs("driver_schedules")
            logging.info("Created driver_schedules directory")

        # Iterate through different configurations
        for max_drivers in max_drivers_list:
            logging.info(f"Initializing genetic algorithm with {max_drivers} drivers...")
            best_allocation = genetic_algorithm(schedule, max_drivers, 15, stops=stops)  # Explicitly pass stops parameter

            logging.info("Genetic algorithm completed. Saving best allocation to CSV...")

            # Prepare data for CSV
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"driver_schedules/driver_schedule_{max_drivers}drivers_{timestamp}.csv"

            # Flatten the allocation and prepare it for saving
            allocation_data = []
            for i, driver_schedule in enumerate(best_allocation):
                for bus in driver_schedule:
                    allocation_data.append({
                        'driver': i + 1,
                        'bus_id': bus
                    })

            # Convert to DataFrame and save as CSV
            allocation_df = pd.DataFrame(allocation_data)
            allocation_df.to_csv(output_file, index=False)

            logging.info(f"Best allocation saved to {output_file}.")
    
    except Exception as e:
        logging.error(f"An error occurred in the main program: {e}")
        import traceback
        logging.error(traceback.format_exc())