# scheduling_app/algorythms/petrov_sokolitsyn.py

from typing import List, Tuple
from core.scheduler import calculate_makespan


def petrov_sokolitsyn_algorithm(processing_matrix: List[List[int]]) -> Tuple[List[int], int]:
    """
    Эвристический метод Петрова–Соколицына для flow shop (m >= 2).
    
    Сводит задачу к двухстаночной:
      A_i = sum(t[i][0 : m-1])  # все, кроме последнего станка
      B_i = sum(t[i][1 : m])    # все, кроме первого станка
    
    Затем применяет правило Джонсона к парам (A_i, B_i).
    
    Параметры:
    ----------
    processing_matrix : List[List[int]]
        Матрица n x m, m >= 2.
    
    Возвращает:
    ----------
    Tuple[List[int], int]
        (последовательность, makespan)
    """
    if not processing_matrix:
        return [], 0

    n = len(processing_matrix)
    m = len(processing_matrix[0])

    if m < 2:
        raise ValueError("Метод Петрова–Соколицына требует как минимум 2 станка.")

    # Строим псевдостанции A и B
    pseudo_jobs = []
    for i in range(n):
        row = processing_matrix[i]
        A = sum(row[:-1])  # все, кроме последнего
        B = sum(row[1:])   # все, кроме первого
        pseudo_jobs.append((A, B, i))

    # Применяем правило Джонсона к (A, B)
    group1 = []  # A <= B
    group2 = []  # A > B

    for A, B, idx in pseudo_jobs:
        if A <= B:
            group1.append((A, idx))
        else:
            group2.append((B, idx))

    group1.sort(key=lambda x: x[0])      # по возрастанию A
    group2.sort(key=lambda x: x[0], reverse=True)  # по убыванию B

    sequence = [idx for _, idx in group1] + [idx for _, idx in group2]
    makespan = calculate_makespan(processing_matrix, sequence)

    return sequence, makespan