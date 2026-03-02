# scheduling_app/analytics/metrics.py

import pandas as pd
from typing import List, Dict, Tuple
#from core.scheduler import calculate_makespan
from visualization.gantt import build_gantt_dataframe

def analyze_schedule(
    processing_matrix: List[List[int]],
    sequence: List[int]) -> Dict[str, float]:
    """
    Полный BI-анализ расписания.
    """
    
    df_gantt = build_gantt_dataframe(processing_matrix, sequence)
    
    if df_gantt.empty:
        makespan = 0.0
        total_processing_time = 0.0
        completion_times = pd.Series([], dtype=float)
    else:
        makespan = float(df_gantt["Finish"].max())
        df_gantt = df_gantt.copy()  
        df_gantt["Duration"] = df_gantt["Finish"] - df_gantt["Start"]
        total_processing_time = float(df_gantt["Duration"].sum())
        completion_times = df_gantt.groupby('Job')['Finish'].max()

    n_machines = len(processing_matrix[0]) if processing_matrix and processing_matrix[0] else 1
    total_capacity = n_machines * makespan
    total_idle_time = total_capacity - total_processing_time
    equipment_utilization = (total_processing_time / total_capacity * 100) if total_capacity > 0 else 0.0

    if completion_times.empty:
        avg_completion_time = max_completion_time = min_completion_time = 0.0
    else:
        avg_completion_time = float(completion_times.mean())
        max_completion_time = float(completion_times.max())
        min_completion_time = float(completion_times.min())

    return {
        "makespan": makespan,
        "total_idle_time": total_idle_time,
        "equipment_utilization": equipment_utilization,
        "avg_completion_time": avg_completion_time,
        "max_completion_time": max_completion_time,
        "min_completion_time": min_completion_time,
        "n_jobs": len(completion_times),
        "n_machines": n_machines
    }

def compare_schedules(
    processing_matrix: List[List[int]],
    sequences: Dict[str, List[int]]
) -> pd.DataFrame:
    """
    Сравнивает несколько расписаний (например, "до" и "после").
    
    Параметры:
    ----------
    processing_matrix : List[List[int]]
        Матрица обработки.
    sequences : Dict[str, List[int]]
        Словарь вида {"Исходное": [0,1,2], "NEH": [1,0,2], ...}
    
    Возвращает:
    ----------
    pd.DataFrame
        Таблица с метриками для каждого расписания.
    """
    results = {}
    for name, seq in sequences.items():
        metrics = analyze_schedule(processing_matrix, seq)
        results[name] = metrics
    
    df = pd.DataFrame(results).T
    df.index.name = "Расписание"
    return df


def calculate_idle_by_machine(df_gantt: pd.DataFrame, makespan: int) -> pd.DataFrame:
    """
    Рассчитывает простои по каждому станку.
    df_gantt должен содержать колонки: Machine, Job, Start, Finish.
    """
    if "Duration" not in df_gantt.columns:
        df_gantt = df_gantt.copy()
        df_gantt["Duration"] = df_gantt["Finish"] - df_gantt["Start"]
    
    machine_stats = df_gantt.groupby('Machine').agg(
        TotalWorkTime=('Duration', 'sum'),
        FirstStart=('Start', 'min'),
        LastFinish=('Finish', 'max')
    ).reset_index()

    machine_stats['Span'] = machine_stats['LastFinish'] - machine_stats['FirstStart']
    machine_stats['LeadingIdle'] = machine_stats['FirstStart']
    machine_stats['TrailingIdle'] = makespan - machine_stats['LastFinish']
    machine_stats['InternalIdle'] = machine_stats['Span'] - machine_stats['TotalWorkTime']
    machine_stats['IdleTime'] = (
        machine_stats['LeadingIdle'] +
        machine_stats['InternalIdle'] +
        machine_stats['TrailingIdle']
    )
    machine_stats['Utilization'] = (
        machine_stats['TotalWorkTime'] / makespan * 100
    )

    return machine_stats[[
        'Machine', 'TotalWorkTime', 'IdleTime', 'Utilization'
    ]]

def generate_bi_report(
    processing_matrix: List[List[int]],
    initial_sequence: List[int],
    optimal_sequence: List[int],
    algorithm_name: str
) -> Dict:
    """
    Генерирует полный BI-отчёт для UI.
    """
    # Анализ обоих расписаний
    before = analyze_schedule(processing_matrix, initial_sequence)
    after = analyze_schedule(processing_matrix, optimal_sequence)

    # Эффективность
    improvement_makespan = (1 - after["makespan"] / before["makespan"]) * 100
    improvement_idle = (1 - after["total_idle_time"] / before["total_idle_time"]) * 100 if before["total_idle_time"] > 0 else 0.0

    # Простои по станкам (только после оптимизации)
    df_after = build_gantt_dataframe(processing_matrix, optimal_sequence)
    idle_by_machine = calculate_idle_by_machine(df_after, after["makespan"])

    return {
        "summary": {
            "before": before,
            "after": after,
            "improvement_makespan": improvement_makespan,
            "improvement_idle": improvement_idle,
            "algorithm": algorithm_name
        },
        "idle_by_machine": idle_by_machine
    }