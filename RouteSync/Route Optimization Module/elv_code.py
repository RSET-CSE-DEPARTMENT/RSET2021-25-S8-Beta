import pandas as pd
import numpy as np
import random
from itertools import combinations
from scipy.spatial.distance import euclidean

# Load input data
def load_data():
    trips = pd.read_csv("trips.csv")
    stops = pd.read_csv("stops.csv")
    stop_times = pd.read_csv("stop_times.csv")
    return trips, stops, stop_times

def fix_time_format(time_str):
    """Convert times like 24:xx:xx to 00:xx:xx (next day logic)."""
    try:
        hours, minutes, seconds = map(int, time_str.split(":"))
        if hours >= 24:
            hours -= 24
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    except ValueError:
        # Return the original string if it's not a valid time format
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
    return population

# Fitness function
def fitness(allocation, trips, stop_times, stops):
    idle_time = 0
    total_distance = 0

    for bus_schedule in allocation:
        bus_schedule.sort(key=lambda trip: stop_times[stop_times['trip_id'] == trip]['arrival_time'].min())

        for i in range(len(bus_schedule) - 1):
            trip1 = bus_schedule[i]
            trip2 = bus_schedule[i + 1]

            last_stop_trip1 = stop_times[stop_times['trip_id'] == trip1].iloc[-1]
            first_stop_trip2 = stop_times[stop_times['trip_id'] == trip2].iloc[0]

            travel_time_between_trips = travel_time(
                last_stop_trip1['stop_id'], first_stop_trip2['stop_id'], stops
            )
            
            time_diff = (pd.to_datetime(first_stop_trip2['arrival_time']) - pd.to_datetime(last_stop_trip1['departure_time'])).total_seconds() / 60
            idle_time += max(0, time_diff - travel_time_between_trips)

            # idle_time += max(0, pd.to_datetime(first_stop_trip2['arrival_time']) - pd.to_datetime(last_stop_trip1['departure_time']).total_seconds() / 60 - travel_time_between_trips)
            total_distance += haversine(
                stops.loc[stops['stop_id'] == last_stop_trip1['stop_id'], ['stop_lat', 'stop_lon']].values[0][0],
                stops.loc[stops['stop_id'] == last_stop_trip1['stop_id'], ['stop_lat', 'stop_lon']].values[0][1],
                stops.loc[stops['stop_id'] == first_stop_trip2['stop_id'], ['stop_lat', 'stop_lon']].values[0][0],
                stops.loc[stops['stop_id'] == first_stop_trip2['stop_id'], ['stop_lat', 'stop_lon']].values[0][1],
            )

    return 1 / (1 + idle_time + total_distance)  # Minimize idle time and distance

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
def genetic_algorithm(trips, stops, stop_times, max_buses, generations=100):
    print("Initializing population...")
    population = initialize_population(trips, max_buses)
    print("Population initialized.")

    for gen in range(generations):
        print(f"Generation {gen + 1}/{generations}: Calculating fitness...")
        fitnesses = [fitness(ind, trips, stop_times, stops) for ind in population]
        print(f"Generation {gen + 1}/{generations}: Selection and crossover...")
        population = select(population, fitnesses)

        new_population = []
        for i in range(0, len(population), 2):
            parent1, parent2 = population[i], population[i + 1]
            child1, child2 = crossover(parent1, parent2)
            new_population.extend([child1, child2])

        print(f"Generation {gen + 1}/{generations}: Mutation...")
        population = [mutate(ind, trips['trip_id'].tolist()) for ind in new_population]

        # Optional: Display the best fitness in this generation
        best_fitness = max(fitnesses)
        print(f"Generation {gen + 1}/{generations}: Best fitness = {best_fitness:.4f}")

    print("Selecting the best allocation...")
    best_allocation = max(population, key=lambda ind: fitness(ind, trips, stop_times, stops))
    return best_allocation

if __name__ == "__main__":
    print("Loading data...")
    trips, stops, stop_times = load_data()
    print("Data loaded successfully.")

    print("Preprocessing stop_times to fix time format...")
    stop_times['arrival_time'] = stop_times['arrival_time'].apply(fix_time_format)
    stop_times['departure_time'] = stop_times['departure_time'].apply(fix_time_format)
    print("Preprocessing completed.")

    max_buses = 1000
    generations = 100  # Set the number of generations

    print(f"Initializing genetic algorithm with {max_buses} buses and {generations} generations...")
    best_allocation = genetic_algorithm(trips, stops, stop_times, max_buses, generations)

    print("Genetic algorithm completed. Displaying best allocation:")
    for i, bus_schedule in enumerate(best_allocation):
        print(f"Bus {i + 1}: {bus_schedule}")
