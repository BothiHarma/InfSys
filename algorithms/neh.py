# scheduling_app/algorithms/neh.py

from typing import List, Tuple
from core.scheduler import calculate_makespan


def neh_algorithm(processing_matrix: List[List[int]]) -> Tuple[List[int], int]:
    """
    Шаги:
    1. Сортируем детали по убыванию суммарного времени обработки.
    2. Последовательно вставляем каждую деталь в позицию, дающую минимальный makespan.
    
    Параметры:
    ----------
    processing_matrix : List[List[int]]
        Матрица обработки размером n x m.
    
    Возвращает:
    ----------
    Tuple[List[int], int]
        (лучшая_последовательность, makespan)
    """
    if not processing_matrix:
        return [], 0

    n = len(processing_matrix)
    m = len(processing_matrix[0])

    # сортировка по убыванию суммарного времени
    job_sums = [(sum(processing_matrix[i]), i) for i in range(n)]
    job_sums.sort(key=lambda x: x[0], reverse=True)
    ordered_jobs = [job_id for _, job_id in job_sums]

    # итеративная вставка
    current_sequence = [ordered_jobs[0]]

    for k in range(1, n):
        new_job = ordered_jobs[k]
        best_sequence = None
        best_makespan = float('inf')

        # пробуем вставить new_job в каждую возможную позицию
        for pos in range(len(current_sequence) + 1):
            candidate = current_sequence[:pos] + [new_job] + current_sequence[pos:]
            mksp = calculate_makespan(processing_matrix, candidate)
            if mksp < best_makespan:
                best_makespan = mksp
                best_sequence = candidate

        current_sequence = best_sequence

    final_makespan = calculate_makespan(processing_matrix, current_sequence)
    return current_sequence, final_makespan