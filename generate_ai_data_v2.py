"""
================================================================
AI Data Generation Script (Version 2.1) - Correct Import Path
================================================================
This script takes full control of the simulation loop to ensure
data for the entire orbit cycle is generated correctly. This version
uses the correct import path for the positive_Grid plugin.
"""
import time
import csv
import os
import h5py
import networkx as nx
import numpy as np

# --- Core Imports ---
from src.constellation_generation.by_XML.constellation_configuration import constellation_configuration
# --- THIS IS THE CORRECTED IMPORT LINE ---
from src.XML_constellation.constellation_connectivity.connectivity_plugin.positive_Grid import positive_Grid

# --- Main Data Generation Logic ---

def generate_data_v2():
    # --- 1. Scenario Setup ---
    constellation_name = "Telesat"
    time_step_s = 60 # seconds

    # --- 2. Build the Constellation Object ---
    print("Initializing constellation structure...")
    # This step is still fast, it just sets up the object parameters.
    constellation = constellation_configuration(dT=time_step_s, constellation_name=constellation_name, max_duration=True)
    shell = constellation.shells[0]
    total_duration = shell.orbit_cycle
    total_timeslots = int(total_duration / time_step_s)
    print(f"Initialization complete. Ready to simulate for {total_timeslots} timeslots.")

    # --- 3. Prepare for Data Collection ---
    output_csv_file = 'isl_link_data_v2.csv'
    csv_header = ['time_slot', 'source_sat_id', 'target_sat_id', 'is_inter_plane', 'actual_delay']
    
    sat_to_orbit_map = {}
    for orbit in shell.orbits:
        for sat in orbit.satellites:
            sat_to_orbit_map[f"satellite_{sat.id}"] = orbit.orbit_id

    # --- 4. Main Simulation and Data Collection Loop ---
    start_time = time.time()
    print(f"\nStarting data generation loop... THIS WILL BE SLOW.")

    with open(output_csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(csv_header)

        for t in range(1, total_timeslots + 1):
            # --- For each timeslot, we explicitly calculate connectivity and delay ---
            # This is the function that does the heavy lifting for each time step.
            G = positive_Grid(constellation_name, shell, t)
            
            if G is None or G.number_of_edges() == 0:
                print(f"  Warning: No graph or no edges found for timeslot {t}. Skipping.")
                continue

            for u, v, data in G.edges(data=True):
                u_orbit = sat_to_orbit_map.get(u)
                v_orbit = sat_to_orbit_map.get(v)
                is_inter_plane = 1 if u_orbit != v_orbit else 0
                actual_delay = data.get('weight', -1)

                if actual_delay != -1:
                    writer.writerow([t, u, v, is_inter_plane, actual_delay])
            
            if t % 5 == 0:
                print(f"  Processed timeslot {t}/{total_timeslots}...")

    end_time = time.time()
    print("\n----------------------------------------------------")
    print(f"Data generation complete!")
    print(f"Data saved to: {output_csv_file}")
    print(f"Total time taken: {end_time - start_time:.2f} seconds.")
    print("----------------------------------------------------")

if __name__ == "__main__":
    generate_data_v2()
