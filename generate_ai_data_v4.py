"""
======================================================================
AI Data Generation Script (Version 4) - Final & Correct Workflow
======================================================================
This script follows the simulator's intended workflow:
1. Run a full pre-computation to generate a complete H5 file with
   position and delay data for an entire orbit cycle.
2. Loop through the timeslots, read data from the H5 file, build
   the graph, and extract features.
"""
import time
import csv
import os
import h5py
import networkx as nx
import numpy as np

# --- Core Imports ---
from src.constellation_generation.by_XML.constellation_configuration import constellation_configuration
import src.XML_constellation.constellation_connectivity.connectivity_mode_plugin_manager as connectivity_mode_plugin_manager

# --- Utility function to build graph from H5 data ---
def build_graph_from_h5(h5_file_path, shell_name, time_slot):
    """
    Builds and returns a NetworkX graph 'G' for a specific shell and time slot
    by READING pre-computed data from an H5 file.
    """
    try:
        with h5py.File(h5_file_path, 'r') as file:
            delay_group = file['delay']
            current_shell_group = delay_group[shell_name]
            delay_matrix = np.array(current_shell_group[f'timeslot{time_slot}']).tolist()
    except (KeyError, FileNotFoundError):
        print(f"Warning: Could not read delay data for shell '{shell_name}', timeslot {time_slot}.")
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
    time_step_s = 60

    h5_file_path = f"data/XML_constellation/{constellation_name}.h5"

    # --- 2. PRE-COMPUTATION: The most important step ---
    # Delete old file to force a full re-computation
    if os.path.exists(h5_file_path):
        os.remove(h5_file_path)
        print(f"Removed existing H5 file: {h5_file_path}")
        
    print("\nStarting full pre-computation. THIS WILL BE VERY SLOW...")
    start_precomp_time = time.time()
    
    # Initialize constellation with max_duration=True
    constellation = constellation_configuration(dT=time_step_s, constellation_name=constellation_name, max_duration=True)
    # This manager will call the positive_Grid plugin and do all the heavy lifting
    connectionManager = connectivity_mode_plugin_manager.connectivity_mode_plugin_manager()
    connectionManager.execute_connection_policy(constellation, time_step_s)
    
    end_precomp_time = time.time()
    print(f"Pre-computation finished in {end_precomp_time - start_precomp_time:.2f} seconds.")

    # --- 3. Prepare for Data Collection ---
    shell = constellation.shells[0]
    total_duration = shell.orbit_cycle
    total_timeslots = int(total_duration / time_step_s)
    
    output_csv_file = 'isl_link_data.csv'
    csv_header = ['time_slot', 'source_sat_id', 'target_sat_id', 'is_inter_plane', 'actual_delay']
    
    sat_to_orbit_map = {}
    for orbit in shell.orbits:
        for sat in orbit.satellites:
            sat_to_orbit_map[f"satellite_{sat.id}"] = orbit.orbit_id

    # --- 4. Data Extraction Loop ---
    start_extract_time = time.time()
    print(f"\nStarting data extraction for {total_timeslots} timeslots...")

    with open(output_csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(csv_header)

        for t in range(1, total_timeslots + 1):
            # Now we just read the H5 file at each step
            G = build_graph_from_h5(h5_file_path, shell.shell_name, t)
            
            if G is None: continue

            for u, v, data in G.edges(data=True):
                u_orbit = sat_to_orbit_map.get(u)
                v_orbit = sat_to_orbit_map.get(v)
                is_inter_plane = 1 if u_orbit != v_orbit else 0
                actual_delay = data['weight']
                writer.writerow([t, u, v, is_inter_plane, actual_delay])
            
            if t % 10 == 0:
                print(f"  Extracted data from timeslot {t}/{total_timeslots}...")

    end_extract_time = time.time()
    print("\n----------------------------------------------------")
    print(f"Data generation complete!")
    print(f"Data saved to: {output_csv_file}")
    print(f"Total extraction time: {end_extract_time - start_extract_time:.2f} seconds.")
    print("----------------------------------------------------")

if __name__ == "__main__":
    generate_data()
