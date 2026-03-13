# scheduling_app/visualization/gantt_chart.py

import pandas as pd
import plotly.express as px
import colorsys
from typing import List, Optional, Dict
from plotly.graph_objs._figure import Figure
from visualization.gantt import build_gantt_dataframe


def _create_color_map(job_ids: List[str], palette: str = "plotly") -> Dict[str, str]:
    """
    Генерирует цветовую карту.
    
    Параметры:
    ----------
    palette : str
        "plotly", "dark24", "russian_flag"
    """
    n = len(job_ids)
    sorted_jobs = sorted(job_ids)
    
    if palette == "russian_flag":
        # Базовые цвета флага
        silver = (192, 192, 192)   # серебристый
        blue = (0, 57, 166)         # синий
        red = (213, 43, 30)         # красный
        
        color_array = []
        
        # Делим на 3 равные части
        part_size = n // 3
        remainder = n % 3
        
        # Определяем границы частей
        part1_end = part_size + (1 if remainder > 0 else 0)
        part2_end = part1_end + part_size + (1 if remainder > 1 else 0)
        # part3_end = n
        
        for i in range(n):
            if i < part1_end:
                # Первая часть: градиент от белого к серебристому
                t = i / max(1, part1_end - 1) if part1_end > 1 else 0
                base = (255, 255, 255)  # белый
                r = int(base[0] * (1 - t) + silver[0] * t)
                g = int(base[1] * (1 - t) + silver[1] * t)
                b = int(base[2] * (1 - t) + silver[2] * t)
            elif i < part2_end:
                # Вторая часть: градиент от светло-синего к синему
                local_i = i - part1_end
                local_n = part2_end - part1_end
                t = local_i / max(1, local_n - 1) if local_n > 1 else 0
                light_blue = (173, 216, 230)  # светло-голубой
                r = int(light_blue[0] * (1 - t) + blue[0] * t)
                g = int(light_blue[1] * (1 - t) + blue[1] * t)
                b = int(light_blue[2] * (1 - t) + blue[2] * t)
            else:
                # Третья часть: градиент от оранжевого к красному
                local_i = i - part2_end
                local_n = n - part2_end
                t = local_i / max(1, local_n - 1) if local_n > 1 else 0
                orange = (255, 165, 0)  # оранжевый
                r = int(orange[0] * (1 - t) + red[0] * t)
                g = int(orange[1] * (1 - t) + red[1] * t)
                b = int(orange[2] * (1 - t) + red[2] * t)
            
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            color_array.append(hex_color)
        
        return {job: color_array[i] for i, job in enumerate(sorted_jobs)}

    else:
        if n <= 10:
            base_colors = px.colors.qualitative.Plotly
        elif n <= 24:
            base_colors = px.colors.qualitative.Dark24
        else:
            
            base_colors = []
            for i in range(n):
                hue = i / n
                rgb = colorsys.hsv_to_rgb(hue, 0.8, 0.95)
                hex_color = '#{:02x}{:02x}{:02x}'.format(
                    int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255)
                )
                base_colors.append(hex_color)
        
        color_map = {}
        for i, job in enumerate(sorted_jobs):
            color_map[job] = base_colors[i % len(base_colors)]
        return color_map

def create_gantt_figure(
    processing_matrix: List[List[int]], 
    sequence: List[int], 
    title: str = "",
    color_map: Optional[Dict[str, str]] = None,
    fixed_height: int = 600,
    width: int = 1200
) -> Figure:
    df_gantt = build_gantt_dataframe(processing_matrix, sequence)
    if df_gantt.empty:
        raise ValueError("Невозможно построить диаграмму: пустые данные.")

    df_gantt = df_gantt.copy()
    df_gantt["Duration"] = df_gantt["Finish"] - df_gantt["Start"]
    m_act = len(processing_matrix[0]) if processing_matrix else 1

    
    df_gantt["Machine"] = "M" + df_gantt["Machine"].str.replace("Machine ", "")
    
    makespan = df_gantt["Finish"].max()

    if color_map is None:
        all_jobs = [f"J{i}" for i in range(len(processing_matrix))]
        color_map = _create_color_map(all_jobs)

    fig = px.bar(
        df_gantt,
        x="Duration",
        y="Machine",
        color="Job",
        color_discrete_map=color_map,
        text="Job",
        orientation="h",
        base="Start",
        height=fixed_height,
        width=width,
        title=title,
        hover_data={"Job": True, "Start": True, "Finish": True}
    )
    fig.update_traces(
        textposition="inside",
        textfont=dict(color="white", size=8), 
        insidetextanchor="middle"
    )
    dtick_y = max(1, m_act // 50)
    fig.update_layout(
        xaxis_title="Время (единицы)",
        yaxis_title="Станок",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5,
            title="Детали"
        ),
        xaxis=dict(
            range=[0, makespan],
            tickmode='auto',      
            nticks=20,
            showgrid=True,
            autorange=False
        ),
        yaxis=dict(
            tickmode='linear',
            tick0=0,
            dtick=dtick_y, # было 1
            showgrid=True,
            autorange="reversed",
            tickfont=dict(size=8)
        ),
        dragmode="pan",
        hovermode="closest",
        margin=dict(b=100, r=50),
        autosize=False
    )
    return fig
