"""
======================================================================
AI-Assisted Resilience Test (Version 3 - Fully Dynamic)
======================================================================
This version dynamically finds the best access satellites at the
specified timeslot to ensure the start/end nodes are always valid.
"""
import time
import networkx as nx
import os
import pandas as pd
import numpy as np # <--- THÊM DÒNG NÀY VÀO

# --- Core Imports ---
from src.constellation_generation.by_XML.constellation_configuration import constellation_configuration
import src.XML_constellation.constellation_entity.user as USER
import src.XML_constellation.constellation_connectivity.connectivity_mode_plugin_manager as connectivity_mode_plugin_manager
import h5py
from math import radians, cos, sin, asin, sqrt

# --- Utility Functions ---
# (build_graph_from_h5, calculate_path_metrics, assess_risk, find_backup_path remain the same)

def build_graph_from_h5(h5_file_path, shell_name, time_slot):
    try:
        with h5py.File(h5_file_path, 'r') as file:
            delay_group = file['delay']
            current_shell_group = delay_group[shell_name]
            delay_matrix = np.array(current_shell_group[f'timeslot{time_slot}']).tolist()
    except (KeyError, FileNotFoundError):
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

def assess_risk(G):
    print("  Assessing satellite risk using Betweenness Centrality...")
    centrality = nx.betweenness_centrality(G, weight='weight', normalized=True)
    return centrality

def find_backup_path(G, main_path, risk_scores):
    if not main_path or len(main_path) <= 2: return None, None
    riskiest_satellite, max_risk = None, -1
    for sat in main_path[1:-1]:
        if risk_scores.get(sat, 0) > max_risk:
            max_risk, riskiest_satellite = risk_scores.get(sat, 0), sat
    if riskiest_satellite is None: return None, main_path[1]
    print(f"  Identified riskiest satellite on main path: {riskiest_satellite} (Risk: {max_risk:.4f})")
    G_temp = G.copy()
    G_temp.remove_node(riskiest_satellite)
    try:
        backup_path = nx.dijkstra_path(G_temp, source=main_path[0], target=main_path[-1], weight='weight')
        print("  Successfully pre-computed a backup path.")
        return backup_path, riskiest_satellite
    except nx.NetworkXNoPath:
        print("  Could not find a backup path after removing the riskiest satellite.")
        return None, riskiest_satellite

def distance_between_satellite_and_user(groundstation, satellite, t):
    longitude1, latitude1 = groundstation.longitude, groundstation.latitude
    longitude2, latitude2 = satellite.longitude[t-1], satellite.latitude[t-1]
    longitude1, latitude1, longitude2, latitude2 = map(radians, [float(longitude1), float(latitude1), float(longitude2), float(latitude2)])
    dlon, dlat = longitude2 - longitude1, latitude2 - latitude1
    a = sin(dlat/2)**2 + cos(latitude1) * cos(latitude2) * sin(dlon/2)**2
    distance = 2 * asin(sqrt(a)) * 6371.0
    return np.round(distance, 3)
    
