"""
================================================================
Data Generation Script for Predictive Routing AI Model
================================================================
This script simulates a satellite constellation over a long period,
builds the network graph at each time step, and extracts link
features to create a training dataset.

Output: isl_link_data.csv
"""
import time
import csv
import os

# --- Core Imports ---
import src.constellation_generation.by_XML.constellation_configuration as constellation_configuration
import h5py
import numpy as np
from math import radians, cos, sin, asin, sqrt

# --- Utility Function to Build Graph (from our previous work) ---
def build_graph_at_time_t(constellation_name, shell, time_slot):
    file_path = f"data/XML_constellation/{constellation_name}.h5"
    try:
        with h5py.File(file_path, 'r') as file:
            delay_group = file['delay']
            current_shell_group = delay_group[shell.shell_name]
            delay_matrix = np.array(current_shell_group[f'timeslot{time_slot}']).tolist()
    except KeyError:
        print(f"ERROR: 'delay' data not found for timeslot {time_slot}. The pre-computation might not have run for this long.")
        return None

    G = nx.Graph()
    num_sats_plus_one = len(delay_matrix)
    for i in range(1, num_sats_plus_one):
        for j in range(i + 1, num_sats_plus_one):
            if delay_matrix[i][j] > 0:
                G.add_edge(f"satellite_{i}", f"satellite_{j}", weight=delay_matrix[i][j])
    return G

# --- Main Data Generation Logic ---

def generate_data():
    # --- 1. Scenario Setup ---
    constellation_name = "Telesat"
    # To get a lot of data, we need a long simulation time.
    # Let's use the full orbit cycle.
    # A smaller time step gives more data points.
    time_step_s = 60 # seconds
    
    # --- 2. Initialize Constellation (to get parameters) ---
    # This pre-computation step is crucial. It generates the position and delay data we need.
    print("Executing pre-computation step to generate all necessary data...")
    # We use orbit_cycle as the total simulation time (dT).
    # This might take a very long time, but it's necessary.
    constellation = constellation_configuration.constellation_configuration(dT=time_step_s, constellation_name=constellation_name, max_duration=True)
    import src.XML_constellation.constellation_connectivity.connectivity_mode_plugin_manager as connectivity_mode_plugin_manager
    connectionModePluginManager = connectivity_mode_plugin_manager.connectivity_mode_plugin_manager()
    connectionModePluginManager.execute_connection_policy(constellation=constellation, dT=time_step_s)
    print("Pre-computation finished.")

    # Let's work with the first shell
    shell = constellation.shells[0]
    total_duration = shell.orbit_cycle
    total_timeslots = int(total_duration / time_step_s)

    # --- 3. Prepare for Data Collection ---
    output_csv_file = 'isl_link_data.csv'
    csv_header = [
        'time_slot', 
        'source_sat_id', 'target_sat_id',
        'is_inter_plane', # Feature: Is this a link between different orbital planes?
        'actual_delay' # Label: The real delay of the link
    ]

    # Create a lookup map for satellite -> orbit_id for quick access
    sat_to_orbit_map = {}
    for orbit in shell.orbits:
        for sat in orbit.satellites:
            sat_to_orbit_map[f"satellite_{sat.id}"] = orbit.orbit_id

    # --- 4. Main Simulation Loop ---
    start_time = time.time()
    print(f"\nStarting data generation for {total_timeslots} timeslots. This will take a while...")

    with open(output_csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(csv_header)

        for t in range(1, total_timeslots + 1):
            # Build the graph for the current time slot
            G = build_graph_at_time_t(constellation_name, shell, t)
            
            if G is None:
                # Stop if data for this timeslot doesn't exist
                break

            # Iterate over every link (edge) in the graph
            for u, v, data in G.edges(data=True):
                # Extract the satellite IDs from the node names
                u_id = u
                v_id = v
                
                # --- Feature Engineering ---
                # 1. is_inter_plane
                # A crucial feature. Links between planes are generally less stable.
                is_inter_plane = 1 if sat_to_orbit_map.get(u_id) != sat_to_orbit_map.get(v_id) else 0

                # --- Label ---
                actual_delay = data['weight']

                # Write the row to the CSV file
                writer.writerow([t, u_id, v_id, is_inter_plane, actual_delay])
            
            if t % 10 == 0:
                print(f"  Processed timeslot {t}/{total_timeslots}...")

    end_time = time.time()
    print("\n----------------------------------------------------")
    print(f"Data generation complete!")
    print(f"Data saved to: {output_csv_file}")
    print(f"Total time taken: {end_time - start_time:.2f} seconds.")
    print("----------------------------------------------------")

if __name__ == "__main__":
    # We need to import networkx for the build_graph function
    import networkx as nx
    generate_data()

