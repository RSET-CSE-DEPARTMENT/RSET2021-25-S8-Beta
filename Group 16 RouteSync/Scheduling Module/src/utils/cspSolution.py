import pandas as pd
import logging
from ortools.sat.python import cp_model

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Load input data
def load_data():
    logging.info("Loading input data...")
    trips = pd.read_csv("DMRC_Data/trips.txt")
    stop_times = pd.read_csv("DMRC_Data/stop_times.txt")
    logging.info("Data loaded successfully.")
    return trips, stop_times

# Fix time format
def fix_time_format(time_str):
    try:
        hours, minutes, seconds = map(int, time_str.split(":"))
        if hours >= 24:
            hours -= 24
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    except ValueError:
        logging.warning(f"Invalid time format: {time_str}")
        return time_str

# Convert time to minutes for easier comparison
def time_to_minutes(time_str):
    hours, minutes, seconds = map(int, time_str.split(":"))
    return hours * 60 + minutes + seconds / 60

# Create the CSP model
def allocate_buses(trips, stop_times, max_buses):
    logging.info("Initializing CSP model...")
    model = cp_model.CpModel()

    # Extract unique trip IDs
    trip_ids = trips['trip_id'].tolist()

    # Create variables for each trip and bus allocation
    logging.info("Creating variables for each trip and bus allocation...")    
    bus_assignments = {}
    for trip_id in trip_ids:
        bus_assignments[trip_id] = model.NewIntVar(0, max_buses - 1, f"bus_{trip_id}")

    # Add constraints to prevent overlapping trips on the same bus
    logging.info("Adding constraints to prevent overlapping trips on the same bus...")
    
    # Precompute start and end times
    trip_times = [
        (trip_id, time_to_minutes(stop_times[stop_times['trip_id'] == trip_id]['arrival_time'].iloc[0]),
        time_to_minutes(stop_times[stop_times['trip_id'] == trip_id]['departure_time'].iloc[-1]))
        for trip_id in trip_ids
    ]

    # Sort trips by start time
    trip_times.sort(key=lambda x: x[1])  # Sort by start time (second element)

    # Create interval variables for each trip
    interval_vars = {}
    for trip_id, start_time, end_time in trip_times:
        # Convert start_time and end_time to integers
        start_time = int(start_time)  # Ensure start time is an integer
        end_time = int(end_time)      # Ensure end time is an integer
        interval_vars[trip_id] = model.NewIntervalVar(
            start_time, end_time - start_time, end_time, f"interval_{trip_id}"
        )

    # Add non-overlapping constraints for trips
    for i in range(len(trip_times)):
        for j in range(i + 1, len(trip_times)):
            trip1, start1, end1 = trip_times[i]
            trip2, start2, end2 = trip_times[j]

            # Break early if trips don't overlap in time
            if start2 >= end1:
                break

            no_overlap = model.NewBoolVar(f"no_overlap_{trip1}_{trip2}")
            model.AddNoOverlap([interval_vars[trip1], interval_vars[trip2]]).OnlyEnforceIf(no_overlap)


    # Minimize the number of buses used
    logging.info("Minimizing the number of buses used...")

    bus_usage = [
        model.NewBoolVar(f"bus_used_{bus}") for bus in range(max_buses)
    ]

    # For each bus, we ensure that at least one trip is assigned to it.
    for bus in range(max_buses):
        # Create a list of linear expressions for each bus assignment comparison
        bus_assignments_for_bus = [model.NewBoolVar(f"bus_{trip_id}_assigned_to_{bus}") for trip_id in trip_ids]
        
        # Each trip assigned to this bus results in a boolean variable being True
        for idx, trip_id in enumerate(trip_ids):
            model.Add(bus_assignments[trip_id] == bus).OnlyEnforceIf(bus_assignments_for_bus[idx])

        # Add a constraint to ensure at least one trip is assigned to the bus
        model.Add(sum(bus_assignments_for_bus) >= 1).OnlyEnforceIf(bus_usage[bus])

    # Minimize the number of buses used
    model.Minimize(sum(bus_usage))



    # Solve the model
    solver = cp_model.CpSolver()
    logging.info("Solving the CSP model...")
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        logging.info("Solution found!")
        allocation = []
        for trip_id in trip_ids:
            allocation.append({
                'Trip ID': trip_id,
                'Bus Number': solver.Value(bus_assignments[trip_id]) + 1
            })
        return pd.DataFrame(allocation)
    else:
        logging.error("No solution found.")
        return None

if __name__ == "__main__":
    logging.info("Loading data...")
    trips, stop_times = load_data()

    logging.info("Fixing time formats...")
    stop_times['arrival_time'] = stop_times['arrival_time'].apply(fix_time_format)
    stop_times['departure_time'] = stop_times['departure_time'].apply(fix_time_format)

    max_buses = 5000  # Define the maximum number of buses available
    
    trips['trip_id'] = pd.to_numeric(trips['trip_id'], errors='coerce')

    logging.info("Allocating buses to trips...")
    allocation = allocate_buses(trips, stop_times, max_buses)

    if allocation is not None:
        logging.info("Saving allocation to CSV...")
        allocation.to_csv("bus_allocation.csv", index=False)
        logging.info("Allocation saved successfully.")
