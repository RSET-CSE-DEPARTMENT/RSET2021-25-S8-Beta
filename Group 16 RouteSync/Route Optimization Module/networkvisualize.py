import pandas as pd
import networkx as nx
from datetime import datetime, timedelta
import matplotlib.pyplot as plt


file_path = 'stop_times.csv'
stop_times_df = pd.read_csv(file_path)


bus_graph = nx.DiGraph()


def parse_time(time_str):
    try:
        if "day" in time_str:
            
            days, time_part = time_str.split(", ")
            day_offset = int(days.split()[0])
            time_obj = datetime.strptime(time_part, '%H:%M:%S') + timedelta(days=day_offset)
        else:
            time_obj = datetime.strptime(time_str, '%H:%M:%S')
        return time_obj
    except Exception as e:
        print(f"")
        return None


prev_stop = None
prev_departure = None
prev_trip_id = None

for index, row in stop_times_df.iterrows():
    current_stop = row['stop_id']
    current_arrival = str(row['arrival_time']).strip()
    current_departure = str(row['departure_time']).strip()
    current_trip_id = row['trip_id']

    
    current_arrival_time = parse_time(current_arrival)
    current_departure_time = parse_time(current_departure)

    if current_arrival_time is None or current_departure_time is None:
        continue

    
    if prev_trip_id == current_trip_id and prev_stop is not None:
        travel_time = (current_arrival_time - prev_departure).total_seconds()

        if travel_time >= 0:  
            bus_graph.add_edge(prev_stop, current_stop, weight=travel_time)

    
    prev_stop = current_stop
    prev_departure = current_departure_time
    prev_trip_id = current_trip_id


print(f"Number of bus stops (nodes): {len(bus_graph.nodes())}")
print(f"Number of bus routes (edges): {len(bus_graph.edges())}")

plt.figure(figsize=(12, 8))
pos = nx.spring_layout(bus_graph)  

nx.draw_networkx_nodes(bus_graph, pos, node_size=700, node_color='lightblue', edgecolors='black')
nx.draw_networkx_edges(bus_graph, pos, edge_color='gray')

nx.draw_networkx_labels(bus_graph, pos, font_size=10, font_color='black')

edge_labels = {(u, v): f"{d['weight'] / 60:.2f} min" for u, v, d in bus_graph.edges(data=True)}
nx.draw_networkx_edge_labels(bus_graph, pos, edge_labels=edge_labels, font_color='red', font_size=8)

# Title plot
plt.title("Bus Network Visualization (Travel Time Between Stops)")
plt.xlabel("Bus Stops (Nodes)")
plt.ylabel("Travel Time Between Stops (Edges)")
plt.show()
