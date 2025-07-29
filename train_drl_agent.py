"""
================================================================
DRL Agent Training Script for Satellite Beam Steering
================================================================
This script initializes our custom SatelliteEnv, selects a DRL
algorithm (PPO) from Stable Baselines3, trains the agent for a
specified number of steps, and saves the resulting trained model.
"""
import time
from stable_baselines3 import PPO
from satellite_env import SatelliteEnv

def train_agent():
    print("--- Initializing the Satellite Environment ---")
    env = SatelliteEnv()
    print("Environment initialized.")

    # --- Model Definition ---
    # We will use the Proximal Policy Optimization (PPO) algorithm.
    # It's a robust and widely used DRL algorithm.
    # "MlpPolicy": Use a standard Multi-Layer Perceptron (a type of neural network).
    # verbose=1: Print training progress.
    print("\n--- Defining the DRL (PPO) model ---")
    model = PPO("MlpPolicy", env, verbose=1, tensorboard_log="./ppo_tensorboard/")
    print("Model defined.")

    # --- Training ---
    # total_timesteps: The total number of interactions (steps) the agent will
    # have with the environment. Let's start with 50,000 for a quick test.
    # For a "smarter" agent, this number should be much higher (e.g., 500,000 or 1M).
    training_steps = 50000
    print(f"\n--- Starting training for {training_steps} timesteps ---")
    start_time = time.time()
    
    model.learn(total_timesteps=training_steps)
    
    end_time = time.time()
    print("--- Training finished ---")
    print(f"Total training time: {end_time - start_time:.2f} seconds.")

    # --- Saving the Model ---
    model_file = "drl_beam_steering_agent"
    print(f"\n--- Saving the trained agent to {model_file}.zip ---")
    model.save(model_file)
    print("Agent saved successfully.")

    # Optional: You can view training curves by running this in the terminal:
    # tensorboard --logdir ./ppo_tensorboard/

if __name__ == "__main__":
    train_agent()

