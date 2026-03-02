# scheduling_app/core/scheduler.py

import numpy as np
from numba import jit
from typing import List


@jit(nopython=True)
def _calculate_makespan_numba(P: np.ndarray, sequence: np.ndarray) -> int:
    """
    Внутренняя JIT-функция, работающая с NumPy-массивами.
    """
    n = sequence.shape[0]
    m = P.shape[1]

    # Матрица завершения
    completion = np.zeros((n, m), dtype=np.int64)

    for i in range(n):
        job_id = sequence[i]
        for j in range(m):
            duration = P[job_id, j]
            if i == 0 and j == 0:
                completion[i, j] = duration
            elif i == 0:
                completion[i, j] = completion[i, j - 1] + duration
            elif j == 0:
                completion[i, j] = completion[i - 1, j] + duration
            else:
                completion[i, j] = max(completion[i - 1, j], completion[i, j - 1]) + duration

    return int(completion[n - 1, m - 1])


def calculate_makespan(processing_matrix: List[List[int]], sequence: List[int]) -> int:
    """
    Публичный интерфейс: принимает списки, преобразует в numpy, вызывает JIT-версию.
    """
    P = np.array(processing_matrix, dtype=np.int64)
    seq = np.array(sequence, dtype=np.int64)
    return _calculate_makespan_numba(P, seq)