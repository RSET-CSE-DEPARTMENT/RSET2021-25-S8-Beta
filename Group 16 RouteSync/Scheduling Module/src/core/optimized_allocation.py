import pandas as pd
import numpy as np
import random
import logging
from itertools import combinations
from datetime import datetime
import heapq
from typing import List, Dict, Tuple, Set
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import os
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='allocation.log'
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

@dataclass
class Trip:
    """Data class to store trip information"""
    trip_id: str
    start_time: pd.Timestamp
    end_time: pd.Timestamp
    start_stop: str
    end_stop: str
    distance: float = 0.0
    route_id: str = ""

class BusAllocationOptimizer:
    def __init__(self, 
                 population_size: int = 50,
                 mutation_rate: float = 0.1,
                 elite_size: int = 5,
                 tournament_size: int = 3):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.elite_size = elite_size
        self.tournament_size = tournament_size
        self.cache = {}
        
    @staticmethod
    def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate the great circle distance between two points on Earth"""
        from math import radians, cos, sin, sqrt, atan2
        
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return R * c

    def parse_dmrc_time(self, time_str: str) -> pd.Timestamp:
        """Parse DMRC time format, handling hours >= 24 correctly."""
        try:
            hours, minutes, seconds = map(int, time_str.split(':'))
            # Create a base timestamp and add the total hours
            base = pd.Timestamp('2024-01-01')  # Use any date as base
            return base + pd.Timedelta(hours=hours, minutes=minutes, seconds=seconds)
        except (ValueError, TypeError):
            logging.error(f"Invalid time format: {time_str}")
            return pd.Timestamp('2024-01-01')

    def preprocess_data(self, trips_df: pd.DataFrame, stops_df: pd.DataFrame) -> List[Trip]:
        """Preprocess the input data into Trip objects."""
        logging.info("Preprocessing input data...")
        
        # Create a stops dictionary for quick lookup
        stops_dict = stops_df.set_index('stop_id')[['stop_lat', 'stop_lon']].to_dict('index')
        
        trips_list = []
        # Add progress bar for preprocessing
        for _, row in tqdm(trips_df.iterrows(), total=len(trips_df), desc="Preprocessing trips"):
            # Calculate trip distance
            if row['start_stop'] in stops_dict and row['end_stop'] in stops_dict:
                start = stops_dict[row['start_stop']]
                end = stops_dict[row['end_stop']]
                distance = self.haversine(
                    start['stop_lat'], start['stop_lon'],
                    end['stop_lat'], end['stop_lon']
                )
            else:
                distance = 0.0
                
            trip = Trip(
                trip_id=row['trip_id'],
                start_stop=row['start_stop'],
                end_stop=row['end_stop'],
                start_time=self.parse_dmrc_time(row['start_time']),
                end_time=self.parse_dmrc_time(row['end_time']),
                route_id=row['route_id'],
                distance=distance
            )
            trips_list.append(trip)
            
        # Sort trips by start time
        trips_list.sort(key=lambda x: x.start_time)
        return trips_list

    def initialize_population(self, trips: List[Trip], max_buses: int) -> List[List[List[Trip]]]:
        """Initialize population with improved initial solutions"""
        logging.info("Initializing population...")
        population = []
        
        # Add progress bar for population initialization
        for _ in tqdm(range(self.population_size), desc="Initializing population"):
            # Initialize buses with empty trip lists
            allocation = [[] for _ in range(max_buses)]
            available_trips = trips.copy()
            
            # Priority queue to track bus availability: (end_time, bus_index, current_location)
            bus_heap = [(pd.Timestamp.min, i, None) for i in range(max_buses)]
            heapq.heapify(bus_heap)
            
            while available_trips:
                trip = available_trips.pop(0)
                allocated = False
                
                # Try to find the best available bus
                while bus_heap and not allocated:
                    end_time, bus_idx, current_loc = heapq.heappop(bus_heap)
                    
                    # Check if bus can handle this trip
                    if end_time + pd.Timedelta(minutes=30) <= trip.start_time:
                        allocation[bus_idx].append(trip)
                        heapq.heappush(bus_heap, (trip.end_time, bus_idx, trip.end_stop))
                        allocated = True
                    else:
                        heapq.heappush(bus_heap, (end_time, bus_idx, current_loc))
                        break
                
                if not allocated:
                    # Find the bus that can take this trip with minimal impact
                    best_bus = min(range(max_buses), 
                                 key=lambda i: self._calculate_insertion_cost(allocation[i], trip))
                    allocation[best_bus].append(trip)
            
            population.append(allocation)
        
        return population

    def _calculate_insertion_cost(self, bus_schedule: List[Trip], trip: Trip) -> float:
        """Calculate the cost of inserting a trip into a bus schedule"""
        if not bus_schedule:
            return 0.0
            
        # Consider time gaps and distance
        last_trip = bus_schedule[-1]
        time_gap = (trip.start_time - last_trip.end_time).total_seconds() / 3600  # hours
        
        if time_gap < 0:  # Overlap penalty
            return float('inf')
        
        return time_gap

    def fitness(self, allocation: List[List[Trip]]) -> float:
        """Calculate the fitness of an allocation with multiple objectives"""
        # Cache check
        allocation_key = tuple(tuple(trip.trip_id for trip in bus) for bus in allocation)
        if allocation_key in self.cache:
            return self.cache[allocation_key]
        
        # Initialize metrics
        buses_used = sum(1 for bus in allocation if bus)
        total_distance = 0
        total_idle_time = 0
        total_trips = 0
        overlaps = 0
        
        for bus_schedule in allocation:
            if not bus_schedule:
                continue
                
            # Sort trips by start time for this bus
            sorted_trips = sorted(bus_schedule, key=lambda x: x.start_time)
            
            # Check for overlaps between consecutive trips
            for i in range(len(sorted_trips) - 1):
                current_trip = sorted_trips[i]
                next_trip = sorted_trips[i + 1]
                
                if current_trip.end_time > next_trip.start_time:
                    overlaps += 1
                else:
                    idle_time = (next_trip.start_time - current_trip.end_time).total_seconds() / 60
                    total_idle_time += idle_time
                
                total_trips += 1
                total_distance += current_trip.distance
            
            # Add the last trip
            if sorted_trips:
                total_trips += 1
                total_distance += sorted_trips[-1].distance
        
        # Calculate normalized metrics
        bus_utilization = buses_used / len(allocation)
        avg_trips_per_bus = total_trips / buses_used if buses_used > 0 else 0
        efficiency_score = total_distance / (total_idle_time + 1)  # Avoid division by zero
        
        # Combined fitness score (lower is better)
        fitness_value = (
            0.4 * bus_utilization +
            0.3 * (1 / (avg_trips_per_bus + 1)) +
            0.2 * (1 / (efficiency_score + 1)) +
            0.1 * (overlaps / (total_trips + 1))
        )
        
        # Cache the result
        self.cache[allocation_key] = fitness_value
        return fitness_value

    def tournament_select(self, population: List[List[List[Trip]]], 
                        fitnesses: List[float]) -> List[List[List[Trip]]]:
        """Selection using tournament selection"""
        selected = []
        
        # Elitism: Keep the best solutions
        elite_indices = sorted(range(len(fitnesses)), key=lambda i: fitnesses[i])[:self.elite_size]
        selected.extend([population[i] for i in elite_indices])
        
        # Tournament selection for the rest
        while len(selected) < self.population_size:
            tournament = random.sample(range(len(population)), self.tournament_size)
            winner = min(tournament, key=lambda i: fitnesses[i])
            selected.append(population[winner])
        
        return selected

    def crossover(self, parent1: List[List[Trip]], 
                 parent2: List[List[Trip]]) -> Tuple[List[List[Trip]], List[List[Trip]]]:
        """Improved crossover operator"""
        max_buses = len(parent1)
        child1 = [[] for _ in range(max_buses)]
        child2 = [[] for _ in range(max_buses)]
        
        # Create sets of trips for each parent
        trips1 = {trip.trip_id for bus in parent1 for trip in bus}
        trips2 = {trip.trip_id for bus in parent2 for trip in bus}
        
        # Crossover point
        crossover_point = random.randint(0, max_buses - 1)
        
        # Copy first part
        for i in range(crossover_point):
            child1[i] = parent1[i].copy()
            child2[i] = parent2[i].copy()
        
        # Fill remaining trips
        remaining1 = trips1 - {trip.trip_id for bus in child1 for trip in bus}
        remaining2 = trips2 - {trip.trip_id for bus in child2 for trip in bus}
        
        # Distribute remaining trips
        for trip_id in remaining1:
            # Find the trip object
            trip = next(trip for bus in parent1 for trip in bus if trip.trip_id == trip_id)
            # Find best bus for this trip
            best_bus = min(range(crossover_point, max_buses),
                          key=lambda i: self._calculate_insertion_cost(child1[i], trip))
            child1[best_bus].append(trip)
            
        for trip_id in remaining2:
            trip = next(trip for bus in parent2 for trip in bus if trip.trip_id == trip_id)
            best_bus = min(range(crossover_point, max_buses),
                          key=lambda i: self._calculate_insertion_cost(child2[i], trip))
            child2[best_bus].append(trip)
        
        return child1, child2

    def mutate(self, allocation: List[List[Trip]]) -> List[List[Trip]]:
        """Improved mutation operator"""
        if random.random() > self.mutation_rate:
            return allocation
            
        mutated = [bus.copy() for bus in allocation]
        
        # Different mutation operations
        mutation_ops = [
            self._swap_trips_mutation,
            self._move_trip_mutation,
            self._shuffle_bus_mutation
        ]
        
        # Apply random mutation operation
        mutation_op = random.choice(mutation_ops)
        mutated = mutation_op(mutated)
        
        return mutated

    def _swap_trips_mutation(self, allocation: List[List[Trip]]) -> List[List[Trip]]:
        """Swap two random trips between buses"""
        non_empty_buses = [i for i, bus in enumerate(allocation) if bus]
        if len(non_empty_buses) < 2:
            return allocation
            
        bus1_idx, bus2_idx = random.sample(non_empty_buses, 2)
        if allocation[bus1_idx] and allocation[bus2_idx]:
            trip1_idx = random.randrange(len(allocation[bus1_idx]))
            trip2_idx = random.randrange(len(allocation[bus2_idx]))
            
            allocation[bus1_idx][trip1_idx], allocation[bus2_idx][trip2_idx] = \
                allocation[bus2_idx][trip2_idx], allocation[bus1_idx][trip1_idx]
        
        return allocation

    def _move_trip_mutation(self, allocation: List[List[Trip]]) -> List[List[Trip]]:
        """Move a random trip to another bus"""
        source_buses = [i for i, bus in enumerate(allocation) if bus]
        if not source_buses:
            return allocation
            
        source_bus = random.choice(source_buses)
        target_bus = random.randrange(len(allocation))
        
        if allocation[source_bus]:
            trip = random.choice(allocation[source_bus])
            allocation[source_bus].remove(trip)
            allocation[target_bus].append(trip)
        
        return allocation

    def _shuffle_bus_mutation(self, allocation: List[List[Trip]]) -> List[List[Trip]]:
        """Shuffle the trips within a random bus"""
        non_empty_buses = [i for i, bus in enumerate(allocation) if bus]
        if not non_empty_buses:
            return allocation
            
        bus_idx = random.choice(non_empty_buses)
        random.shuffle(allocation[bus_idx])
        
        return allocation

    def optimize(self, trips_df: pd.DataFrame, stops_df: pd.DataFrame, 
                max_buses: int, generations: int = 100,
                export_interval: int = 1) -> List[List[Trip]]:
        """Main optimization function"""
        logging.info(f"Starting optimization with {max_buses} buses for {generations} generations")
        
        # Preprocess data
        trips = self.preprocess_data(trips_df, stops_df)
        
        # Initialize population
        population = self.initialize_population(trips, max_buses)
        best_fitness = float('inf')
        best_solution = None
        generations_without_improvement = 0
        
        # Create output directory
        os.makedirs("optimized_schedules", exist_ok=True)
        
        # Main generation progress bar
        pbar = tqdm(range(generations), desc=f"Generations ({max_buses} buses)", position=0)
        
        # Create progress bars for each phase
        fitness_pbar = tqdm(total=self.population_size, desc="Calculating fitness", position=1, leave=False)
        evolution_pbar = tqdm(total=self.population_size, desc="Evolution progress", position=2, leave=False)
        
        for gen in pbar:
            # Reset progress bars
            fitness_pbar.reset()
            evolution_pbar.reset()
            
            # Calculate fitness for all solutions
            fitnesses = []
            for solution in population:
                fitness = self.fitness(solution)
                fitnesses.append(fitness)
                fitness_pbar.update(1)
                fitness_pbar.set_description(f"Fitness calc (current: {fitness:.4f})")
            
            # Track best solution
            current_best = min(fitnesses)
            if current_best < best_fitness:
                best_fitness = current_best
                best_solution = population[fitnesses.index(current_best)]
                generations_without_improvement = 0
            else:
                generations_without_improvement += 1
            
            # Update main progress bar with stats
            avg_fitness = sum(fitnesses) / len(fitnesses)
            pbar.set_description(
                f"Gen {gen+1}/{generations} - Best: {best_fitness:.4f}, Avg: {avg_fitness:.4f}, No improv: {generations_without_improvement}"
            )
            
            # Early stopping if no improvement for many generations
            if generations_without_improvement >= 20:
                logging.info("Early stopping due to no improvement")
                break
            
            # Selection
            selected = self.tournament_select(population, fitnesses)
            evolution_pbar.update(self.elite_size)
            evolution_pbar.set_description(f"Selection complete, creating new population")
            
            # Create new population
            new_population = []
            new_population.extend(selected[:self.elite_size])  # Keep elite solutions
            
            # Crossover and mutation with progress tracking
            while len(new_population) < self.population_size:
                parent1, parent2 = random.sample(selected, 2)
                child1, child2 = self.crossover(parent1, parent2)
                child1 = self.mutate(child1)
                child2 = self.mutate(child2)
                new_population.extend([child1, child2])
                evolution_pbar.update(2)
                evolution_pbar.set_description(
                    f"Evolution ({len(new_population)}/{self.population_size} solutions)"
                )
            
            population = new_population[:self.population_size]
            
            # Export intermediate results
            if (gen + 1) % export_interval == 0:
                self._export_solution(best_solution, max_buses, gen + 1)
        
        # Close progress bars
        fitness_pbar.close()
        evolution_pbar.close()
        pbar.close()
        
        return best_solution

    def _export_solution(self, solution: List[List[Trip]], max_buses: int, generation: int):
        """Export the solution to a CSV file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"optimized_schedules/schedule_buses{max_buses}_gen{generation}_{timestamp}.csv"
        
        data = []
        for bus_idx, bus_schedule in enumerate(solution):
            for trip in bus_schedule:
                data.append({
                    'bus_id': bus_idx + 1,
                    'trip_id': trip.trip_id,
                    'start_time': trip.start_time,
                    'end_time': trip.end_time,
                    'start_stop': trip.start_stop,
                    'end_stop': trip.end_stop,
                    'distance': trip.distance
                })
        
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        logging.info(f"Exported solution to {filename}")

