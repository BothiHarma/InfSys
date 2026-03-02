# scheduling_app/app/main.py

import streamlit as st
import time
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
from io import BytesIO

from data_io.data_loader import load_from_excel, generate_random_matrix
from data_io.excel_exporter import create_excel_report
from algorithms.johnson import johnson_algorithm
from algorithms.petrov_sokolitsyn import petrov_sokolitsyn_algorithm
from algorithms.branch_and_bound import branch_and_bound_algorithm
from algorithms.neh import neh_algorithm 
from visualization.gantt_chart import create_gantt_figure, _create_color_map
from visualization.gantt import build_gantt_dataframe
from analytics.metrics import generate_bi_report


# прокрутка графика
def scrollable_plot(fig, max_height: int = 600):
    # include_plotlyjs='require' или 'inline' — локальная загрузка
    chart_html = fig.to_html(include_plotlyjs='inline', full_html=False)
    scrollable_html = f"""
    <div style="
        max-height: {max_height}px;
        overflow-y: auto;
        border: 1px solid #ddd;
        padding: 10px;
        border-radius: 5px;
        background: white;
    ">
        {chart_html}
    </div>
    """
    components.html(scrollable_html, height=max_height + 50, scrolling=False)
st.set_page_config(page_title="Оперативное планирование", layout="wide")
st.title("Программный модуль оперативно-календарного планирования")
st.markdown("""
Предприятия единичного и мелкосерийного типа характеризуются малым 
объемом выпуска одинаковых изделий и широкой номенклатурой деталей и 
операций, выполняемых на рабочих местах. Для таких предприятий особенно 
актуальна задача автоматизации оперативно-календарного планирования, 
целью которого является составление оптимального расписания запуска 
деталей в обработку.  
 **Число деталей n = 3–100**, **Число станков = 2–100**.  
""")

# === Шаг 1: Ввод данных ===
st.header("1. Ввод исходных данных")
data_source = st.radio(
    "Источник данных:",
    ("Загрузить Excel (.xlsx)", "Сгенерировать случайные данные", "Ручной ввод"),
    index=1
)

if "processing_matrix" not in st.session_state:
    st.session_state.processing_matrix = None

if data_source == "Загрузить Excel (.xlsx)":
    uploaded_file = st.file_uploader("Выберите файл .xlsx", type=["xlsx"])
    if uploaded_file:
        try:
            matrix = load_from_excel(BytesIO(uploaded_file.getvalue()))
            st.session_state.processing_matrix = matrix
            n, m = len(matrix), len(matrix[0])
            st.success(f"✅ Загружено: {n} деталей × {m} станков")
        except Exception as e:
            st.error(f"❌ Ошибка загрузки: {e}")
elif data_source == "Сгенерировать случайные данные":
    n = st.slider("Число деталей (n)", 3, 100, 5)
    m = st.slider("Число станков (m)", 2, 100, 3)
    min_t, max_t = st.slider("Диапазон времени обработки", 1, 100, (5, 20))
    if st.button("Сгенерировать данные"):
        try:
            matrix = generate_random_matrix(n, m, min_t, max_t)
            st.session_state.processing_matrix = matrix
            st.success(f"✅ Сгенерировано: {n} деталей × {m} станков")
        except Exception as e:
            st.error(f"❌ Ошибка генерации: {e}")

elif data_source == "Ручной ввод":
    st.write("Укажите размеры матрицы:")
    col_n, col_m = st.columns(2)
    with col_n:
        n_manual = st.number_input("Число деталей (n)", min_value=3, max_value=15, value=5, step=1)
    with col_m:
        m_manual = st.number_input("Число станков (m)", min_value=2, max_value=15, value=3, step=1)
    
    st.write(f"Введите матрицу обработки ({n_manual} × {m_manual}):")
    
    default_data = [[1 for _ in range(m_manual)] for _ in range(n_manual)]
    df_manual = pd.DataFrame(
        default_data,
        columns=[f"Станок {j}" for j in range(m_manual)],
        index=[f"Деталь {i}" for i in range(n_manual)]
    )
    
    edited_df = st.data_editor(
        df_manual,
        use_container_width=True,
        key="manual_matrix_editor"
    )
    
    if st.button("✅ Применить матрицу"):
        try:
            matrix = edited_df.values.astype(int).tolist()
            for i, row in enumerate(matrix):
                for j, val in enumerate(row):
                    if val <= 0:
                        raise ValueError(f"Значение [{i}][{j}] должно быть > 0")
            
            st.session_state.processing_matrix = matrix
            st.success(f"✅ Матрица применена: {n_manual} деталей × {m_manual} станков")
        except Exception as e:
            st.error(f"❌ Ошибка ввода: {e}")

