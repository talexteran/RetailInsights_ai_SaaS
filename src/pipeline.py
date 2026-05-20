"""
pipeline.py
-----------
Pipeline completo para RetailInsights.ai.
Compatible con Streamlit Cloud: usa memoria y carpetas temporales, no rutas relativas.

Uso CLI:  python src/pipeline.py --input data/raw/ventas.xlsx
Uso API:  from src.pipeline import run_pipeline
          result = run_pipeline(df_or_path, api_key="sk-ant-...")
"""

import argparse
import sys
import time
import tempfile
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))

from data_cleaning import clean_data
from generate_kpis import generate_kpis
from generate_charts import generate_all_charts
from export_report import export_report
from ai_insights import generate_insights


def run_pipeline(
    input_source,           # str path | Path | pd.DataFrame
    api_key: str = None,
    client_name: str = "Cliente",
    progress_callback=None,
) -> dict:
    """
    Ejecuta el pipeline completo de analytics.

    Retorna dict con:
        {
            "success": bool,
            "df_clean": pd.DataFrame,
            "kpis": dict,
            "insights": dict,
            "charts": dict,
            "report_html": str,   # HTML como string (para descarga directa)
            "clean_report": dict,
            "duration_sec": float,
            "error": str | None
        }
    """
    t0 = time.time()
    result = {"success": False, "error": None}

    def _progress(step, msg):
        if progress_callback:
            progress_callback(step, msg)
        else:
            print(f"  [{step}/5] {msg}")

    try:
        # ── 1. Cargar ──────────────────────────────────────────────
        _progress(1, "Cargando datos...")

        if isinstance(input_source, pd.DataFrame):
            df_raw = input_source.copy()
        else:
            path = Path(input_source)
            if not path.exists():
                raise FileNotFoundError(f"Archivo no encontrado: {path}")
            if path.suffix.lower() in [".xlsx", ".xls"]:
                df_raw = pd.read_excel(path)
            elif path.suffix.lower() == ".csv":
                df_raw = pd.read_csv(path)
            else:
                raise ValueError(f"Formato no soportado: {path.suffix}. Usa CSV o Excel.")

        # ── 2. Limpiar ─────────────────────────────────────────────
        _progress(2, f"Limpiando {len(df_raw):,} filas...")
        df_clean, clean_report = clean_data(df_raw)

        # ── 3. KPIs ────────────────────────────────────────────────
        _progress(3, "Calculando KPIs...")
        kpis = generate_kpis(df_clean)

        # ── 4. Charts (en memoria, sin escribir a disco) ───────────
        _progress(4, "Generando visualizaciones...")
        charts = generate_all_charts(kpis)

        # ── 5. IA Insights ─────────────────────────────────────────
        _progress(5, "Generando insights con IA...")
        insights = generate_insights(kpis, api_key=api_key)

        # ── 6. Reporte HTML (string en memoria) ────────────────────
        report_html = export_report(
            kpis=kpis,
            insights=insights,
            charts=charts,
            client_name=client_name,
        )

        result.update({
            "success": True,
            "df_clean": df_clean,
            "kpis": kpis,
            "insights": insights,
            "charts": charts,
            "report_html": report_html,
            "clean_report": clean_report,
            "duration_sec": round(time.time() - t0, 1),
        })

    except Exception as e:
        result["error"] = str(e)
        result["duration_sec"] = round(time.time() - t0, 1)

    return result


# ── CLI ────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RetailInsights.ai Pipeline")
    parser.add_argument("--input", required=True, help="Ruta del archivo CSV o Excel")
    parser.add_argument("--api-key", default=None, help="Anthropic API key (opcional)")
    parser.add_argument("--client", default="Cliente", help="Nombre del cliente")
    args = parser.parse_args()

    print("\n" + "="*50)
    print("  RetailInsights.ai — Pipeline Automatizado")
    print("="*50)

    r = run_pipeline(args.input, api_key=args.api_key, client_name=args.client)

    if r["success"]:
        print(f"\n✅ Pipeline completado en {r['duration_sec']}s")
        print(f"   Revenue:      ${r['kpis']['revenue_total']:,.0f}")
        print(f"   Ticket prom:  ${r['kpis']['ticket_promedio']:,.2f}")
        print(f"   MoM growth:   {r['kpis'].get('mom_growth_pct', 0)}%")
        print(f"   Semáforo IA:  {r['insights'].get('semaforo', 'N/A').upper()}")
        print("="*50 + "\n")
    else:
        print(f"\n❌ Error: {r['error']}")
        sys.exit(1)