def main():
    # Set up logging
    print("\nStarting bus allocation optimization")
    print("=" * 50)
    
    # Load data
    print("\nLoading data...")
    trips_df = pd.read_csv("formatted_DMRC_trips.csv")
    stops_df = pd.read_csv("DMRC_Data/stops.txt")
    print(f"Loaded {len(trips_df)} trips and {len(stops_df)} stops")
    
    # Initialize optimizer
    optimizer = BusAllocationOptimizer(
        population_size=50,
        mutation_rate=0.1,
        elite_size=5,
        tournament_size=3
    )
    
    # Run optimization for different bus configurations
    # max_buses_list = [600]
    max_buses_list = [600, 800, 1000]
    
    for i, max_buses in enumerate(max_buses_list, 1):
        print(f"\nOptimization Run {i}/{len(max_buses_list)}: {max_buses} buses")
        print("-" * 50)
        
        best_solution = optimizer.optimize(
            trips_df=trips_df,
            stops_df=stops_df,
            max_buses=max_buses,
            generations=15,
            export_interval=1
        )
        
        # Export final solution
        optimizer._export_solution(best_solution, max_buses, -1)  # -1 indicates final solution
        print(f"\nCompleted optimization for {max_buses} buses")
        print("=" * 50)

if __name__ == "__main__":
    main() 