import numpy as np

"""
Dependencies:
    - numpy | pip install numpy
"""


def calculate_dist_post_transitions(
    initial_dist: np.array, stochastic_mat: np.array, transitions: int
) -> np.array:
    if (
        not isinstance(initial_dist, np.ndarray)
        or not isinstance(stochastic_mat, np.ndarray)
        or transitions <= 0
    ):
        raise RuntimeError(
            "ERROR: Invalid parameters. Must provide initial distribution, stochastic matrix and whole, positive amount of transitions"
        )

    # First set result as copy with float conversion
    result = initial_dist.astype(float)

    # Multiply by matrix with transition probabilities, the amount of times specified
    for _ in range(transitions):
        result = result @ stochastic_mat

    return result


if __name__ == "__main__":
    # Vector representing intiial distributions (active, occasional, inactive, abandoned)
    initial_distribution = np.array([70, 20, 10, 0])

    # Initial stochastic matrix with transition probabilities
    stochastic_matrix = np.array(
        [
            [0.6, 0.3, 0.1, 0.0],
            [0.22, 0.55, 0.22, 0.01],
            [0.0, 0.3, 0.5, 0.2],
            [0.0, 0.0, 0.0, 1.0],
        ]
    )

    transitions = input("Enter amount of transitions to calculate: ")
    if transitions.isnumeric() and int(transitions) >= 1:
        try:
            updated_distribution = calculate_dist_post_transitions(
                initial_distribution, stochastic_matrix, int(transitions)
            )

            print(f"Initial state distributions:\n{initial_distribution}")
            print(
                f"State distributions after {transitions} transitions \n{updated_distribution}"
            )
        except Exception as e:
            print(e)
    else:
        print("Transitions must be a whole number greater than 0")
