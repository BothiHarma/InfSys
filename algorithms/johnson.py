from typing import List, Tuple
from core.scheduler import calculate_makespan


def johnson_algorithm(processing_matrix: List[List[int]]) -> Tuple[List[int], int]:
    """
    Реализация классического алгоритма Джонсона для задачи flow shop
    с двумя станками (m = 2). Минимизирует makespan.

    Правило:
    - Деталь i помещается в начало последовательности, если P[i][0] <= P[i][1]
    - Иначе — в конец последовательности.
    - Сортировка внутри групп по возрастанию соответствующего времени.

    Параметры:
    ----------
    processing_matrix : List[List[int]]
        Матрица обработки размером n x 2.
        Каждая строка: [время_на_станке_0, время_на_станке_1]

    Возвращает:
    ----------
    Tuple[List[int], int]
        (оптимальная_последовательность, makespan)
    """
    if not processing_matrix:
        return [], 0

    m = len(processing_matrix[0])
    if m != 2:
        raise ValueError("Алгоритм Джонсона применим только для двух станков (m=2).")

    n = len(processing_matrix)
    group1 = []  # P[i][0] <= P[i][1]
    group2 = []  # P[i][0] > P[i][1]

    for i in range(n):
        t1, t2 = processing_matrix[i]
        if t1 <= t2:
            group1.append((t1, i))
        else:
            group2.append((t2, i))

    # Сортируем первую группу по возрастанию t1
    group1.sort(key=lambda x: x[0])
    # Сортируем вторую группу по убыванию t2 
    group2.sort(key=lambda x: x[0], reverse=True)

    # Формируем последовательность
    sequence = [idx for _, idx in group1] + [idx for _, idx in group2]

    # Рассчитываем makespan
    makespan = calculate_makespan(processing_matrix, sequence)

    return sequence, makespan


if __name__ == "__main__":
    print("HDF")
    P = [
    [3, 2],
    [1, 4],
    [5, 1]
    ]
    seq, mksp = johnson_algorithm(P)
    print(seq)   # [1, 0, 2] → J1, J0, J2
    print(mksp)  # 9