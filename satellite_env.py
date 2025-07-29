import gymnasium as gym
from gymnasium import spaces
import numpy as np
import random

class SatelliteEnv(gym.Env):
    """
    A custom environment for a single satellite beam steering problem.
    - State: Satellite's current lat/lon.
    - Action: Choose which grid cells to point beams at.
    - Reward: Total user demand covered by the beams.
    """
    metadata = {'render_modes': ['human']}

    def __init__(self, trajectory_file='satellite_1_trajectory.npz'):
        super(SatelliteEnv, self).__init__()

        # --- 1. Load Satellite Trajectory ---
        self.trajectory = np.load(trajectory_file)
        self.total_timesteps = len(self.trajectory['lat'])
        self.current_timestep = 0

        # --- 2. Define User Demand Map (Simplified) ---
        # Create a 36x18 grid representing the world (each cell is 10x10 degrees)
        # Higher values mean more users.
        self.demand_map = np.zeros((18, 36))
        # Add high-demand zones (e.g., North America, Europe, East Asia)
        self.demand_map[12:15, 2:7] = 10  # North America
        self.demand_map[12:15, 18:24] = 12 # Europe
        self.demand_map[9:12, 28:34] = 15 # East Asia

        # --- 3. Define Constants ---
        self.NUM_BEAMS = 4 # Our satellite has 4 beams
        self.GRID_ROWS = 18
        self.GRID_COLS = 36

        # --- 4. Define Action and Observation Space (Crucial for DRL) ---
        # Action Space: For each of the NUM_BEAMS, choose one of the GRID_COLS*GRID_ROWS cells.
        # This is a MultiDiscrete space, like 4 slot machines, each with 648 slots.
        self.action_space = spaces.MultiDiscrete([self.GRID_ROWS * self.GRID_COLS] * self.NUM_BEAMS)

        # Observation Space: What the agent sees.
        # [sat_lat, sat_lon]
        # Latitude is from -90 to 90, Longitude is from -180 to 180.
        low = np.array([-90.0, -180.0])
        high = np.array([90.0, 180.0])
        self.observation_space = spaces.Box(low=low, high=high, dtype=np.float32)

    def _get_obs(self):
        """Returns the current observation (state) of the environment."""
        lat = self.trajectory['lat'][self.current_timestep]
        lon = self.trajectory['lon'][self.current_timestep]
        return np.array([lat, lon], dtype=np.float32)

    def _get_info(self):
        """Returns auxiliary information (optional)."""
        return {'timestep': self.current_timestep}

    def reset(self, seed=None, options=None):
        """Resets the environment to the beginning."""
        super().reset(seed=seed)
        self.current_timestep = 0
        return self._get_obs(), self._get_info()

    def step(self, action):
        """
        Executes one time step in the environment.
        1. Takes an action.
        2. Calculates the reward.
        3. Moves to the next state.
        4. Checks if the episode is done.
        """
        # --- Calculate Reward ---
        # The action is an array of indices, e.g., [10, 150, 34, 8]
        total_reward = 0
        covered_cells = set()
        for cell_index in action:
            # Prevent beams from pointing to the same cell to get double reward
            if cell_index not in covered_cells:
                # Convert 1D index to 2D grid coordinate
                row = cell_index // self.GRID_COLS
                col = cell_index % self.GRID_COLS
                total_reward += self.demand_map[row, col]
                covered_cells.add(cell_index)

        # --- Move to the next state ---
        self.current_timestep += 1

        # --- Check if the episode is done ---
        # The episode ends when the satellite has completed its trajectory
        done = self.current_timestep >= (self.total_timesteps - 1)
        
        # Get the next observation and info
        observation = self._get_obs()
        info = self._get_info()

        # The 'truncated' flag is used for time limits, similar to 'done'
        truncated = done

        return observation, total_reward, done, truncated, info

    def render(self):
        """A simple text-based rendering."""
        lat = self.trajectory['lat'][self.current_timestep]
        lon = self.trajectory['lon'][self.current_timestep]
        print(f"Timestep {self.current_timestep}: Sat at ({lat:.2f}, {lon:.2f})")

    def close(self):
        pass
