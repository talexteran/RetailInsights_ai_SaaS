"""
data_cleaning.py
----------------
Limpieza y validación automática del dataset del cliente.
Detecta columnas por alias, estandariza tipos y elimina outliers.
v2 — aliases colombianos agregados + fix ciudad duplicada
"""

import pandas as pd
import numpy as np

# Mapeo de alias → nombre estándar
# FIX: ciudad/city solo en categoria, no en region (evita confusión)
# NUEVO: aliases colombianos reales agregados
COLUMN_ALIASES = {
    "fecha":    [
        "date", "fecha", "dt", "order_date", "sale_date",
        "transaction_date", "fecha_venta", "fecha_pedido",
        "fecha_factura", "dia", "f_venta",
    ],
    "ventas":   [
        "sales", "ventas", "revenue", "amount", "total", "monto",
        "importe", "valor", "total_venta", "valor_venta", "venta",
        "ingreso", "importe_total", "precio_total", "total_ventas",
        "valor_total", "factura_total", "subtotal",
    ],
    "producto": [
        "product", "producto", "item", "articulo", "sku",
        "nombre_producto", "product line", "product_line",
        "productline", "descripcion", "nombre", "referencia",
        "producto_nombre", "art", "bien",
    ],
    "categoria": [
        "category", "categoria", "cat", "type", "tipo",
        "department", "city", "ciudad", "customer type",
        "customer_type", "linea", "grupo", "familia",
        "segmento", "clasificacion",
    ],
    "region": [
        "region", "store", "tienda", "location", "zona",
        "sucursal", "branch", "sede", "local", "punto_venta",
        "punto de venta", "canal", "municipio", "departamento",
        "bodega", "almacen", "establecimiento",
    ],
    "cantidad": [
        "quantity", "cantidad", "qty", "units", "unidades",
        "cant", "unid", "piezas",
    ],
}


def detect_columns(df: pd.DataFrame) -> dict:
    """
    Detecta qué columna del df corresponde a cada columna estándar.
    Prioriza columnas exactas antes de alias para evitar ambigüedades.
    """
    cols_lower = {c: c.lower().strip().replace(" ", "_") for c in df.columns}
    mapping = {}
    used_orig_cols = set()

    for std_col, aliases in COLUMN_ALIASES.items():
        for orig_col, col_lower in cols_lower.items():
            # Evitar mapear la misma columna original a dos estándar
            if orig_col in used_orig_cols:
                continue
            if col_lower in aliases:
                mapping[std_col] = orig_col
                used_orig_cols.add(orig_col)
                break

    return mapping


def validate_columns(mapping: dict) -> list:
    """Retorna lista de columnas requeridas que faltan."""
    required = ["fecha", "ventas"]
    return [col for col in required if col not in mapping]


def clean_data(df: pd.DataFrame):
    """
    Pipeline completo de limpieza.
    Retorna (df_limpio, reporte_de_calidad).
    """
    report = {"original_rows": len(df), "issues": []}
    mapping = detect_columns(df)

    missing = validate_columns(mapping)
    if missing:
        raise ValueError(
            f"Columnas requeridas no encontradas: {missing}. "
            f"Columnas en tu archivo: {list(df.columns)}. "
            f"Asegúrate de tener una columna de fecha y una de ventas/total."
        )

    # Renombrar a nombres estándar
    df = df.rename(columns={v: k for k, v in mapping.items()})

    # --- Fecha ---
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce", dayfirst=True)
    fecha_nulls = df["fecha"].isna().sum()
    if fecha_nulls:
        report["issues"].append(f"{fecha_nulls} filas con fecha inválida eliminadas")
    df = df.dropna(subset=["fecha"])

    # --- Ventas ---
    # Limpiar símbolos de moneda y separadores antes de convertir
    if df["ventas"].dtype == object:
        df["ventas"] = (
            df["ventas"]
            .astype(str)
            .str.replace(r"[$,\s]", "", regex=True)
            .str.replace(",", ".", regex=False)
        )
    df["ventas"] = pd.to_numeric(df["ventas"], errors="coerce")
    ventas_nulls = df["ventas"].isna().sum()
    if ventas_nulls:
        report["issues"].append(f"{ventas_nulls} filas con ventas inválidas eliminadas")
    df = df.dropna(subset=["ventas"])
    df = df[df["ventas"] > 0]

    # --- Outliers en ventas (IQR) ---
    Q1, Q3 = df["ventas"].quantile([0.25, 0.75])
    IQR = Q3 - Q1
    outlier_mask = (df["ventas"] < Q1 - 3 * IQR) | (df["ventas"] > Q3 + 3 * IQR)
    n_outliers = outlier_mask.sum()
    if n_outliers:
        report["issues"].append(f"{n_outliers} outliers extremos marcados (col: ventas_outlier)")
    df["ventas_outlier"] = outlier_mask

    # --- Columnas opcionales ---
    for col in ["producto", "categoria", "region"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.title()
            df[col] = df[col].replace(
                {"Nan": "Sin datos", "None": "Sin datos", "": "Sin datos", "Nat": "Sin datos"}
            )

    # --- Columnas derivadas ---
    df["año"] = df["fecha"].dt.year
    df["mes"] = df["fecha"].dt.month
    df["mes_nombre"] = df["fecha"].dt.strftime("%b %Y")
    df["dia_semana"] = df["fecha"].dt.day_name()
    df["semana"] = df["fecha"].dt.isocalendar().week.astype(int)

    report["clean_rows"] = len(df)
    report["columns_detected"] = mapping
    return df.sort_values("fecha").reset_index(drop=True), report


if __name__ == "__main__":
    # Test con columnas colombianas reales
    sample = pd.DataFrame({
        "fecha_venta": ["2024-01-01", "2024-01-02", "bad_date", "2024-01-03"],
        "total_venta": ["$100,000", "200000", "150000", "-10000"],
        "producto": ["Arroz 5kg", "Aceite 1L", "Leche", "Arroz 5kg"],
        "categoria": ["Abarrotes", "Abarrotes", "Lácteos", "Abarrotes"],
        "sucursal": ["Barranquilla", "Soledad", "Barranquilla", "Malambo"],
    })
    df_clean, rpt = clean_data(sample)
    print("✅ Limpieza OK:", rpt)
    print(df_clean[["fecha", "ventas", "producto", "categoria", "region"]].head())
