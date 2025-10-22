import numpy as np
import pandas as pd

"""
Dependencies:
    - numpy | pip install numpy
    - pandas | pip install pandas
    - openpyxl | pip install openpyxl
"""


# Function used in exercise 4 and 6 to obtain nth stochastic matrix (P^n)
def calculate_stochastic_matrix(
    base_matrix: np.array, n: int, filename: str = "stochastic_matrix_result.xlsx"
) -> None:
    if not isinstance(n, int) or n < 1:
        print("n must be an integer >= 1")
        return

    temp_matrix = base_matrix.copy()
    blocks = []

    for i in range(1, n + 1):
        result_matrix = temp_matrix @ base_matrix

        df_base = pd.DataFrame(np.round(base_matrix, 5))
        df_temp = pd.DataFrame(np.round(temp_matrix, 5))
        df_result = pd.DataFrame(np.round(result_matrix, 5))

        blocks.append(pd.DataFrame([[f"Multiplicación {i}"]]))

        blocks.append(df_temp)
        blocks.append(pd.DataFrame([[""] * base_matrix.shape[1]]))
        blocks.append(df_base)
        blocks.append(pd.DataFrame([["="] * base_matrix.shape[1]]))
        blocks.append(df_result)
        blocks.append(pd.DataFrame([[""] * base_matrix.shape[1]]))
        blocks.append(pd.DataFrame([[""] * base_matrix.shape[1]]))

        temp_matrix = result_matrix

    final_result = pd.concat(blocks, ignore_index=True)
    with pd.ExcelWriter(filename) as writer:
        final_result.to_excel(writer, index=False, header=False)


# Example usage:

# Homework's base stochastic matrix with probabilities
stochastic_matrix = np.array(
    [
        [0.6, 0.3, 0.1, 0.0],
        [0.2197, 0.5494, 0.2197, 0.0109],
        [0.0, 0.3, 0.5, 0.2],
        [0.0, 0.0, 0.0, 1.0],
    ]
)

calculate_stochastic_matrix(
    stochastic_matrix, n=11, filename="actividad_4_tarea_2.xlsx"
)
