"""
My Comparison Test: Shortest Path vs. Least Hop
"""

# Import all necessary modules
import src.constellation_generation.by_XML.constellation_configuration as constellation_configuration
import src.XML_constellation.constellation_connectivity.connectivity_mode_plugin_manager as connectivity_mode_plugin_manager
import src.XML_constellation.constellation_routing.routing_policy_plugin_manager as routing_policy_plugin_manager
import src.XML_constellation.constellation_entity.user as USER
# We might need this later to calculate delay of a given path
import src.XML_constellation.constellation_evaluation.exists_ISL.delay as DELAY_CALCULATOR

def comparison_test():
    print("--- Starting Comparison: Shortest Path vs. Least Hop ---")
    
    # --- 1. Setup the Scenario ---
    dT = 5730
    constellation_name = "Telesat"  # Let's use Telesat as in the original tests
    source = USER.user(105.84, 21.02, "Hanoi")
    target = USER.user(2.35, 48.85, "Paris")
    
    print(f"\nCalculating routes from {source.user_name} to {target.user_name}...")
    
    # --- 2. Initialize Constellation and Connectivity ---
    # This part is the same for both tests, so we only do it once.
    constellation = constellation_configuration.constellation_configuration(dT, constellation_name=constellation_name)
    connectionModePluginManager = connectivity_mode_plugin_manager.connectivity_mode_plugin_manager()
    connectionModePluginManager.execute_connection_policy(constellation=constellation, dT=dT)
    
    # Initialize the routing manager
    routingPolicyPluginManager = routing_policy_plugin_manager.routing_policy_plugin_manager()
    
    # --- 3. Run Test 1: Shortest Path (Default Policy) ---
    print("\n--- Running Algorithm 1: Shortest Path (Lowest Latency) ---")
    # The default policy is "shortest_path"
    path1 = routingPolicyPluginManager.execute_routing_policy(constellation.constellation_name, source, target, constellation.shells[0])
    hops1 = len(path1) - 1
    # TODO: We need a function to calculate the delay of path1
    # delay1 = calculate_path_delay(path1, ...) 
    
    print(f"\tPath: {path1}")
    print(f"\tHop Count: {hops1}")
    # print(f"\tDelay: {delay1} s")

    # --- 4. Run Test 2: Least Hop Path ---
    print("\n--- Running Algorithm 2: Least Hop Path ---")
    routingPolicyPluginManager.set_routing_policy("least_hop_path") # Switch the policy
    path2 = routingPolicyPluginManager.execute_routing_policy(constellation.constellation_name, source, target, constellation.shells[0])
    hops2 = len(path2) - 1
    # TODO: We need a function to calculate the delay of path2
    # delay2 = calculate_path_delay(path2, ...)

    print(f"\tPath: {path2}")
    print(f"\tHop Count: {hops2}")
    # print(f"\tDelay: {delay2} s")

    print("\n--- Comparison Finished ---")


if __name__ == "__main__":
    comparison_test()