# --- Main Test Logic ---
def resilience_test():
    # --- 1. Setup ---
    constellation_name = "Telesat"
    time_step_s = 60
    time_slot_to_test = 10
    source_user = USER.user(116.41, 39.9, "Beijing")
    target_user = USER.user(-74.00, 40.43, "NewYork")
    h5_file_path = f"data/XML_constellation/{constellation_name}.h5"

    print("======================================================================")
    print(f"Resilience Test: Proactive vs. Reactive Failure Response")
    print(f"Route: {source_user.user_name} -> {target_user.user_name} at Timeslot {time_slot_to_test}")
    print("======================================================================")

    # --- 2. Pre-computation (Ensure H5 data exists) ---
    print("\nExecuting pre-computation step...")
    constellation = constellation_configuration(dT=time_step_s, constellation_name=constellation_name, max_duration=True)
    connectionManager = connectivity_mode_plugin_manager.connectivity_mode_plugin_manager()
    connectionManager.execute_connection_policy(constellation, time_step_s)
    print("Pre-computation finished.")

    # --- 3. Build the "Healthy" Network Graph ---
    shell = constellation.shells[0]
    G_healthy = build_graph_from_h5(h5_file_path, shell.shell_name, time_slot_to_test)
    if G_healthy is None:
        print("Could not build the healthy graph. Aborting.")
        return

    # --- 4. DYNAMICALLY FIND ACCESS SATELLITES ---
    print("\nFinding best access satellites for the specified timeslot...")
    nearest_sat_to_source, nearest_sat_to_target = None, None
    min_dist_source, min_dist_target = float('inf'), float('inf')
    for orbit in shell.orbits:
        for sat in orbit.satellites:
            dist1 = distance_between_satellite_and_user(source_user, sat, time_slot_to_test)
            if dist1 < min_dist_source:
                min_dist_source, nearest_sat_to_source = dist1, sat
            dist2 = distance_between_satellite_and_user(target_user, sat, time_slot_to_test)
            if dist2 < min_dist_target:
                min_dist_target, nearest_sat_to_target = dist2, sat
    
    if not nearest_sat_to_source or not nearest_sat_to_target:
        print("ERROR: Could not find access satellites.")
        return
        
    start_node = f"satellite_{nearest_sat_to_source.id}"
    end_node = f"satellite_{nearest_sat_to_target.id}"
    print(f"Access nodes found: {start_node} -> {end_node}")
    # --- END OF DYNAMIC FINDING ---

    try:
        print("\n--- [Phase 1: Healthy Network Operation] ---")
        main_path = nx.dijkstra_path(G_healthy, source=start_node, target=end_node, weight='weight')
        main_delay, main_hops = calculate_path_metrics(main_path, G_healthy)
        print(f"  Main path found: Hops={main_hops}, Delay={main_delay:.4f}s")

        print("\n--- [Phase 2: Proactive AI-Assisted Strategy] ---")
        risk_scores = assess_risk(G_healthy)
        backup_path, failed_satellite = find_backup_path(G_healthy, main_path, risk_scores)
        
        if failed_satellite is None:
            print("Could not determine a satellite to fail. Aborting test.")
            return

        print(f"\n--- [Phase 3: Simulating Failure of {failed_satellite}] ---")
        G_failed = G_healthy.copy()
        if G_failed.has_node(failed_satellite): G_failed.remove_node(failed_satellite)

        proactive_delay, proactive_hops = calculate_path_metrics(backup_path, G_failed)
        
        start_reroute_time = time.time()
        reactive_path = nx.dijkstra_path(G_failed, source=start_node, target=end_node, weight='weight')
        end_reroute_time = time.time()
        reactive_delay, reactive_hops = calculate_path_metrics(reactive_path, G_failed)
        reroute_time_ms = (end_reroute_time - start_reroute_time) * 1000

        print("\n======================================================================")
        print("                      Comparison of Failure Responses")
        print("======================================================================")
        print(f"  Healthy Path:      Delay = {main_delay:.4f}s, Hops = {main_hops}")
        print("  ------------------------------------------------------------------")
        print(f"  FAILURE EVENT: Satellite {failed_satellite} fails!")
        print("  ------------------------------------------------------------------")
        print(f"  Proactive (AI) Path: Delay = {proactive_delay:.4f}s, Hops = {proactive_hops}")
        print(f"    - Recovery Time: ~0 ms (path was pre-computed)")
        print(f"  Reactive Path:       Delay = {reactive_delay:.4f}s, Hops = {reactive_hops}")
        print(f"    - Recovery Time: {reroute_time_ms:.2f} ms (time to re-run Dijkstra)")

    except (nx.NetworkXNoPath, TypeError, AttributeError) as e:
        print(f"\nAn error occurred during the test: {e}")

if __name__ == "__main__":
    resilience_test()
