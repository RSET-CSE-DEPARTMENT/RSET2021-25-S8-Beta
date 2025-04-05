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
    # Preprocess trips into a dictionary for faster lookups
    # Specify the datetime format explicitly
    datetime_format = "%H:%M:%S"  # Adjust this format to match your actual datetime strings

    # Convert start_time_y and end_time_y to timestamps
    trips['start_time_y'] = pd.to_datetime(trips['start_time_y'], format=datetime_format).astype(int)
    trips['end_time_y'] = pd.to_datetime(trips['end_time_y'], format=datetime_format).astype(int)

    trip_dict = {
        trip_id: {
            "start_time_y": row["start_time_y"],
            "end_time_y": row["end_time_y"]
        }
        for trip_id, row in trips.set_index("trip_id").iterrows()
    }
    
    # Sort trips by start time
    trip_ids = sorted(trip_dict.keys(), key=lambda x: trip_dict[x]["start_time_y"])
    
    population = []
    
    for i in range(25):  # Population size
        allocation = [[] for _ in range(max_buses)]
        unallocated = 0
        bus_heap = []  # Priority queue to track bus availability
        logging.info(f"Creating population {i}")

        
        for _ in range(max_buses):
            bus = random.randint(0, max_buses - 1)
            heapq.heappush(bus_heap, (0, bus))  # Initialize all buses as available at time 0
        
        for trip in trip_ids:
            trip_start = trip_dict[trip]["start_time_y"]
            trip_end = trip_dict[trip]["end_time_y"]
            
            allocated = False
            for _, bus in bus_heap:
                if allocation[bus] and trip_start < trip_dict[allocation[bus][-1]]["end_time_y"] + 10 * 60:
                    continue  # Skip if the trip overlaps with the last trip on this bus
                allocation[bus].append(trip)
                heapq.heappush(bus_heap, (trip_end, bus))
                allocated = True
                break

            if not allocated:
                unallocated += 1

        # logging.info(f"{unallocated} trips not allocated...")
        population.append(allocation)
    
    logging.info("Population initialized.")
    return population

def fitness(allocation, trips, stops):
    actual_idle_time = 0
    required_idle_time = 0
    total_time = 0
    active_time = 0
    total_distance = 0
    overlap_penalty = 0
    infeasibility_penalty = 0

    # Pre-fetch stop coordinates for faster access
    stop_coords = stops.set_index('stop_id')[['stop_lat', 'stop_lon']].to_dict('index')

    # Pre-fetch trip data for quick lookup
    trip_data = trips.set_index('trip_id')[['start_stop_y', 'end_stop_y', 'start_time_y', 'end_time_y']]
    
    max_idle_time = 250000  # Set an upper bound for idle time
    max_total_distance = 120000  # Set an upper bound for total distance
    max_overlap_penalty = 10  # Set an upper bound for overlap penalties
    max_infeasibility_penalty = 5000  # Set an upper bound for infeasibility penalties

    logging.info("Calculating fitness...")

    # Initialize the progress bar
    total_steps = sum(len(bus_schedule) - 1 for bus_schedule in allocation)
    with tqdm(total=total_steps, desc="Calculating Fitness", unit="pair") as pbar:
        for bus_schedule in allocation:
            for i in range(len(bus_schedule) - 1):
                trip1_id = bus_schedule[i]
                trip2_id = bus_schedule[i + 1]
                

                # Ensure trips exist in the dataset
                if trip1_id not in trip_data.index or trip2_id not in trip_data.index:
                    logging.warning(f"Trip {trip1_id} or {trip2_id} not found in trips.")
                    pbar.update(1)
                    continue

                # Extract trip details
                trip1 = trip_data.loc[trip1_id]
                trip2 = trip_data.loc[trip2_id]

                # Extract stops for the trips
                start_stop1, end_stop1 = trip1['start_stop_y'], trip1['end_stop_y']
                start_stop2, end_stop2 = trip2['start_stop_y'], trip2['end_stop_y']

                # Check if stop coordinates exist
                if end_stop1 not in stop_coords or start_stop2 not in stop_coords:
                    logging.warning(f"Stop coordinates for trips {trip1_id} or {trip2_id} not found.")
                    pbar.update(1)
                    continue

                # Calculate travel time between trips
                travel_time_between_trips = travel_time(end_stop1, start_stop2, stops)

                # Calculate idle time
                trip1_start_time = pd.to_datetime(trip1['start_time_y'])
                trip1_end_time = pd.to_datetime(trip1['end_time_y'])
                trip2_start_time = pd.to_datetime(trip2['start_time_y'])
                trip2_end_time = pd.to_datetime(trip2['end_time_y'])
                
                
                time_diff = (trip2_start_time - trip1_end_time).total_seconds() / 60
                
                active_time += (trip1_end_time - trip1_start_time).total_seconds() / 60
                actual_idle_time += (trip2_start_time - trip1_end_time).total_seconds() / 60
                required_idle_time += travel_time_between_trips
                                
                if(i+1 == len(bus_schedule) - 1):
                    active_time += (trip2_end_time - trip2_start_time).total_seconds() / 60
                    total_time += (trip2_end_time - trip2_start_time).total_seconds() / 60
                
                # Check for infeasibility
                if travel_time_between_trips > time_diff:
                    infeasibility_penalty += 1

                # Calculate distance between trip end and start stops
                lat1, lon1 = stop_coords[end_stop1]['stop_lat'], stop_coords[end_stop1]['stop_lon']
                lat2, lon2 = stop_coords[start_stop2]['stop_lat'], stop_coords[start_stop2]['stop_lon']
                total_distance += haversine(lat1, lon1, lat2, lon2)

                # Optional: Add overlap penalty if trips overlap in time
                if trip1_end_time > trip2_start_time:
                    overlap_penalty += 1

                # Update progress bar
                pbar.update(1)

    # Normalize the factors
    normalized_idle_time = min(actual_idle_time / max_idle_time, 1)
    normalized_total_distance = min(total_distance / max_total_distance, 1)
    normalized_overlap_penalty = min(overlap_penalty / max_overlap_penalty, 1)
    normalized_infeasibility_penalty = min(infeasibility_penalty / max_infeasibility_penalty, 1)

    # Fitness value: lower idle time, distance, overlap, and infeasibility are better
    # fitness_value = 1 / (1 + normalized_idle_time + normalized_total_distance + 
    #                      1000 * normalized_overlap_penalty + 
    #                      10 * normalized_infeasibility_penalty)
    # if overlap_penalty > 0:
    #     fitness_value = 0
    # else:
    fitness_value = 1 / (1 + 1000 * normalized_overlap_penalty + 10 * normalized_infeasibility_penalty)
    fitness_value = (active_time / actual_idle_time) / (1 + 1000 * normalized_overlap_penalty + 10 * normalized_infeasibility_penalty)

    logging.info(
        f"Fitness: {fitness_value:.6f}, Idle Time: {actual_idle_time}, Distance: {total_distance}, "
        f"Overlaps: {overlap_penalty}, Infeasibility: {infeasibility_penalty},"
    )
    logging.info(
        f"Total: {active_time + actual_idle_time}, Active: {active_time}, Actual Idle: {actual_idle_time}, Required Idle: {required_idle_time}"
    )
    return fitness_value


