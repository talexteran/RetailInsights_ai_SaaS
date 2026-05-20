"""
generate_charts.py
------------------
Genera visualizaciones con Plotly.
Retorna objetos Figure en memoria (sin escribir a disco).
Compatible con Streamlit Cloud.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def chart_monthly_trend(kpis: dict):
    if not kpis.get("ventas_mensuales"):
        return None
    data = pd.DataFrame(kpis["ventas_mensuales"])
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data["mes_label"], y=data["ventas"],
        mode="lines+markers",
        line=dict(color="#3b82f6", width=3),
        marker=dict(size=8, color="#06b6d4"),
        fill="tozeroy", fillcolor="rgba(59,130,246,0.1)"
    ))
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", height=380,
        xaxis_title="Mes", yaxis_title="Ventas ($)",
        margin=dict(l=0, r=0, t=10, b=0)
    )
    return fig


def chart_top_products(kpis: dict):
    if not kpis.get("top_productos"):
        return None
    data = pd.DataFrame(kpis["top_productos"]).head(10)
    fig = px.bar(
        data, x="ventas", y="producto", orientation="h",
        color="ventas", color_continuous_scale=["#1e3a5f", "#3b82f6"],
        text=data["ventas"].apply(lambda x: f"${x:,.0f}")
    )
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", height=400,
        yaxis=dict(autorange="reversed"), coloraxis_showscale=False,
        margin=dict(l=0, r=0, t=10, b=0)
    )
    return fig


def chart_category_pie(kpis: dict):
    if not kpis.get("ventas_categoria"):
        return None
    data = pd.DataFrame(kpis["ventas_categoria"])
    fig = px.pie(
        data, values="ventas", names="categoria", hole=0.45,
        color_discrete_sequence=["#3b82f6", "#06b6d4", "#8b5cf6", "#10b981", "#f59e0b", "#ef4444"]
    )
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        height=380, margin=dict(l=0, r=0, t=10, b=0)
    )
    return fig


def chart_region_bars(kpis: dict):
    if not kpis.get("ventas_region"):
        return None
    data = pd.DataFrame(kpis["ventas_region"])
    fig = px.bar(
        data, x="region", y="ventas",
        color="ventas", color_continuous_scale=["#1e3a5f", "#06b6d4"],
        text=data["ventas"].apply(lambda x: f"${x:,.0f}")
    )
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", height=380,
        coloraxis_showscale=False, margin=dict(l=0, r=0, t=10, b=0)
    )
    return fig


def chart_weekday(kpis: dict):
    if not kpis.get("ventas_por_dia"):
        return None
    data = pd.DataFrame(kpis["ventas_por_dia"])
    fig = px.bar(
        data, x="dia", y="ventas",
        color="ventas", color_continuous_scale=["#1e3a5f", "#8b5cf6"],
        text=data["ventas"].apply(lambda x: f"${x:,.0f}")
    )
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", height=360,
        coloraxis_showscale=False, margin=dict(l=0, r=0, t=10, b=0)
    )
    return fig


def generate_all_charts(kpis: dict) -> dict:
    """Genera todos los charts y retorna dict {nombre: figura Plotly}."""
    fns = {
        "tendencia_mensual": chart_monthly_trend,
        "top_productos": chart_top_products,
        "categorias": chart_category_pie,
        "regiones": chart_region_bars,
        "dias_semana": chart_weekday,
    }
    charts = {}
    for name, fn in fns.items():
        fig = fn(kpis)
        if fig is not None:
            charts[name] = fig
    return charts
