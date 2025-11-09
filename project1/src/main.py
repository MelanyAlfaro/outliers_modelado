from simulator import Simulator
from speed_mode import SpeedMode
import argparse
import sys


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments for the simulation.
    """
    parser = argparse.ArgumentParser(
        description="Computer Message System Simulation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
    Examples:
    python3 main.py --time 60 --runs 5 --speed fast
    python3 main.py -t 120 -r 10 -s silent
    python3 main.py (runs in interactive mode)
            """,
    )

    parser.add_argument(
        "-t",
        "--time",
        type=float,
        help="Maximum time for each simulation run in seconds (float)",
    )

    parser.add_argument(
        "-r", "--runs", type=int, help="Number of simulation runs (int)"
    )

    parser.add_argument(
        "-s",
        "--speed",
        choices=["slow", "fast", "silent"],
        help="Speed mode: slow, fast, or silent",
    )

    return parser.parse_args()


def get_speed_mode(speed_str) -> SpeedMode:
    """
    Convert speed mode string to SpeedMode enum.

    Returns FAST as default value if entered string is not valid.
    """
    speed_map = {
        "slow": SpeedMode.SLOW,
        "fast": SpeedMode.FAST,
        "silent": SpeedMode.SILENT,
    }
    return speed_map.get(speed_str.lower(), SpeedMode.FAST)


def get_interactive_interface() -> tuple[float, int, SpeedMode]:
    """
    Shows an interface for the user to run the program with the input given.

    Asks the user for the maximum time for each simulation run, the amount of
    simulation runs and the speed mode for the logger.
    """
    # Ask the user for the corresponding parameters
    print("Please enter the simulation parameters.")

    # Request maximum simulation time
    while True:
        try:
            max_sim_time = float(
                input("\n- Enter maximum time for every simulation run (seconds): ")
            )
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

    return max_sim_time, requested_runs, speed_mode


def run_simulation(max_sim_time, requested_runs, speed_mode) -> None:
    """
    Run the simulation with the given parameters.
    """
    print(f"\nStarting simulation with {requested_runs} run(s).")

    sim = Simulator(max_sim_time, requested_runs, speed_mode)
    sim.run()

    print("\n" + "=" * 60)
    print("SIMULATION COMPLETED ☺")
    print("=" * 60)


def start_program() -> None:
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

    args = parse_arguments()

    # Check if all arguments were given via command-line
    if args.runs is not None and args.time is not None and args.speed is not None:
        # Run the program with the command-line arguments
        max_sim_time = args.time
        requested_runs = args.runs
        speed_mode = get_speed_mode(args.speed)
        print(f"Running program with command-line input:")
        print(f"- Runs: {requested_runs}")
        print(f"- Max Time: {max_sim_time}s")
        print(f"- Speed Mode: {args.speed.upper()}")

    else:
        # Run the interactive interface
        max_sim_time, requested_runs, speed_mode = get_interactive_interface()

    run_simulation(max_sim_time, requested_runs, speed_mode)


if __name__ == "__main__":
    start_program()
