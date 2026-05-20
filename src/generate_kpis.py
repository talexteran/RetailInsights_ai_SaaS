"""
generate_kpis.py
----------------
Calcula automáticamente los KPIs de negocio sobre el df limpio.
Retorna un diccionario estructurado listo para reporte y dashboard.
"""

import pandas as pd
import numpy as np


def generate_kpis(df: pd.DataFrame) -> dict:
    """
    Genera KPIs completos a partir del df limpio.
    El df debe tener columnas: fecha, ventas (producto, categoria, region opcionales).
    """
    kpis = {}

    # ── KPIs globales ──────────────────────────────────────────────
    kpis["revenue_total"] = round(float(df["ventas"].sum()), 2)
    kpis["n_transacciones"] = int(len(df))
    kpis["ticket_promedio"] = round(float(df["ventas"].mean()), 2)
    kpis["venta_maxima"] = round(float(df["ventas"].max()), 2)
    kpis["venta_minima"] = round(float(df[df["ventas"] > 0]["ventas"].min()), 2)
    kpis["mediana_venta"] = round(float(df["ventas"].median()), 2)

    # ── Rango de fechas ────────────────────────────────────────────
    kpis["fecha_inicio"] = df["fecha"].min().strftime("%Y-%m-%d")
    kpis["fecha_fin"] = df["fecha"].max().strftime("%Y-%m-%d")
    kpis["n_dias"] = int((df["fecha"].max() - df["fecha"].min()).days + 1)
    kpis["promedio_diario"] = round(kpis["revenue_total"] / kpis["n_dias"], 2)

    # ── Tendencia mensual ──────────────────────────────────────────
    monthly = (
        df.groupby(["año", "mes"])["ventas"]
        .sum()
        .reset_index()
        .sort_values(["año", "mes"])
    )
    monthly["mes_label"] = (
        monthly["año"].astype(str) + "-" + monthly["mes"].astype(str).str.zfill(2)
    )
    kpis["ventas_mensuales"] = monthly[["mes_label", "ventas"]].to_dict("records")

    if len(monthly) >= 2:
        last = float(monthly["ventas"].iloc[-1])
        prev = float(monthly["ventas"].iloc[-2])
        kpis["mom_growth_pct"] = round(((last - prev) / prev) * 100, 1) if prev else 0
        kpis["mejor_mes"] = monthly.loc[monthly["ventas"].idxmax(), "mes_label"]
        kpis["peor_mes"] = monthly.loc[monthly["ventas"].idxmin(), "mes_label"]
    else:
        kpis["mom_growth_pct"] = 0
        kpis["mejor_mes"] = kpis["peor_mes"] = "N/A"

    # ── Por producto ───────────────────────────────────────────────
    if "producto" in df.columns:
        prod = (
            df.groupby("producto")["ventas"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )
        prod["participacion_pct"] = round(prod["ventas"] / prod["ventas"].sum() * 100, 1)
        kpis["top_productos"] = prod.head(10).to_dict("records")
        kpis["n_productos"] = int(df["producto"].nunique())

    # ── Por categoría ──────────────────────────────────────────────
    if "categoria" in df.columns:
        cat = (
            df.groupby("categoria")["ventas"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )
        cat["participacion_pct"] = round(cat["ventas"] / cat["ventas"].sum() * 100, 1)
        kpis["ventas_categoria"] = cat.to_dict("records")
        kpis["categoria_top"] = cat.iloc[0]["categoria"]

    # ── Por región ─────────────────────────────────────────────────
    if "region" in df.columns:
        reg = (
            df.groupby("region")["ventas"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )
        reg["participacion_pct"] = round(reg["ventas"] / reg["ventas"].sum() * 100, 1)
        kpis["ventas_region"] = reg.to_dict("records")
        kpis["region_top"] = reg.iloc[0]["region"]

    # ── Día de semana ──────────────────────────────────────────────
    if "dia_semana" in df.columns:
        day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        dow = df.groupby("dia_semana")["ventas"].sum().reindex(day_order).dropna().reset_index()
        dow.columns = ["dia", "ventas"]
        kpis["ventas_por_dia"] = dow.to_dict("records")
        kpis["mejor_dia"] = dow.loc[dow["ventas"].idxmax(), "dia"]

    return kpis
