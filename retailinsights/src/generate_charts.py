"""
generate_charts.py
------------------
Genera y guarda visualizaciones HTML interactivos con Plotly.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

OUTPUT_DIR = Path("reports")


def _save_html(fig, name: str) -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)
    path = OUTPUT_DIR / f"{name}.html"
    fig.write_html(str(path), full_html=False, include_plotlyjs="cdn")
    return path


def chart_monthly_trend(kpis: dict) -> Path:
    data = pd.DataFrame(kpis["ventas_mensuales"])
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data["mes_label"], y=data["ventas"],
        mode="lines+markers",
        line=dict(color="#e94560", width=3),
        marker=dict(size=8, color="#f5a623"),
        fill="tozeroy", fillcolor="rgba(233,69,96,0.15)"
    ))
    fig.update_layout(
        title="📈 Tendencia Mensual de Ventas",
        template="plotly_dark",
        xaxis_title="Mes", yaxis_title="Ventas ($)",
        height=380
    )
    return _save_html(fig, "chart_monthly_trend")


def chart_top_products(kpis: dict) -> Path:
    if "top_productos" not in kpis:
        return None
    data = pd.DataFrame(kpis["top_productos"]).head(10)
    fig = px.bar(
        data, x="ventas", y="producto", orientation="h",
        color="ventas", color_continuous_scale=["#0f3460", "#e94560"],
        text=data["ventas"].apply(lambda x: f"${x:,.0f}")
    )
    fig.update_layout(
        title="🏆 Top 10 Productos por Ventas",
        template="plotly_dark", height=400,
        yaxis=dict(autorange="reversed"),
        coloraxis_showscale=False
    )
    return _save_html(fig, "chart_top_products")


def chart_category_pie(kpis: dict) -> Path:
    if "ventas_categoria" not in kpis:
        return None
    data = pd.DataFrame(kpis["ventas_categoria"])
    fig = px.pie(
        data, values="ventas", names="categoria",
        hole=0.45,
        color_discrete_sequence=["#e94560","#0f3460","#f5a623","#50fa7b","#16213e"]
    )
    fig.update_layout(
        title="🍩 Ventas por Categoría",
        template="plotly_dark", height=380
    )
    return _save_html(fig, "chart_category_pie")


def chart_region_bars(kpis: dict) -> Path:
    if "ventas_region" not in kpis:
        return None
    data = pd.DataFrame(kpis["ventas_region"])
    fig = px.bar(
        data, x="region", y="ventas",
        color="ventas", color_continuous_scale=["#0f3460","#e94560"],
        text=data["ventas"].apply(lambda x: f"${x:,.0f}")
    )
    fig.update_layout(
        title="📍 Ventas por Región",
        template="plotly_dark", height=380,
        coloraxis_showscale=False
    )
    return _save_html(fig, "chart_region_bars")


def chart_weekday(kpis: dict) -> Path:
    if "ventas_por_dia" not in kpis:
        return None
    data = pd.DataFrame(kpis["ventas_por_dia"])
    fig = px.bar(
        data, x="dia", y="ventas",
        color="ventas", color_continuous_scale=["#16213e","#f5a623"],
        text=data["ventas"].apply(lambda x: f"${x:,.0f}")
    )
    fig.update_layout(
        title="📅 Ventas por Día de Semana",
        template="plotly_dark", height=360,
        coloraxis_showscale=False
    )
    return _save_html(fig, "chart_weekday")


def generate_all_charts(kpis_summary: dict) -> dict:
    """Genera todos los charts y retorna dict {nombre: path}."""
    charts = {}
    fns = [chart_monthly_trend, chart_top_products,
           chart_category_pie, chart_region_bars, chart_weekday]
    for fn in fns:
        path = fn(kpis_summary)
        if path:
            charts[fn.__name__] = str(path)
    return charts
