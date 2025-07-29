import h5py

# Define the path to the H5 file we want to inspect
file_path = 'data/XML_constellation/Telesat.h5'

print(f"--- Exploring structure of: {file_path} ---")

def print_structure(name, obj):
    """A function to be passed to h5py's visititems method."""
    print(name)

try:
    with h5py.File(file_path, 'r') as f:
        print("Keys at the root level:", list(f.keys()))
        print("\nFull structure:")
        f.visititems(print_structure)

except FileNotFoundError:
    print(f"ERROR: File not found at {file_path}")
except Exception as e:
    print(f"An error occurred: {e}")

print("\n--- Exploration finished ---")

