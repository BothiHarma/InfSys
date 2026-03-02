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
        colors_rgb = [
            (192, 192, 192),  # серебристый 
            (0, 57, 166),      # синий
            (213, 43, 30)      # красный
        ]
        
        color_array = []
        for i in range(n):
            t = i / max(1, n - 1)
            
            if t <= 0.5:
                t_local = t * 2
                r = int(colors_rgb[0][0] * (1 - t_local) + colors_rgb[1][0] * t_local)
                g = int(colors_rgb[0][1] * (1 - t_local) + colors_rgb[1][1] * t_local)
                b = int(colors_rgb[0][2] * (1 - t_local) + colors_rgb[1][2] * t_local)
            else:
                t_local = (t - 0.5) * 2
                r = int(colors_rgb[1][0] * (1 - t_local) + colors_rgb[2][0] * t_local)
                g = int(colors_rgb[1][1] * (1 - t_local) + colors_rgb[2][1] * t_local)
                b = int(colors_rgb[1][2] * (1 - t_local) + colors_rgb[2][2] * t_local)
            
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
        
        print("\n\n\n\nJFJFJFJF\n\n\n\n\n")
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
            autorange=True,
            tickfont=dict(size=8)  
        ),
        dragmode="pan",
        hovermode="closest",
        margin=dict(b=100, r=50),
        autosize=False
    )
    return fig
