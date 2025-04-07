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
    trips = pd.read_csv("formatted_DMRC_trips.csv")
    stops = pd.read_csv("DMRC_Data/stops.txt")
    logging.info("Data loaded successfully.")
    return trips, stops

# Fix time format for arrival and departure times
def fix_time_format(time_str):
    try:
        hours, minutes, seconds = map(int, time_str.split(":"))
        if hours >= 24:
            hours -= 24
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    except ValueError:
        # Return the original string if it's not a valid time format
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
    lat1, lon1 = stops.loc[stops['stop_id'] == stop1, ['stop_lat', 'stop_lon']].values[0]
    lat2, lon2 = stops.loc[stops['stop_id'] == stop2, ['stop_lat', 'stop_lon']].values[0]
    distance = haversine(lat1, lon1, lat2, lon2)
    return distance / 50 * 60  # Assume average speed of 50 km/h

def initialize_population(trips, max_buses):
    trip_dict = {
        trip_id: {
            "start_time_y": row["start_time_y"],
            "end_time_y": row["end_time_y"]
        }
        for trip_id, row in trips.set_index("trip_id").iterrows()
    }
    
    trip_ids = sorted(trip_dict.keys(), key=lambda x: trip_dict[x]["start_time_y"])
    
    population = []
    
    for i in range(10):  # Population size
        allocation = [[] for _ in range(max_buses)]
        unallocated = 0
        bus_heap = []
        logging.info(f"Creating population {i}")

        # Randomized initialization of bus_heap
        bus_ids = list(range(max_buses))
        random.shuffle(bus_ids)
        for bus in bus_ids:
            initial_time = random.randint(0, 10 * 60)  # Randomize availability time
            heapq.heappush(bus_heap, (initial_time, bus))

        # Randomized trip order
        random_trip_ids = trip_ids[:]
        # random.shuffle(random_trip_ids)

        for trip in random_trip_ids:
            trip_start = trip_dict[trip]["start_time_y"] + random.randint(-5 * 60, 5 * 60)  # Shift timing
            trip_end = trip_start + (trip_dict[trip]["end_time_y"] - trip_dict[trip]["start_time_y"])

            allocated = False
            # Randomized bus selection
            available_buses = [(_, bus) for _, bus in bus_heap if allocation[bus] == [] or 
                               trip_start >= trip_dict[allocation[bus][-1]]["end_time_y"] + 20 * 60]

            if available_buses:
                _, bus = random.choice(available_buses)
                allocation[bus].append(trip)
                heapq.heappush(bus_heap, (trip_end, bus))
                allocated = True
            else:
                unallocated += 1

        logging.info(f"{unallocated} trips not allocated...")
        population.append(allocation)
    
    logging.info("Population initialized.")
    return population