# === Оптимизация ===
processing_matrix = st.session_state.processing_matrix

if processing_matrix is not None:
    n_act = len(processing_matrix)
    m_act = len(processing_matrix[0])
    
    st.subheader("2. Выбор алгоритма оптимизации")
    st.info(f"Обнаружена матрица: **{n_act} деталей × {m_act} станков**")
    
    available_algorithms = []
    if m_act == 2:
        available_algorithms.append("Johnson (точный, m=2)")
    else:
        available_algorithms.append("NEH (эвристика, n=3–100, m≥2)")
        available_algorithms.append("Петров–Соколицын (эвристика, m≥3)")
        if n_act <= 12:
            available_algorithms.append("Ветви и границы (точный, n≤12)")
        else:
            available_algorithms.append("Ветви и границы (недоступен: n>12)")

    selected_algo = st.selectbox("Выберите алгоритм:", available_algorithms)
    
    if st.button("🚀 Запустить оптимизацию"):
        try:
            initial_seq = list(range(n_act))
            
            start_time = time.time()
            
            if "Johnson" in selected_algo and m_act == 2:
                optimal_seq, optimal_mksp = johnson_algorithm(processing_matrix)
            elif "NEH" in selected_algo:
                optimal_seq, optimal_mksp = neh_algorithm(processing_matrix)
            elif "Петров" in selected_algo and m_act >= 3:
                optimal_seq, optimal_mksp = petrov_sokolitsyn_algorithm(processing_matrix)
            elif "Ветви" in selected_algo and n_act <= 12:
                optimal_seq, optimal_mksp = branch_and_bound_algorithm(processing_matrix)
            else:
                st.error("Выбранный алгоритм не может быть применён к текущим данным.")
                st.stop()
            
            elapsed_ms = (time.time() - start_time) * 1000
            
            report = generate_bi_report(
                processing_matrix,
                initial_seq,
                optimal_seq,
                selected_algo
            )
            before = report["summary"]["before"]
            after = report["summary"]["after"]
            improvement_makespan = report["summary"]["improvement_makespan"]
            
            # === Результаты ===
            st.subheader("3. Результаты оптимизации")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Длительность цикла (до)", f"{int(before['makespan'])}")
            col2.metric("Длительность цикла (после)", f"{int(after['makespan'])}")
            col3.metric("Эффект оптимизации", f"{improvement_makespan:.1f}%")
            col4.metric("Время расчёта", f"{elapsed_ms:.1f} мс")
            
            st.write("**Оптимальная последовательность:**", " → ".join([f"Деталь {i}" for i in optimal_seq]))
            
            # === BI-аналитика ===
            st.subheader("4. BI-аналитика производственного расписания")
            kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
            kpi_col1.metric("Загрузка оборудования", f"{after['equipment_utilization']:.1f}%")
            kpi_col2.metric("Общие простои", f"{int(after['total_idle_time'])}")
            kpi_col3.metric("Среднее время выпуска", f"{after['avg_completion_time']:.1f}")
            
            # перевод на русский
            idle_df_ui = report["idle_by_machine"].rename(columns={
                "Machine": "Станок",
                "TotalWorkTime": "Время работы",
                "IdleTime": "Простой",
                "Utilization": "Загрузка (%)"
            })
            st.write("**Простои по станкам (оптимизированное расписание):**")
            st.dataframe(idle_df_ui.round(2).set_index("Станок"))

            # === Круговые диаграммы ===
            st.subheader("5. Распределение ресурсов")

            with st.expander("📊 Простои по станкам", expanded=False):
                idle_pie = report["idle_by_machine"][["Machine", "IdleTime"]].copy()
                idle_pie = idle_pie[idle_pie["IdleTime"] > 0]
                if not idle_pie.empty:
                    n_categories = len(idle_pie)
                    height = min(600 + max(0, n_categories - 10) * 20, 1200)
                    
                    fig_idle_pie = px.pie(
                        idle_pie, 
                        names="Machine", 
                        values="IdleTime",
                        title=f"Простои по {n_categories} станкам"
                    )
                    fig_idle_pie.update_layout(
                        height=height,
                        legend=dict(
                            orientation="v",
                            yanchor="top",
                            y=1.0,
                            xanchor="left",
                            x=1.02,
                            font=dict(size=10)
                        )
                    )
                    st.plotly_chart(fig_idle_pie, use_container_width=True)
                else:
                    st.info("Нет простоев")

            with st.expander("📊 Время завершения по деталям", expanded=False):
                df_after = build_gantt_dataframe(processing_matrix, optimal_seq)
                completion_by_job = df_after.groupby('Job')['Finish'].max().reset_index()
                n_jobs = len(completion_by_job)
                
                height = min(600 + max(0, n_jobs - 10) * 20, 1200)
                
                fig_comp_pie = px.pie(
                    completion_by_job, 
                    names="Job", 
                    values="Finish",
                    title=f"Время завершения для {n_jobs} деталей"
                )
                fig_comp_pie.update_layout(
                    height=height,
                    legend=dict(
                        orientation="v",
                        yanchor="top",
                        y=1.0,
                        xanchor="left",
                        x=1.02,
                        font=dict(size=10)
                    )
                )
                st.plotly_chart(fig_comp_pie, use_container_width=True)

            # === Диаграммы Ганта ===
            all_job_ids = [f"J{i}" for i in range(n_act)]
            common_color_map = _create_color_map(all_job_ids)

            st.subheader("6. Диаграммы Ганта")
            
            st.write("**До оптимизации:**")
            fig_before = create_gantt_figure(
                processing_matrix, 
                initial_seq, 
                "Исходное расписание",
                color_map=common_color_map
            )
            scrollable_plot(fig_before, max_height=500)
            
            st.write("**После оптимизации:**")
            fig_after = create_gantt_figure(
                processing_matrix, 
                optimal_seq, 
                "Оптимизированное расписание",
                color_map=common_color_map
            )
            scrollable_plot(fig_after, max_height=500)

            # === Экспорт в Excel  ===
            st.subheader("7. Экспорт данных")

            report_data = {
                "Метрика": [
                    "Длительность цикла (до)",
                    "Длительность цикла (после)",
                    "Эффект оптимизации (%)",
                    "Время расчёта (мс)",
                    "Загрузка оборудования (%)",
                    "Общие простои",
                    "Среднее время выпуска"
                ],
                "Значение": [
                    int(before['makespan']),
                    int(after['makespan']),
                    round(improvement_makespan, 2),
                    round(elapsed_ms, 1),
                    round(after['equipment_utilization'], 2),
                    int(after['total_idle_time']),
                    round(after['avg_completion_time'], 2)
                ]
            }
            df_report = pd.DataFrame(report_data)

            df_gantt_before = build_gantt_dataframe(processing_matrix, initial_seq)
            df_gantt_after = build_gantt_dataframe(processing_matrix, optimal_seq)
            completion_by_job = df_gantt_after.groupby('Job')['Finish'].max().reset_index()

            # png в отчет для круговых диаграмм
            #idle_pie_data = report["idle_by_machine"][["Machine", "IdleTime"]].copy()
            #idle_pie_data = idle_pie_data[idle_pie_data["IdleTime"] > 0]
            #if not idle_pie_data.empty:
            #    fig_idle = px.pie(idle_pie_data, names="Machine", values="IdleTime")
            #    pie_idle_png = fig_idle.to_image(format="png", width=600, height=400, scale=1)
            #else:
             #   pie_idle_png = None

            #ig_comp = px.pie(completion_by_job, names="Job", values="Finish")
            #pie_comp_png = fig_comp.to_image(format="png", width=600, height=400, scale=1)

            # Экспорт в Excel
            excel_bytes = create_excel_report(
                summary_data=df_report,
                idle_by_machine=report["idle_by_machine"],
                gantt_before=df_gantt_before,
                gantt_after=df_gantt_after,
                completion_by_job=completion_by_job,
                processing_matrix=processing_matrix,  
                pie_idle_png=None,
                pie_comp_png=None
            )

            st.download_button(
                label="📥 Скачать отчёт (Excel)",
                data=excel_bytes,
                file_name="production_schedule_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_excel_full"
            )
            
        except Exception as e:
            st.error("💥 Произошла ошибка")
            st.exception(e)