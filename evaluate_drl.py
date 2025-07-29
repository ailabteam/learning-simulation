"""
================================================================
DRL Agent Evaluation Script
================================================================
This script loads a pre-trained DRL agent and evaluates its
performance over a full episode. It also compares the DRL agent's
performance against two baseline strategies: Random and Greedy.
"""
import numpy as np
from stable_baselines3 import PPO
from satellite_env import SatelliteEnv

def evaluate_agent(agent, env):
    """Runs one full episode with a given agent and returns the total reward."""
    obs, info = env.reset()
    total_reward = 0
    done = False
    
    while not done:
        # For DRL agent, we use predict to get the best action.
        # For other policies, this will be handled by a wrapper.
        action, _states = agent.predict(obs, deterministic=True)
        
        obs, reward, done, truncated, info = env.step(action)
        total_reward += reward
    
    return total_reward

def run_random_policy(env):
    """Runs one full episode using a random action policy."""
    env.reset()
    total_reward = 0
    done = False
    
    while not done:
        # Take a completely random action from the action space
        action = env.action_space.sample()
        
        obs, reward, done, truncated, info = env.step(action)
        total_reward += reward
        
    return total_reward

def run_greedy_policy(env):
    """
    Runs one full episode using a greedy policy.
    At each step, it points beams to the cells with the highest demand.
    Note: This is a "cheating" policy as it has perfect knowledge of the demand map.
    """
    env.reset()
    total_reward = 0
    done = False
    
    # Get the demand map and flatten it to find the best cells
    flat_demand_map = env.demand_map.flatten()
    # Get the indices of the top N cells, where N is the number of beams
    best_cell_indices = np.argsort(flat_demand_map)[-env.NUM_BEAMS:]
    
    # The greedy action is always the same: point to the best cells
    greedy_action = best_cell_indices
    
    while not done:
        obs, reward, done, truncated, info = env.step(greedy_action)
        total_reward += reward
        
    return total_reward

def main_evaluation():
    model_file = "drl_beam_steering_agent.zip"
    
    print("--- Initializing the Satellite Environment for Evaluation ---")
    env = SatelliteEnv()
    
    # --- 1. Evaluate the DRL Agent ---
    print(f"\n--- Loading and Evaluating DRL Agent from {model_file} ---")
    try:
        model = PPO.load(model_file)
        drl_total_reward = evaluate_agent(model, env)
        print(f"  DRL Agent Total Reward: {drl_total_reward:.2f}")
    except FileNotFoundError:
        print(f"  ERROR: Model file not found. Skipping DRL agent evaluation.")
        drl_total_reward = 0

    # --- 2. Evaluate the Random Baseline ---
    print("\n--- Evaluating Random Policy Baseline ---")
    random_total_reward = run_random_policy(env)
    print(f"  Random Policy Total Reward: {random_total_reward:.2f}")
    
    # --- 3. Evaluate the Greedy Baseline ---
    print("\n--- Evaluating Greedy Policy Baseline (Near-Optimal) ---")
    greedy_total_reward = run_greedy_policy(env)
    print(f"  Greedy Policy Total Reward: {greedy_total_reward:.2f}")
    
    # --- 4. Final Comparison ---
    print("\n======================================================================")
    print("                      Policy Performance Comparison")
    print("======================================================================")
    print(f"  Random Policy (Baseline):      {random_total_reward:>10.2f}")
    print(f"  Greedy Policy (Near-Optimal):  {greedy_total_reward:>10.2f}")
    print(f"  DRL Agent (Our Trained Model): {drl_total_reward:>10.2f}")
    print("======================================================================")

if __name__ == "__main__":
    main_evaluation()
