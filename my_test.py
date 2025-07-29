"""
My custom test file
"""
def main():
    print("--- My Custom Test Runner ---")

    # Chỉ chạy bài test 16
    print("\t\t\033[31mRunning ONLY Test(16) : calculate the least hop path route in +Grid mode\033[0m")
    # minimum hop count routing in +Grid mode
    import samples.XML_constellation.positive_Grid.least_hop_path as POSITIVE_GRID_LEAST_HOP_PATH_ROUTING_TEST
    POSITIVE_GRID_LEAST_HOP_PATH_ROUTING_TEST.least_hop_path()

    print("--- End of Custom Test ---")

# This part remains the same
if __name__ == "__main__":
    main()

