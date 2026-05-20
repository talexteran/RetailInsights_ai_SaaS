"""
data_cleaning.py
----------------
Limpieza y validación automática del dataset del cliente.
Detecta columnas por alias, estandariza tipos y elimina outliers.
"""

import pandas as pd
import numpy as np

# Mapeo de alias → nombre estándar
COLUMN_ALIASES = {
    "fecha":    ["date", "fecha", "dt", "order_date", "sale_date", "transaction_date"],
    "ventas":   ["sales", "ventas", "revenue", "amount", "total", "monto", "importe", "valor"],
    "producto": ["product", "producto", "item", "articulo", "sku", "nombre_producto", "product line", "product_line", "productline"],
    "categoria":["category", "categoria", "cat", "type", "tipo", "department", "city", "ciudad", "customer type", "customer_type"],
    "region":   ["region", "store", "tienda", "location", "zona", "sucursal", "branch", "city", "ciudad"],
    "cantidad": ["quantity", "cantidad", "qty", "units", "unidades"],
}


def detect_columns(df: pd.DataFrame) -> dict:
    """Detecta qué columna del df corresponde a cada columna estándar."""
    cols_lower = {c: c.lower().strip() for c in df.columns}
    mapping = {}
    for std_col, aliases in COLUMN_ALIASES.items():
        for orig_col, col_lower in cols_lower.items():
            if col_lower in aliases:
                mapping[std_col] = orig_col
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
            f"Columnas detectadas: {list(df.columns)}"
        )

    # Renombrar a nombres estándar
    df = df.rename(columns={v: k for k, v in mapping.items()})

    # --- Fecha ---
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    fecha_nulls = df["fecha"].isna().sum()
    if fecha_nulls:
        report["issues"].append(f"{fecha_nulls} filas con fecha inválida eliminadas")
    df = df.dropna(subset=["fecha"])

    # --- Ventas ---
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
            df[col] = df[col].replace({"Nan": "Sin datos", "None": "Sin datos", "": "Sin datos"})

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
    sample = pd.DataFrame({
        "date": ["2024-01-01", "2024-01-02", "bad_date", "2024-01-03"],
        "sales": [100, 200, 150, -10],
        "product": ["Manzana", "Pera", "Uva", "Manzana"],
        "category": ["Frutas", "Frutas", "Frutas", "Frutas"],
        "region": ["Norte", "Sur", "Norte", "Sur"],
    })
    df_clean, rpt = clean_data(sample)
    print("✅ Limpieza OK:", rpt)
    print(df_clean.head())