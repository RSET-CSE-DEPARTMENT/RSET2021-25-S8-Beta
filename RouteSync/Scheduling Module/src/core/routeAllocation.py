import pandas as pd
import numpy as np
import random
from itertools import combinations
from scipy.spatial.distance import euclidean

# Load input data
def load_data():
    routes = pd.read_csv("All_Data/routes.txt")
    stops = pd.read_csv("./stop_merge.csv")
    return routes, stops

# Load the precomputed Haversine distances from the CSV file
# def load_distances(filename="haversine_distances.csv"):
#     distances_df = pd.read_csv(filename)
#     # Convert to a dictionary with (stop_id_1, stop_id_2) as keys and distances as values
#     distance_dict = {(row['stop_id_1'], row['stop_id_2']): row['distance_km'] for _, row in distances_df.iterrows()}
#     return distance_dict

# distance_dict = load_distances("haversine_distances.csv")

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
def initialize_population(routes, max_buses):
    population = []
    route_ids = routes['route_id'].tolist()

    for _ in range(100):  # Population size
        allocation = [[] for _ in range(max_buses)]
        for route in route_ids:
            bus = random.randint(0, max_buses - 1)
            allocation[bus].append(route)
        population.append(allocation)
    return population

def fitness(allocation, routes, stops):
    idle_time = 0
    total_distance = 0
    overlap_penalty = 0  # Penalty for overlapping routes

    print("Starting fitness computation...")
    for bus_idx, bus_schedule in enumerate(allocation):
        # Sort the bus schedule by the earliest arrival time of its routes
        bus_schedule.sort(key=lambda route: stops[stops['route_id'] == route]['arrival_time'].min())

        for i in range(len(bus_schedule) - 1):
            route1 = bus_schedule[i]
            route2 = bus_schedule[i + 1]

            last_stop_route1 = stops[stops['route_id'] == route1].iloc[-1]
            first_stop_route2 = stops[stops['route_id'] == route2].iloc[0]

            travel_time_between_routes = travel_time(
                last_stop_route1['stop_id'], first_stop_route2['stop_id'], stops
            )
            time_diff = (pd.to_datetime(first_stop_route2['arrival_time']) - 
                         pd.to_datetime(last_stop_route1['departure_time'])).total_seconds() / 60

            idle_time_increment = max(0, time_diff - travel_time_between_routes)
            idle_time += idle_time_increment

            distance_increment = haversine(
                stops.loc[stops['stop_id'] == last_stop_route1['stop_id'], ['stop_lat', 'stop_lon']].values[0][0],
                stops.loc[stops['stop_id'] == last_stop_route1['stop_id'], ['stop_lat', 'stop_lon']].values[0][1],
                stops.loc[stops['stop_id'] == first_stop_route2['stop_id'], ['stop_lat', 'stop_lon']].values[0][0],
                stops.loc[stops['stop_id'] == first_stop_route2['stop_id'], ['stop_lat', 'stop_lon']].values[0][1],
            )
            total_distance += distance_increment

            # Check for overlapping routes
            route1_end_time = pd.to_datetime(last_stop_route1['departure_time'])
            route2_start_time = pd.to_datetime(first_stop_route2['arrival_time'])
            if route1_end_time > route2_start_time:
                # Add a penalty for overlap (e.g., proportional to overlap duration in minutes)
                overlap_duration = (route1_end_time - route2_start_time).total_seconds() / 60
                overlap_penalty += overlap_duration
                print(f"Overlap detected between routes {route1} and {route2}: {overlap_duration} minutes penalty added.")

    # Modify the fitness value to include the overlap penalty
    fitness_value = 1 / (1 + idle_time + total_distance + overlap_penalty)
    print(f"\nFinal fitness value: {fitness_value:.6f}, Idle Time: {idle_time}, Distance: {total_distance}, Overlap Penalty: {overlap_penalty}")
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
def mutate(allocation, route_ids):
    for _ in range(random.randint(1, 5)):
        bus1, bus2 = random.sample(range(len(allocation)), 2)
        if allocation[bus1]:
            route = random.choice(allocation[bus1])
            allocation[bus1].remove(route)
            allocation[bus2].append(route)
    return allocation

# Genetic algorithm
def genetic_algorithm(routes, stops, max_buses, generations=100):
    print("Initializing population...")
    population = initialize_population(routes, max_buses)
    print("Population initialized.")

    for gen in range(generations):
        print(f"Generation {gen + 1}/{generations}: Calculating fitness...")
        fitnesses = [fitness(ind, routes, stops) for ind in population]
        print(f"Generation {gen + 1}/{generations}: Selection and crossover...")
        population = select(population, fitnesses)

        new_population = []
        for i in range(0, len(population), 2):
            parent1, parent2 = population[i], population[i + 1]
            child1, child2 = crossover(parent1, parent2)
            new_population.extend([child1, child2])

        print(f"Generation {gen + 1}/{generations}: Mutation...")
        population = [mutate(ind, routes['route_id'].tolist()) for ind in new_population]

        # Optional: Display the best fitness in this generation
        best_fitness = max(fitnesses)
        print(f"Generation {gen + 1}/{generations}: Best fitness = {best_fitness:.4f}")

    print("Selecting the best allocation...")
    best_allocation = max(population, key=lambda ind: fitness(ind, routes, stops))
    return best_allocation

if __name__ == "__main__":
    print("Loading data...")
    routes, stops = load_data()
    print("Data loaded successfully.")

    print("Preprocessing stops to fix time format...")
    stops['arrival_time'] = stops['arrival_time'].apply(fix_time_format)
    stops['departure_time'] = stops['departure_time'].apply(fix_time_format)
    print("Preprocessing completed.")

    max_buses = 5000
    generations = 5  # Set the number of generations

    print(f"Initializing genetic algorithm with {max_buses} buses and {generations} generations...")
    best_allocation = genetic_algorithm(routes, stops, max_buses, generations)

    print("Genetic algorithm completed. Displaying best allocation:")
    for i, bus_schedule in enumerate(best_allocation):
        print(f"Bus {i + 1}: {bus_schedule}")

