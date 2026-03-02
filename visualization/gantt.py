# scheduling_app/visualization/gantt.py

import pandas as pd
from typing import List, Union
import numpy as np


def build_gantt_dataframe(processing_matrix, sequence: List[int]) -> pd.DataFrame:
    if not processing_matrix or not sequence:
        return pd.DataFrame(columns=["Станок", "Деталь", "Начало", "Окончание"])

    # Нормализация матрицы
    if isinstance(processing_matrix, np.ndarray):
        matrix = processing_matrix.tolist()
    else:
        matrix = processing_matrix

    n = len(sequence)
    m = len(matrix[0])

    # Валидация
    if any(len(row) != m for row in matrix):
        raise ValueError("Несогласованное число станков.")
    if not all(0 <= job < len(matrix) for job in sequence):
        raise ValueError("Некорректные ID деталей.")

    # Сброс времён
    completion_on_machine = [0] * m
    completion_of_job = [0] * n

    records = []
    for i, job_id in enumerate(sequence):
        for j in range(m):
            duration = matrix[job_id][j]
            if duration <= 0:
                raise ValueError(f"Длительность должна быть > 0. Деталь {job_id}, станок {j}")

            start_time = max(completion_of_job[i], completion_on_machine[j])
            finish_time = start_time + duration

            completion_of_job[i] = finish_time
            completion_on_machine[j] = finish_time

            records.append({
                "Machine": f"Machine {j}",
                "Job": f"J{job_id}",
                "Start": start_time,
                "Finish": finish_time
            })


    return pd.DataFrame(records)