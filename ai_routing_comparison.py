"""
======================================================================
AI-Powered Routing vs. Classic Routing (Version 3 - Dynamic Access)
======================================================================
This version dynamically finds the best access satellites at each
timeslot instead of using hardcoded start/end nodes. This ensures
that the routing problem is always valid.
"""
import time
import pandas as pd
import numpy as np
import networkx as nx
import joblib
import os

# --- Core Imports ---
from src.constellation_generation.by_XML.constellation_configuration import constellation_configuration
import src.XML_constellation.constellation_entity.user as USER
import src.XML_constellation.constellation_connectivity.connectivity_mode_plugin_manager as connectivity_mode_plugin_manager
import h5py
from math import radians, cos, sin, asin, sqrt

# --- Utility Functions (Unchanged) ---
def distance_between_satellite_and_user(groundstation, satellite, t):
    longitude1, latitude1 = groundstation.longitude, groundstation.latitude
    longitude2, latitude2 = satellite.longitude[t-1], satellite.latitude[t-1]
    longitude1, latitude1, longitude2, latitude2 = map(radians, [float(longitude1), float(latitude1), float(longitude2), float(latitude2)])
    dlon, dlat = longitude2 - longitude1, latitude2 - latitude1
    a = sin(dlat/2)**2 + cos(latitude1) * cos(latitude2) * sin(dlon/2)**2
    distance = 2 * asin(sqrt(a)) * 6371.0
    return np.round(distance, 3)

def build_graph_from_h5(h5_file_path, shell_name, time_slot):
    try:
        with h5py.File(h5_file_path, 'r') as file:
            delay_group = file['delay']
            current_shell_group = delay_group[shell_name]
            delay_matrix = np.array(current_shell_group[f'timeslot{time_slot}']).tolist()
    except (KeyError, FileNotFoundError):
        print(f"  Warning: Could not read delay data for shell '{shell_name}', timeslot {time_slot}.")
        return None
    
    G = nx.Graph()
    num_sats_plus_one = len(delay_matrix)
    for i in range(1, num_sats_plus_one):
        for j in range(i + 1, num_sats_plus_one):
            if delay_matrix[i][j] > 0:
                G.add_edge(f"satellite_{i}", f"satellite_{j}", weight=delay_matrix[i][j])
    return G

def calculate_path_metrics(path, G_real):
    if not path: return float('inf'), float('inf')
    hops = len(path) - 1
    delay = nx.path_weight(G_real, path, weight='weight')
    return delay, hops

# --- Main Comparison Logic ---
def ai_comparison():
    # --- 1. Scenario Setup ---
    constellation_name = "Telesat"
    time_step_s = 60
    source_user = USER.user(105.84, 21.02, "Hanoi")
    target_user = USER.user(-43.17, -22.91, "Rio_de_Janeiro")
    h5_file_path = f"data/XML_constellation/{constellation_name}.h5"
    model_file = 'delay_predictor.joblib'
    
    print("======================================================================")
    print("AI Routing vs. Classic Routing (Dynamic Access)")
    print("======================================================================")

    # --- 2. Pre-computation ---
    if os.path.exists(h5_file_path): os.remove(h5_file_path)
    print("\nStarting full pre-computation...")
    start_precomp_time = time.time()
    constellation = constellation_configuration(dT=time_step_s, constellation_name=constellation_name, max_duration=True)
    connectionManager = connectivity_mode_plugin_manager.connectivity_mode_plugin_manager()
    connectionManager.execute_connection_policy(constellation, time_step_s)
    end_precomp_time = time.time()
    print(f"Pre-computation finished in {end_precomp_time - start_precomp_time:.2f} seconds.")

    # --- 3. Load AI Model and Prepare for Sim ---
    print(f"\nLoading AI model from {model_file}...")
    model = joblib.load(model_file)
    print("AI model loaded successfully.")

    shell = constellation.shells[0]
    sat_to_orbit_map = {f"satellite_{sat.id}": orbit.orbit_id for orbit in shell.orbits for sat in orbit.satellites}
    
    # --- 4. Simulation and Comparison Loop ---
    simulation_range = range(1, 51) # Let's try a longer range
    results = []

    print(f"\nStarting simulation for {len(simulation_range)} time steps...")
    for t in simulation_range:
        # --- DYNAMIC ACCESS SATELLITE FINDING (INSIDE THE LOOP) ---
        nearest_sat_to_source, nearest_sat_to_target = None, None
        min_dist_source, min_dist_target = float('inf'), float('inf')
        for orbit in shell.orbits:
            for sat in orbit.satellites:
                dist1 = distance_between_satellite_and_user(source_user, sat, t)
                if dist1 < min_dist_source:
                    min_dist_source = dist1
                    nearest_sat_to_source = sat
                
                dist2 = distance_between_satellite_and_user(target_user, sat, t)
                if dist2 < min_dist_target:
                    min_dist_target = dist2
                    nearest_sat_to_target = sat
        
        if not nearest_sat_to_source or not nearest_sat_to_target:
            print(f"  Skipping timeslot {t}: Could not find access satellites.")
            continue
        start_node = f"satellite_{nearest_sat_to_source.id}"
        end_node = f"satellite_{nearest_sat_to_target.id}"
        # --- END OF DYNAMIC ACCESS LOGIC ---

        G_real = build_graph_from_h5(h5_file_path, shell.shell_name, t)
        if G_real is None: continue
            
        G_predicted = G_real.copy()
        for u, v in G_predicted.edges():
            is_inter_plane = 1 if sat_to_orbit_map.get(u) != sat_to_orbit_map.get(v) else 0
            features = pd.DataFrame([[t, is_inter_plane]], columns=['time_slot', 'is_inter_plane'])
            predicted_delay = model.predict(features)[0]
            G_predicted[u][v]['weight'] = predicted_delay

        try:
            path_classic = nx.dijkstra_path(G_real, source=start_node, target=end_node, weight='weight')
            path_ai = nx.dijkstra_path(G_predicted, source=start_node, target=end_node, weight='weight')
            
            classic_delay, classic_hops = calculate_path_metrics(path_classic, G_real)
            ai_delay, ai_hops = calculate_path_metrics(path_ai, G_real)

            results.append({'timeslot': t, 'classic_delay': classic_delay, 'ai_delay': ai_delay})
            print(f"  Processed timeslot {t}: Classic Delay={classic_delay:.4f}s, AI Delay={ai_delay:.4f}s")

        except nx.NetworkXNoPath:
            print(f"  Skipping timeslot {t}: No path found between {start_node} and {end_node}.")
            continue

    # --- 5. Analyze and Print Final Results ---
    print("\n======================================================================")
    print("                      Simulation Results Analysis")
    print("======================================================================")

    if not results:
        print("No valid results were generated to analyze.")
        return

    df_results = pd.DataFrame(results)
    jitter_classic = df_results['classic_delay'].std()
    jitter_ai = df_results['ai_delay'].std()

    print("\n--- Stability & Jitter (Lower is Better) ---")
    print(f"  Classic Route Jitter (Std Dev of Delay): {jitter_classic:.6f}")
    print(f"  AI-Powered Route Jitter (Std Dev of Delay): {jitter_ai:.6f}")

    if jitter_classic > 0 and jitter_ai < jitter_classic:
        improvement = ((jitter_classic - jitter_ai) / jitter_classic) * 100
        print(f"\nCONCLUSION: The AI-Powered routing strategy reduced delay jitter by {improvement:.2f}%!")
    else:
        print("\nCONCLUSION: The AI-Powered routing did not improve jitter in this scenario.")

if __name__ == "__main__":
    ai_comparison()
