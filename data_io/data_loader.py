import pandas as pd
import numpy as np
from typing import List, Tuple


def load_from_excel(file_path_or_buffer) -> List[List[int]]:
    """
    Загружает матрицу обработки из Excel-файла (.xlsx).
    
    Ожидаемый формат:
    - Таблица без заголовков или с пропущенными заголовками.
    - Каждая строка = деталь, каждый столбец = станок.
    - Все ячейки — положительные целые числа.
    
    Параметры:
    ----------
    file_path_or_buffer : str или file-like объект
        Путь к файлу или загруженный байтовый поток (например, из Streamlit).
    
    Возвращает:
    ----------
    List[List[int]]
        Матрица обработки размером n x m.
    """
    try:
        df = pd.read_excel(file_path_or_buffer, header=None, dtype=str)
    except Exception as e:
        raise ValueError(f"Не удалось прочитать Excel-файл: {e}")

    # удаляем пустые строки и столбцы
    df.dropna(how='all', inplace=True)
    df.dropna(axis=1, how='all', inplace=True)

    if df.empty:
        raise ValueError("Файл пуст или не содержит данных.")

    try:
        df = df.astype(int)
    except ValueError as e:
        raise ValueError("Все значения в Excel-файле должны быть целыми числами.")

    matrix = df.values.tolist()
    _validate_matrix(matrix)
    return matrix


def generate_random_matrix(n: int, m: int, min_time: int = 1, max_time: int = 100) -> List[List[int]]:
    """
    Генерирует случайную матрицу обработки.
    
    Параметры:
    ----------
    n : int
        Число деталей (строк), 3 ≤ n ≤ 100
    m : int
        Число станков (столбцов), 3 ≤ m ≤ 100
    min_time : int
        Минимальная длительность операции (≥1)
    max_time : int
        Максимальная длительность операции (≥min_time)
    
    Возвращает:
    ----------
    List[List[int]]
        Случайная матрица n x m.
    """
    if not (3 <= n <= 100):
        raise ValueError("Число деталей n должно быть в диапазоне [3, 100].")
    if not (2 <= m <= 100):
        raise ValueError("Число станков m должно быть в диапазоне [3, 100].")
    if min_time < 1:
        raise ValueError("Минимальное время обработки должно быть ≥ 1.")
    if max_time < min_time:
        raise ValueError("max_time не может быть меньше min_time.")

    rng = np.random.default_rng()
    matrix = rng.integers(min_time, max_time + 1, size=(n, m)).tolist()
    return matrix


def _validate_matrix(matrix: List[List[int]]) -> None:
    """
    Проверяет корректность матрицы обработки.
    """
    if not matrix:
        raise ValueError("Матрица не должна быть пустой.")

    n = len(matrix)
    m = len(matrix[0])

    if not (3 <= n <= 100):
        raise ValueError(f"Число деталей (строк) должно быть от 3 до 100. Получено: {n}")
    if not (3 <= m <= 100):
        raise ValueError(f"Число станков (столбцов) должно быть от 3 до 100. Получено: {m}")

    for i, row in enumerate(matrix):
        if len(row) != m:
            raise ValueError(f"Несогласованное число столбцов в строке {i}. Ожидалось {m}.")
        for j, val in enumerate(row):
            if not isinstance(val, int) or val < 1:
                raise ValueError(f"Значение в ячейке [{i}][{j}] должно быть целым положительным числом. Получено: {val}")