# Selection
def select(population, fitnesses):
    selected = random.choices(population, weights=fitnesses, k=len(population))
    return selected

# Crossover
def crossover(parent1, parent2):
    split = random.randint(0, len(parent1) - 1)
    child1 = parent1[:split] + parent2[split:]
    child2 = parent2[:split] + parent1[split:]
    return child1, child2

# Mutation
def mutate(allocation, trip_ids):
    for _ in range(random.randint(1, 5)):
        bus1, bus2 = random.sample(range(len(allocation)), 2)
        if allocation[bus1]:
            trip = random.choice(allocation[bus1])
            allocation[bus1].remove(trip)
            allocation[bus2].append(trip)
    return allocation

# Genetic algorithm
def genetic_algorithm(trips, stops, max_buses, generations=100):
    logging.info("Initializing genetic algorithm...")

    population = initialize_population(trips, max_buses)

    for gen in range(generations):
        logging.info(f"Generation {gen + 1}/{generations}: Calculating fitness...")
        fitnesses = [fitness(ind, trips, stops) for ind in population]
        logging.info(f"Generation {gen + 1}/{generations}: Selection and crossover...")

        population = select(population, fitnesses)

        new_population = []
        for i in range(0, len(population) - 1, 2):
            parent1, parent2 = population[i], population[i + 1]
            child1, child2 = crossover(parent1, parent2)
            new_population.extend([child1, child2])

        logging.info(f"Generation {gen + 1}/{generations}: Mutation...")
        population = [mutate(ind, trips['trip_id'].tolist()) for ind in new_population]

        best_fitness = max(fitnesses)
        logging.info(f"Generation {gen + 1}/{generations}: Best fitness = {best_fitness:.4f}")

    logging.info("Selecting the best allocation...")
    best_allocation = max(population, key=lambda ind: fitness(ind, trips, stops))
    return best_allocation

if __name__ == "__main__":
    logging.info("Loading data...")
    trips, stops = load_data()

    print(trips.columns)

    logging.info("Preprocessing trips to fix time format...")
    trips['start_time_y'] = trips['start_time_y'].apply(fix_time_format)
    trips['end_time_y'] = trips['end_time_y'].apply(fix_time_format)
    trips.sort_values(by='start_time_y')
    logging.info("Preprocessing completed.")

    max_buses = 800
    generations = 5  # Set the number of generations

    logging.info(f"Initializing genetic algorithm with {max_buses} buses and {generations} generations...")
    best_allocation = genetic_algorithm(trips, stops, max_buses, generations)

    logging.info("Genetic algorithm completed. Saving best allocation to CSV...")

    # Prepare data for CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Create a timestamp
    output_file = f"bus_schedule_{timestamp}.csv"  # Generate file name

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

