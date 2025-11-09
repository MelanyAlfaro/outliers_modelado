from simulator import Simulator
from speed_mode import SpeedMode

def start_program():
    """
    Shows an interface for the user and runs the program with the input given.
    
    Asks the user for the maximum time for each simulation run, the amount of
    simulation runs and the speed mode for the logger. Then, runs the simulation
    with the given parameters.
    """
    # Show of the program
    print("\n" + "=" * 60)
    print(f"COMPUTER MESSAGE SYSTEM SIMULATION")
    print("=" * 60)
    
    # Ask the user for the corresponding parameters
    print("Please enter the simulation parameters.")
    
    # Request maximum simulation time
    while True:
        try:
            max_sim_time = float(input("\n- Enter maximum time for every simulation run (seconds): "))
            if max_sim_time <= 0:
                print("Please enter a valid number above 0.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter a valid number.")
    
    # Get number of runs
    while True:
        try:
            requested_runs = int(input("\n- Enter number of simulation runs: "))
            if requested_runs <= 0:
                print("Please enter a valid number above 0.")
                continue
            break
        except:
            print("Invalid input. Please enter a valid number.")
    
    # Get speed mode
    print("\nSelect the speed mode for the log messages.")
    print("    1. SLOW: adds a delay to slow down messages (for observation)")
    print("    2. FAST: executes program and shows messages without delay")
    print("    3. SILENT: executes without delay, suppressing output")
    
    while True:
        try:
            speed_choice = int(input("- Enter the speed mode you want (1-3): "))
            if speed_choice == 1:
                speed_mode = SpeedMode.SLOW
                break
            elif speed_choice == 2:
                speed_mode = SpeedMode.FAST
                break
            elif speed_choice == 3:
                speed_mode = SpeedMode.SILENT
                break
            else:
                print("Please enter a number between 1 and 3.")
        except:
            print("Invalid input. Please enter a valid number.")
    
    # Create and run simulator
    print(f"\nStarting simulation with {requested_runs} run(s).")
    print("=" * 60)
    
    sim = Simulator(max_sim_time, requested_runs, speed_mode)
    sim.run()
    
    print("\n" + "=" * 60)
    print("SIMULATION COMPLETED ☺")
    print("=" * 60)

if __name__ == "__main__":
    start_program()