def fitness(allocation, trips, stops):
    bus_utilization = 0
    bus_unutilization = 0
    overlap_penalty = 0
    total_active_time = 0
    total_idle_time = 0
    total_active_distance = 0

    # Pre-fetch stop coordinates for faster access
    stop_coords = stops.set_index('stop_id')[['stop_lat', 'stop_lon']].to_dict('index')

    # Pre-fetch trip data for quick lookup
    trip_data = trips.set_index('trip_id')[['start_stop_y', 'end_stop_y', 'start_time_y', 'end_time_y']]

    # Iterate through bus schedules
    for bus_schedule in allocation:
        if (len(bus_schedule) == 0):  # Skip buses with no trips
            continue
        bus_utilization += 1  # Count buses with assigned trips

        for i in range(len(bus_schedule)):
            trip_id = bus_schedule[i]

            # Ensure the trip exists in the dataset
            if trip_id not in trip_data.index:
                logging.warning(f"Trip {trip_id} not found in trips.")
                continue

            # Extract trip details
            trip = trip_data.loc[trip_id]
            start_stop, end_stop = trip['start_stop_y'], trip['end_stop_y']
            trip_start_time = pd.to_datetime(trip['start_time_y'])
            trip_end_time = pd.to_datetime(trip['end_time_y'])

            # Calculate active time
            trip_duration = (trip_end_time - trip_start_time).total_seconds() / 60
            total_active_time += trip_duration

            # Calculate distance traveled during the trip
            if start_stop in stop_coords and end_stop in stop_coords:
                lat1, lon1 = stop_coords[start_stop]['stop_lat'], stop_coords[start_stop]['stop_lon']
                lat2, lon2 = stop_coords[end_stop]['stop_lat'], stop_coords[end_stop]['stop_lon']
                total_active_distance += haversine(lat1, lon1, lat2, lon2)

            # For subsequent trips, calculate idle time and overlap penalty
            if i < len(bus_schedule) - 1:
                next_trip_id = bus_schedule[i + 1]

                # Ensure the next trip exists in the dataset
                if next_trip_id not in trip_data.index:
                    logging.warning(f"Next trip {next_trip_id} not found in trips.")
                    continue

                # Extract next trip details
                next_trip = trip_data.loc[next_trip_id]
                next_trip_start_time = pd.to_datetime(next_trip['start_time_y'])

                # Calculate idle time
                idle_time = (next_trip_start_time - trip_end_time).total_seconds() / 60
                total_idle_time += max(idle_time, 0)  # Only count positive idle times

                # Calculate overlap penalty
                if trip_end_time > next_trip_start_time:
                    overlap_penalty += 1

    # Normalize parameters for fitness calculation
    bus_utilization_normalized = bus_utilization / len(allocation)  # Proportion of buses used
    overlap_penalty_normalized = overlap_penalty / sum(len(bus_schedule) for bus_schedule in allocation) * 1000
    activity_ratio = total_active_time / max(total_idle_time, 1)  # Avoid division by zero
    total_active_distance_normalized = total_active_distance / 1000  # Scale distance to kilometers

    # Combine into a single fitness value (smaller values are better)
    fitness_value = (
        1 / max(bus_utilization_normalized, 1) +
        overlap_penalty_normalized * 1000 +
        1 / max(activity_ratio, 1) +  # Inverse for minimization
        total_active_distance_normalized
    )

    logging.info(
        f"Fitness: {fitness_value:.6f}, Bus Utilization: {bus_utilization}, Overlaps: {overlap_penalty}, "
        f"Activity Ratio: {activity_ratio}, Active Distance: {total_active_distance:.2f} km"
    )

    return fitness_value


# Selection
def select(population, fitnesses):
    inverted_fitnesses = [1 / (f + 1e-6) for f in fitnesses]  # Add small value to avoid division by zero
    selected = random.choices(population, weights=fitnesses, k=len(population))
    return selected

# Crossover
def crossover(parent1, parent2):
    split = random.randint(0, len(parent1) - 1)
    child1 = parent1[:split] + parent2[split:]
    child2 = parent2[:split] + parent1[split:]
    return child1, child2

# Mutation
# def mutate(allocation, trip_ids):
#     for _ in range(random.randint(1, 5)):
#         bus1, bus2 = random.sample(range(len(allocation)), 2)
#         if allocation[bus1]:
#             trip = random.choice(allocation[bus1])
#             allocation[bus1].remove(trip)
#             allocation[bus2].append(trip)
#     return allocation

def mutate(allocation, trip_ids, trip_dict):
    """
    Mutates an allocation by randomly transferring trips between buses without causing overlaps.

    Args:
        allocation (list): Current allocation of trips to buses.
        trip_ids (list): List of trip IDs.
        trip_dict (dict): Dictionary containing trip start and end times.

    Returns:
        list: Mutated allocation.
    """
    for _ in range(random.randint(1, 5)):  # Random number of mutations
        bus1, bus2 = random.sample(range(len(allocation)), 2)
        
        if allocation[bus1]:
            trip = random.choice(allocation[bus1])  # Choose a random trip from bus1
            
            # Temporarily remove the trip from bus1
            allocation[bus1].remove(trip)
            
            # Check if the trip can be added to bus2 without causing overlaps
            can_add = True
            trip_start = trip_dict[trip]["start_time_y"]
            trip_end = trip_dict[trip]["end_time_y"]
            
            for assigned_trip in allocation[bus2]:
                assigned_start = trip_dict[assigned_trip]["start_time_y"]
                assigned_end = trip_dict[assigned_trip]["end_time_y"]
                
                # Check for overlap
                if not (trip_end + 10 * 60 <= assigned_start or trip_start >= assigned_end + 10 * 60):
                    can_add = False
                    break
            
            if can_add:
                allocation[bus2].append(trip)  # Add trip to bus2 if no overlap
            else:
                allocation[bus1].append(trip)  # Restore trip to bus1 if it can't be moved
    return allocation


