from stable_baselines3.common.env_checker import check_env
from satellite_env import SatelliteEnv

# Create an instance of our custom environment
env = SatelliteEnv()

# Check the environment
# It will print warnings or errors if something is wrong.
# If it prints nothing, the environment is good to go!
check_env(env)

print("Environment check passed!")
