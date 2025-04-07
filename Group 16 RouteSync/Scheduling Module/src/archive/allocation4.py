import pandas as pd
import numpy as np
import random
import logging
from itertools import combinations
from scipy.spatial.distance import euclidean
from datetime import datetime

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Load input data
def load_data():
    logging.info("Loading input data...")  # Log the action
    trips = pd.read_csv("DMRC_Data/trips.txt")
    stops = pd.read_csv("DMRC_Data/stops.txt")
    stop_times = pd.read_csv("DMRC_Data/stop_times.txt")
    logging.info("Data loaded successfully.")
    return trips, stops, stop_times

# Fix time format for arrival and departure times
def fix_time_format(time_str):
    """Convert times like 24:xx:xx to 00:xx:xx (next day logic)."""
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

# Initialize population
def initialize_population(trips, max_buses):
    population = []
    trip_ids = trips['trip_id'].tolist()

    for _ in range(100):  # Population size
        allocation = [[] for _ in range(max_buses)]
        for trip in trip_ids:
            bus = random.randint(0, max_buses - 1)
            allocation[bus].append(trip)
        population.append(allocation)
    
    logging.info("Population initialized.")
    return population

def fitness(allocation, trips, stop_times, stops):
    idle_time = 0
    total_distance = 0
    overlap_penalty = 0  # Penalty for overlapping trips

    logging.info("Calculating fitness...")

    for bus_idx, bus_schedule in enumerate(allocation):
        bus_schedule.sort(key=lambda trip: stop_times[stop_times['trip_id'] == trip]['arrival_time'].min())

        for i in range(len(bus_schedule) - 1):
            trip1 = bus_schedule[i]
            trip2 = bus_schedule[i + 1]

            last_stop_trip1 = stop_times[stop_times['trip_id'] == trip1].iloc[-1]
            first_stop_trip2 = stop_times[stop_times['trip_id'] == trip2].iloc[0]

            travel_time_between_trips = travel_time(
                last_stop_trip1['stop_id'], first_stop_trip2['stop_id'], stops
            )
            time_diff = (pd.to_datetime(first_stop_trip2['arrival_time']) - 
                         pd.to_datetime(last_stop_trip1['departure_time'])).total_seconds() / 60

            idle_time_increment = max(0, time_diff - travel_time_between_trips)
            idle_time_increment = travel_time_between_trips
            idle_time += idle_time_increment

            distance_increment = haversine(
                stops.loc[stops['stop_id'] == last_stop_trip1['stop_id'], ['stop_lat', 'stop_lon']].values[0][0],
                stops.loc[stops['stop_id'] == last_stop_trip1['stop_id'], ['stop_lat', 'stop_lon']].values[0][1],
                stops.loc[stops['stop_id'] == first_stop_trip2['stop_id'], ['stop_lat', 'stop_lon']].values[0][0],
                stops.loc[stops['stop_id'] == first_stop_trip2['stop_id'], ['stop_lat', 'stop_lon']].values[0][1],
            )
            total_distance += distance_increment

            # Check for overlapping trips
            trip1_end_time = pd.to_datetime(last_stop_trip1['departure_time'])
            trip2_start_time = pd.to_datetime(first_stop_trip2['arrival_time'])
            if trip1_end_time > trip2_start_time:
                overlap_duration = (trip1_end_time - trip2_start_time).total_seconds() / 60
                overlap_penalty += overlap_duration

    fitness_value = 1 / (1 + idle_time + total_distance + overlap_penalty)

    logging.info(f"Final fitness value: {fitness_value:.6f}, Idle Time: {idle_time}, Distance: {total_distance}, Overlapping: {overlap_penalty}")
    return fitness_value  # Minimize idle time, distance, and overlaps

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
from joblib import Parallel, delayed

def genetic_algorithm(trips, stops, stop_times, max_buses, generations=100):
    logging.info("Initializing genetic algorithm...")

    population = initialize_population(trips, max_buses)

    for gen in range(generations):
        logging.info(f"Generation {gen + 1}/{generations}: Calculating fitness...")
        
        # Parallelize fitness calculation
        fitnesses = Parallel(n_jobs=-1)(
            delayed(fitness)(ind, trips, stop_times, stops) for ind in population
        )

        logging.info(f"Generation {gen + 1}/{generations}: Selection and crossover...")
        
        population = select(population, fitnesses)

        new_population = []
        for i in range(0, len(population), 2):
            parent1, parent2 = population[i], population[i + 1]
            child1, child2 = crossover(parent1, parent2)
            new_population.extend([child1, child2])

        logging.info(f"Generation {gen + 1}/{generations}: Mutation...")
        
        # Parallelize mutation
        population = Parallel(n_jobs=-1)(
            delayed(mutate)(ind, trips['trip_id'].tolist()) for ind in new_population
        )

        best_fitness = max(fitnesses)
        logging.info(f"Generation {gen + 1}/{generations}: Best fitness = {best_fitness:.4f}")

    logging.info("Selecting the best allocation...")
    
    # Parallelize best allocation selection
    best_allocation = max(
        Parallel(n_jobs=-1)(
            delayed(lambda ind: (ind, fitness(ind, trips, stop_times, stops)))(ind) for ind in population
        ),
        key=lambda x: x[1]
    )[0]

    return best_allocation

if __name__ == "__main__":
    logging.info("Loading data...")
    trips, stops, stop_times = load_data()

    logging.info("Preprocessing stop_times to fix time format...")
    stop_times['arrival_time'] = stop_times['arrival_time'].apply(fix_time_format)
    stop_times['departure_time'] = stop_times['departure_time'].apply(fix_time_format)
    logging.info("Preprocessing completed.")

    max_buses = 5000
    generations = 5  # Set the number of generations

    logging.info(f"Initializing genetic algorithm with {max_buses} buses and {generations} generations...")
    best_allocation = genetic_algorithm(trips, stops, stop_times, max_buses, generations)

    logging.info("Genetic algorithm completed. Saving best allocation to CSV...")

    # Prepare data for CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Create a timestamp
    output_file = f"bus_schedule_{timestamp}.csv"  # Generate file name

    # Flatten the allocation and prepare it for saving
    allocation_data = []
    for i, bus_schedule in enumerate(best_allocation):
        for trip_id in bus_schedule:
            allocation_data.append({
                'Bus Number': i + 1,
                'Trip ID': trip_id
            })

    # Convert to DataFrame and save as CSV
    allocation_df = pd.DataFrame(allocation_data)
    allocation_df.to_csv(output_file, index=False)

    logging.info(f"Best allocation saved to {output_file}.")

