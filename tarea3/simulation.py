import random
import heapq
from collections import deque

# For replication
SEED = 42
random.seed(SEED)

# Flag for verbose output (for debug)
VERBOSE = False


def simulate(
    sim_time: float,
    operators_count: int,
    arrival_rate: float,  # LAMBDA
    service_rate: float,  # MU
    queue_capacity: int,
) -> dict[str, object]:
    current_time = 0.0  # in minutes
    system_empty_time = 0.0  # total time system was empty
    sum_wait_times = 0.0  # total wait time in queue
    sum_system_times = 0.0  # total time in system

    total_customers = 0  # sum of all customers that arrived
    lost_customers = 0  # customers lost due to full queue
    serviced_customers = 0  # customers that completed service

    customer_queue = deque()  # queue of arrival times of waiting customers
    operators_busy = [False] * operators_count  # track if each operator is busy
    total_operator_busy_times = [0.0] * operators_count  # total busy time per operator

    arrival_time = random.expovariate(arrival_rate)
    # heap entries: (completion_time, operator_index, start_time, arrival_time_of_customer)
    service_completion_times: list[tuple] = []

    # Main simulation loop: process events until next event would be after sim_time
    while True:
        # Next completion is first in heap (soonest) or infinity if none
        next_completion = (
            service_completion_times[0][0] if service_completion_times else float("inf")
        )
        # Pick next event time, either arrival or completion
        next_event_time = min(arrival_time, next_completion)

        if next_event_time > sim_time:
            # No more events within simulation horizon
            break

        # Determine which event occurs
        if arrival_time <= next_completion:
            # Arrival event
            if len(customer_queue) == 0 and len(service_completion_times) == 0:
                # System was empty: add idle time since current_time
                system_empty_time += arrival_time - current_time

            current_time = arrival_time  # Update current time to arrival time
            total_customers += 1

            # If there is space in queue (waiting room), join; else lost
            if len(customer_queue) < queue_capacity:
                customer_queue.append(arrival_time)
                if VERBOSE:
                    print("Customer arrived at time {:.2f}".format(current_time))
            else:
                lost_customers += 1
                if VERBOSE:
                    print(
                        "Customer lost due to full queue at time {:.2f}".format(
                            current_time
                        )
                    )

            # Generate next arrival
            arrival_time = current_time + random.expovariate(arrival_rate)

        else:
            # Service completion event, popped from heap
            (
                service_completion_time,
                operator_index,
                start_time,
                arrival_time,
            ) = heapq.heappop(service_completion_times)

            # Update current_time to completion
            current_time = service_completion_time
            if VERBOSE:
                print(
                    f"Operator {operator_index} completed service at time {current_time:.2f}"
                )

            # Update operator busy time by actual service duration
            service_duration = service_completion_time - start_time
            total_operator_busy_times[operator_index] += service_duration
            operators_busy[operator_index] = False

            # Update wait/system-time aggregates for this completed customer
            wait_time = start_time - arrival_time
            sum_wait_times += wait_time
            sum_system_times += wait_time + service_duration
            serviced_customers += 1

        # After processing an event, assign as many queued customers as possible
        for index in range(operators_count):
            if (not operators_busy[index]) and len(customer_queue) > 0:
                arrival_time = customer_queue.popleft()
                start_time = current_time
                # schedule service
                service_time = random.expovariate(service_rate)
                completion_time = start_time + service_time
                # Insert completion time and related data in heap, ordered by soonest to complete
                heapq.heappush(
                    service_completion_times,
                    (completion_time, index, start_time, arrival_time),
                )
                operators_busy[index] = True
                if VERBOSE:
                    print(f"Operator {index} started service at time {start_time:.2f}")

    # AFTER SIMULATION, FINALIZE METRICS
    # Account for remaining idle time if system empty
    if not service_completion_times and not customer_queue and not any(operators_busy):
        system_empty_time += sim_time - current_time

    # For operators with services that would complete after sim_time, add busy time until sim_time
    for (
        completion_time,
        operator_index,
        start_time,
        _arrival,
    ) in service_completion_times:
        # worker was busy from start_time until min(completion_time, sim_time)
        busy_until = min(completion_time, sim_time)
        if busy_until > start_time:
            total_operator_busy_times[operator_index] += busy_until - start_time

    return {
        "sys_empty_proportion": (system_empty_time / sim_time if sim_time > 0 else 0),
        "lost_customers_proportion": (
            lost_customers / total_customers if total_customers > 0 else 0
        ),
        "avg_wait_time": (
            (sum_wait_times / serviced_customers) if serviced_customers > 0 else 0
        ),
        "avg_system_time": (
            (sum_system_times / serviced_customers) if serviced_customers > 0 else 0
        ),
        "operator_utilizations": [
            busy_time / sim_time for busy_time in total_operator_busy_times
        ],
    }


def run_original_system():
    results = simulate(
        sim_time=480,  # total simulation time in minutes (8 hours)
        operators_count=2,  # number of service operators
        arrival_rate=1 / 3.0,  # average of 1 arrival every 3 minutes
        service_rate=1 / 6.0,  # average service time of 6 minutes
        queue_capacity=10,  # maximum number of customers in queue
    )
    print("[Original System]")
    display_results(results)


def run_increased_operators_system():
    results = simulate(
        sim_time=480,  # total simulation time in minutes (8 hours)
        operators_count=3,  # increased number of service operators
        arrival_rate=1 / 3.0,  # average of 1 arrival every 3 minutes
        service_rate=1 / 6.0,  # average service time of 6 minutes
        queue_capacity=10,  # maximum number of customers in queue
    )
    print("[Increased Operators System]")
    display_results(results)


def run_reduced_arrival_rate_system():
    results = simulate(
        sim_time=480,  # total simulation time in minutes (8 hours)
        operators_count=2,  # number of service operators
        arrival_rate=1 / 4.0,  # average of 1 arrival every 4 minutes (15 per hour)
        service_rate=1 / 6.0,  # average service time of 6 minutes (10 per hour)
        queue_capacity=10,  # increased maximum number of customers in queue
    )
    print("[Reduced Arrival Rate System]")
    display_results(results)


def display_results(results: dict[str, object]):
    print("Simulation Results:")
    print(f"Proportion of time system was empty: {results['sys_empty_proportion']:.4f}")
    print(f"Proportion of lost customers: {results['lost_customers_proportion']:.4f}")
    print(f"Average wait time in queue: {results['avg_wait_time']:.2f} minutes")
    print(f"Average time in system: {results['avg_system_time']:.2f} minutes")
    for i, utilization in enumerate(results["operator_utilizations"]):
        print(f"Utilization of operator {i + 1}: {utilization:.4f}")
    print("================================================")


if __name__ == "__main__":
    run_original_system()
    run_increased_operators_system()
    run_reduced_arrival_rate_system()
