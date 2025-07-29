"""
======================================================================
My Test Runner - Focused on Fault Tolerance
======================================================================
This script isolates and runs the test case for natural satellite
failures in the +Grid mode to analyze its behavior.
"""

def main():
    print("--- Running Fault Tolerance Test ---")
    print("======================================================================")

    # We are running Test(12/16) from the original test suite.
    print("\t\t\033[31mRunning ONLY: Natural satellite damage in +Grid mode\033[0m")
    
    # Import the specific test script
    import samples.XML_constellation.positive_Grid.natural_failure_satellites as FaultToleranceTest
    
    # Execute the function within that script
    FaultToleranceTest.natural_failure_satellites()

    print("======================================================================")
    print("--- End of Test ---")


if __name__ == "__main__":
    main()
