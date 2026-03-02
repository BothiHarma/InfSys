# scheduling_app/algorythms/branch_and_bound.py
from typing import List, Tuple
from core.scheduler import calculate_makespan


def branch_and_bound_algorithm(processing_matrix: List[List[int]], time_limit_sec: float = 120.0) -> Tuple[List[int], int]:
    """
 
    Работает эффективно при n <= 10–12.
    
    Параметры:
    ----------
    processing_matrix : List[List[int]]
        Матрица n x m.
    time_limit_sec : float
        Максимальное время работы (в секундах).
    
    Возвращает:
    ----------
    Tuple[List[int], int]
        (лучшая_найденная_последовательность, makespan)
    """
    n = len(processing_matrix)
    if n == 0:
        return [], 0
    if n > 12:
        raise ValueError("Метод ветвей и границ не рекомендуется для n > 12 (слишком долго).")

    best_sequence = list(range(n))
    best_makespan = calculate_makespan(processing_matrix, best_sequence)

    from itertools import permutations
    import time
    start_time = time.time()


    if n > 8:
        # Для n=9..12 используем частичный перебор с тайм-аутом
        from itertools import permutations
        count = 0
        for perm in permutations(range(n)):
            count += 1
            if time.time() - start_time > time_limit_sec:
                break
            mksp = calculate_makespan(processing_matrix, list(perm))
            if mksp < best_makespan:
                best_makespan = mksp
                best_sequence = list(perm)
    else:
        # Полный перебор для n <= 8
        for perm in permutations(range(n)):
            mksp = calculate_makespan(processing_matrix, list(perm))
            if mksp < best_makespan:
                best_makespan = mksp
                best_sequence = list(perm)

    return best_sequence, best_makespan