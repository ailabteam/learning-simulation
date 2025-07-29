import h5py
import numpy as np

def extract_satellite_trajectory(constellation_name, shell_name, satellite_id, total_timeslots):
    h5_file_path = f"data/XML_constellation/{constellation_name}.h5"
    trajectory = {'lat': [], 'lon': []}
    
    print(f"Extracting trajectory for satellite {satellite_id}...")
    try:
        with h5py.File(h5_file_path, 'r') as file:
            position_group = file['position'][shell_name]
            for t in range(1, total_timeslots + 1):
                # Data is stored as a list of [lon, lat, alt] strings for all satellites
                # Satellite IDs are 1-indexed, so we access at satellite_id - 1
                dataset = position_group[f'timeslot{t}']
                sat_pos_str = dataset[satellite_id - 1]
                lon, lat, _ = sat_pos_str
                trajectory['lon'].append(float(lon))
                trajectory['lat'].append(float(lat))
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
        
    # Save to a simple numpy file for easy loading later
    output_file = f'satellite_{satellite_id}_trajectory.npz'
    np.savez(output_file, lat=trajectory['lat'], lon=trajectory['lon'])
    print(f"Trajectory saved to {output_file}")
    return trajectory

if __name__ == '__main__':
    # We need to run the pre-computation once to have the H5 file
    # Let's import the necessary modules to do that
    from src.constellation_generation.by_XML.constellation_configuration import constellation_configuration
    import src.XML_constellation.constellation_connectivity.connectivity_mode_plugin_manager as connectivity_mode_plugin_manager

    constellation_name = "Telesat"
    time_step_s = 60
    
    print("Running pre-computation to ensure H5 file is up-to-date...")
    constellation = constellation_configuration(dT=time_step_s, constellation_name=constellation_name, max_duration=True)
    connectionManager = connectivity_mode_plugin_manager.connectivity_mode_plugin_manager()
    connectionManager.execute_connection_policy(constellation, time_step_s)
    print("Pre-computation finished.")

    shell = constellation.shells[0]
    total_timeslots = int(shell.orbit_cycle / time_step_s)
    
    extract_satellite_trajectory(constellation_name, shell.shell_name, satellite_id=1, total_timeslots=total_timeslots)