# # Genetic algorithm
# def genetic_algorithm(trips, stops, max_buses, generations=100):
#     logging.info("Initializing genetic algorithm...")

#     population = initialize_population(trips, max_buses)

#     for gen in range(generations):
#         logging.info(f"Generation {gen + 1}/{generations}: Calculating fitness...")
#         fitnesses = [fitness(ind, trips, stops) for ind in population]
#         logging.info(f"Generation {gen + 1}/{generations}: Selection and crossover...")

#         population = select(population, fitnesses)

#         new_population = []
#         for i in range(0, len(population) - 1, 2):
#             parent1, parent2 = population[i], population[i + 1]
#             child1, child2 = crossover(parent1, parent2)
#             new_population.extend([child1, child2])

#         logging.info(f"Generation {gen + 1}/{generations}: Mutation...")
#         population = [mutate(ind, trips['trip_id'].tolist()) for ind in new_population]

#         best_fitness = max(fitnesses)
#         logging.info(f"Generation {gen + 1}/{generations}: Best fitness = {best_fitness:.4f}")

#     logging.info("Selecting the best allocation...")
#     best_allocation = max(population, key=lambda ind: fitness(ind, trips, stops))
#     return best_allocation

# Genetic algorithm with periodic export
# def genetic_algorithm(trips, stops, max_buses, generations=100, export_interval=5):
#     logging.info("Initializing genetic algorithm...")
#     population = initialize_population(trips, max_buses)

#     for gen in range(generations):
#         logging.info(f"Generation {gen + 1}/{generations}: Calculating fitness...")
#         fitnesses = [fitness(ind, trips, stops) for ind in population]
#         logging.info(f"Generation {gen + 1}/{generations}: Selection and crossover...")
        
#         # Selection and crossover
#         population = select(population, fitnesses)
#         new_population = []
#         for i in range(0, len(population) - 1, 2):
#             parent1, parent2 = population[i], population[i + 1]
#             child1, child2 = crossover(parent1, parent2)
#             new_population.extend([child1, child2])
        
#         logging.info(f"Generation {gen + 1}/{generations}: Mutation...")
#         population = [mutate(ind, trips['trip_id'].tolist()) for ind in new_population]

#         # Log the best fitness of the current generation
#         best_fitness = max(fitnesses)
#         logging.info(f"Generation {gen + 1}/{generations}: Best fitness = {best_fitness:.4f}")

#         # Export the best schedule every `export_interval` generations
#         if (gen + 1) % export_interval == 0:
#             logging.info(f"Exporting best schedule for generation {gen + 1}...")
#             best_allocation = max(population, key=lambda ind: fitness(ind, trips, stops))
            
#             # Prepare data for export
#             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#             output_file = f"best_schedule_bus{max_buses}_gen{gen + 1}_{timestamp}.csv"
#             allocation_data = []
#             for i, bus_schedule in enumerate(best_allocation):
#                 for trip_id in bus_schedule:
#                     allocation_data.append({'Bus': i, 'Trip ID': trip_id})
            
#             best_schedule_df = pd.DataFrame(allocation_data)
#             best_schedule_df.to_csv(output_file, index=False)
#             logging.info(f"Best schedule exported to {output_file}.")

#     # Final export after all generations
#     logging.info("Selecting the best allocation...")
#     best_allocation = max(population, key=lambda ind: fitness(ind, trips, stops))
#     return best_allocation

