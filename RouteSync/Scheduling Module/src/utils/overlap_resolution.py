def allocate_overlapping_trips(allocation, trip_dict, buffer_time=10 * 60):
    """
    Allocate overlapping trips to buses with no allocated trips.

    :param allocation: List of buses and their allocated trips (list of lists).
    :param trip_dict: Dictionary with trip details (start and end times).
    :param buffer_time: Buffer time in seconds between trips.
    :return: Updated allocation.
    """
    # Identify buses with no allocated trips
    empty_buses = [i for i, trips in enumerate(allocation) if not trips]

    # Find all overlapping trips
    overlapping_trips = []
    for bus, trips in enumerate(allocation):
        for i in range(len(trips) - 1):
            trip1 = trips[i]
            trip2 = trips[i + 1]

            # Check if the trips overlap
            if trip_dict[trip1]["end_time_y"] + buffer_time > trip_dict[trip2]["start_time_y"]:
                overlapping_trips.append((bus, trip2))

    # Allocate overlapping trips to empty buses
    for bus, trip in overlapping_trips:
        if empty_buses:
            new_bus = empty_buses.pop(0)  # Assign an empty bus
            allocation[new_bus].append(trip)  # Allocate the trip to the empty bus
            allocation[bus].remove(trip)  # Remove the trip from the original bus

    return allocation

# Example Usage
if __name__ == "__main__":
    # Sample trip_dict
    trip_dict = {
        1: {"start_time_y": 0, "end_time_y": 3600},
        2: {"start_time_y": 3500, "end_time_y": 7200},
        3: {"start_time_y": 7100, "end_time_y": 10800},
        4: {"start_time_y": 10700, "end_time_y": 14400},
    }

    # Sample allocation (bus -> trips)
    allocation = [
        [1, 2],  # Bus 0 has trips 1 and 2 (overlap between 2 and 3)
        [3, 4],  # Bus 1 has trips 3 and 4
        [],      # Bus 2 is empty
    ]

    # Allocate overlapping trips to empty buses
    updated_allocation = allocate_overlapping_trips(allocation, trip_dict)

    print("Updated Allocation:", updated_allocation)