# Genetic algorithm with periodic export
def genetic_algorithm(trips, stops, max_buses, generations=100, export_interval=5):
    """
    Runs a genetic algorithm to allocate trips to buses while optimizing based on fitness.
    
    Args:
        trips (DataFrame): Trip data containing trip_id, start_time_y, and end_time_y.
        stops (DataFrame): Stop data (used in fitness calculations).
        max_buses (int): Maximum number of buses available.
        generations (int): Number of generations to run.
        export_interval (int): Interval for exporting the best schedule.
    
    Returns:
        list: The best allocation of trips to buses.
    """
    logging.info("Initializing genetic algorithm...")
    
    # Create trip_dict for faster lookups
    trip_dict = {
        trip_id: {
            "start_time_y": row["start_time_y"],
            "end_time_y": row["end_time_y"]
        }
        for trip_id, row in trips.set_index("trip_id").iterrows()
    }
    
    # Initialize population
    population = initialize_population(trips, max_buses)

    fitnesses = []  # Initialize outside the loop to hold fitness scores

    for gen in range(generations):
        logging.info(f"Generation {gen + 1}/{generations}: Calculating fitness...")
        
        # Calculate fitness only for new individuals
        fitnesses = [fitness(ind, trips, stops) for ind in population]
        
        logging.info(f"Generation {gen + 1}/{generations}: Selection and crossover...")
        # Selection and crossover
        population = select(population, fitnesses)
        new_population = []
        for i in range(0, len(population) - 1, 2):
            parent1, parent2 = population[i], population[i + 1]
            child1, child2 = crossover(parent1, parent2)
            new_population.extend([child1, child2])
        
        logging.info(f"Generation {gen + 1}/{generations}: Mutation...")
        # Apply the updated mutate function to prevent overlaps
        population = [mutate(ind, trips['trip_id'].tolist(), trip_dict) for ind in new_population]

        # Log the best fitness of the current generation
        best_fitness = min(fitnesses)
        logging.info(f"Generation {gen + 1}/{generations}: Best fitness = {best_fitness:.4f}")

        # Export the best schedule every `export_interval` generations
        logging.info(f"Exporting best schedule for generation {gen + 1}...")
        best_index = fitnesses.index(max(fitnesses))  # Use stored fitnesses
        best_allocation = population[best_index]
        
        # Prepare data for export
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"collected_schedules/best_schedule_bus{max_buses}_gen{gen + 1}.csv"
        allocation_data = []
        for i, bus_schedule in enumerate(best_allocation):
            for trip_id in bus_schedule:
                allocation_data.append({'bus': i, 'trip_id': trip_id})
        
        best_schedule_df = pd.DataFrame(allocation_data)
        best_schedule_df.to_csv(output_file, index=False)
        logging.info(f"Best schedule exported to {output_file}.")

    # Final export after all generations
    logging.info("Selecting the best allocation...")
    best_index = fitnesses.index(max(fitnesses))  # Use stored fitnesses
    best_allocation = population[best_index]
    return best_allocation

if __name__ == "__main__":
    logging.info("Loading data...")
    trips, stops = load_data()

    print(trips.columns)

    logging.info("Preprocessing trips to fix time format...")
    trips['start_time_y'] = trips['start_time_y'].apply(fix_time_format)
    trips['end_time_y'] = trips['end_time_y'].apply(fix_time_format)
    trips.sort_values(by='start_time_y', inplace=True)
    
    # Specify the datetime format explicitly
    datetime_format = "%H:%M:%S"  # Adjust this format to match your actual datetime strings

    # Convert start_time_y and end_time_y to timestamps
    trips['start_time_y'] = pd.to_datetime(trips['start_time_y'], format=datetime_format).astype(int)
    trips['end_time_y'] = pd.to_datetime(trips['end_time_y'], format=datetime_format).astype(int)
    
    logging.info("Preprocessing completed.")

    # Define ranges for max_buses and generations
    max_buses_list = [600, 800, 1000]  # Example: different max buses

    # Iterate through different configurations
    for max_buses in max_buses_list:
        logging.info(f"Initializing genetic algorithm with {max_buses} buses...")
        best_allocation = genetic_algorithm(trips, stops, max_buses, 15)

        logging.info("Genetic algorithm completed. Saving best allocation to CSV...")

        # Prepare data for CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"bus_schedule_{max_buses}buses_{timestamp}.csv"

        # Flatten the allocation and prepare it for saving
        allocation_data = []
        for i, bus_schedule in enumerate(best_allocation):
            for trip_id in bus_schedule:
                allocation_data.append({
                    'bus': i + 1,
                    'trip_id': trip_id
                })

        # Convert to DataFrame and save as CSV
        allocation_df = pd.DataFrame(allocation_data)
        allocation_df.to_csv(output_file, index=False)

        logging.info(f"Best allocation saved to {output_file}.")


