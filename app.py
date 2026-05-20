"""
app.py
------
RetailInsights.ai — Interfaz SaaS completa en Streamlit.
Compatible con Streamlit Cloud (sin escritura a disco).
v2 — copy de venta mejorado + manejo de errores más claro

Uso: streamlit run app.py
"""

import os
import sys
import tempfile
from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

sys.path.insert(0, str(Path(__file__).parent / "src"))

from pipeline import run_pipeline

# ── Configuración de página ────────────────────────────────────────────────────
st.set_page_config(
    page_title="RetailInsights.ai — Análisis de ventas con IA",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  [data-testid="stAppViewContainer"] { background: #0a0f1e; }
  [data-testid="stSidebar"] { background: #111827; border-right: 1px solid #1e2d45; }
  .main .block-container { padding-top: 1.5rem; max-width: 1200px; }
  .metric-card {
    background: #1a2236; border: 1px solid #1e2d45;
    border-radius: 12px; padding: 1.1rem 1.25rem;
    border-top: 3px solid #3b82f6;
  }
  .metric-label { font-size: 0.72rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.08em; }
  .metric-value { font-size: 1.6rem; font-weight: 700; color: #f1f5f9; line-height: 1.2; }
  .metric-sub   { font-size: 0.75rem; color: #64748b; margin-top: 0.25rem; }
  .insight-card {
    background: #1a2236; border: 1px solid #1e2d45;
    border-radius: 10px; padding: 1rem 1.1rem; margin-bottom: 0.75rem;
  }
  .semaforo-verde   { background: rgba(16,185,129,0.12); border: 1px solid rgba(16,185,129,0.35); border-radius: 10px; padding: 0.85rem 1.1rem; }
  .semaforo-amarillo{ background: rgba(245,158,11,0.12); border: 1px solid rgba(245,158,11,0.35); border-radius: 10px; padding: 0.85rem 1.1rem; }
  .semaforo-rojo    { background: rgba(239,68,68,0.12);  border: 1px solid rgba(239,68,68,0.35);  border-radius: 10px; padding: 0.85rem 1.1rem; }
  .price-card {
    background: rgba(59,130,246,0.1); border: 1px solid rgba(59,130,246,0.3);
    border-radius: 12px; padding: 1rem; text-align: center; margin-bottom: 0.5rem;
  }
  .stButton > button { border-radius: 8px; font-weight: 600; }
  h1, h2, h3 { color: #f1f5f9 !important; }
</style>
""", unsafe_allow_html=True)


# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📊 RetailInsights.ai")
    st.markdown("*Análisis de ventas con IA para retail*")
    st.markdown("---")

    client_name = st.text_input(
        "Nombre de tu negocio",
        value="Mi Empresa",
        placeholder="Ej: Supermercados XYZ"
    )

    # API key desde secrets o env
    try:
        default_key = st.secrets.get("ANTHROPIC_API_KEY", "")
    except Exception:
        default_key = ""
    default_key = default_key or os.environ.get("ANTHROPIC_API_KEY", "")

    api_key = st.text_input(
        "Anthropic API Key (opcional)",
        type="password",
        placeholder="sk-ant-... (deja vacío para análisis automático)",
        help="Con API key los insights son generados por IA real. Sin ella, el sistema usa análisis automático igualmente.",
        value=default_key,
    )

    st.markdown("---")
    st.markdown("**¿Qué columnas necesita el archivo?**")
    st.markdown("""
✅ **Obligatorias:**
- Columna de **fecha** (cualquier nombre)
- Columna de **ventas/total** (cualquier nombre)

⭐ **Opcionales (más análisis):**
- Producto / artículo
- Categoría / tipo
- Sucursal / región
    """)

    st.markdown("---")

    # Precios visibles en el sidebar
    st.markdown("**Planes disponibles**")
    st.markdown("""
<div class="price-card">
  <div style="font-size:0.75rem;color:#64748b">ANÁLISIS ÚNICO</div>
  <div style="font-size:1.4rem;font-weight:700;color:#f1f5f9">$120.000</div>
  <div style="font-size:0.72rem;color:#64748b">COP · 1 reporte</div>
</div>
<div class="price-card">
  <div style="font-size:0.75rem;color:#64748b">MENSUAL</div>
  <div style="font-size:1.4rem;font-weight:700;color:#3b82f6">$400.000</div>
  <div style="font-size:0.72rem;color:#64748b">COP · ilimitado 30 días</div>
</div>
    """, unsafe_allow_html=True)

    st.markdown("")
    st.markdown("📩 **¿Quieres contratar?**")
    st.markdown("WhatsApp: [Escríbenos aquí](https://wa.me/573000000000)")
    st.caption("Powered by Python · Plotly · Claude AI")


# ── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown("# 📊 RetailInsights.ai")
st.markdown("**Sube tu Excel de ventas → en 30 segundos sabes qué vendiste más, qué te está quitando dinero y qué hacer.**")
st.markdown("---")


# ── UPLOAD ─────────────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader(
    "📂 Arrastra tu archivo de ventas aquí (Excel o CSV)",
    type=["xlsx", "xls", "csv"],
    help="El sistema detecta automáticamente los nombres de columnas. Funciona con cualquier formato.",
)

if not uploaded_file:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**Paso 1**\n\nSube tu Excel o CSV de ventas. Sin formato especial requerido.")
    with col2:
        st.info("**Paso 2**\n\nEl sistema limpia, analiza y calcula KPIs automáticamente.")
    with col3:
        st.info("**Paso 3**\n\nDescarga tu reporte ejecutivo con insights de IA listos para presentar.")

    st.markdown("---")
    st.markdown("### ¿Quieres ver cómo funciona primero?")
    if st.button("▶️ Cargar datos de ejemplo (supermarket_sales.csv)"):
        demo_path = Path(__file__).parent / "data" / "raw" / "supermarket_sales.csv"
        if demo_path.exists():
            st.session_state["demo_mode"] = True
            st.session_state["demo_path"] = str(demo_path)
            st.rerun()
        else:
            st.warning("Archivo de demo no encontrado. Sube tu propio archivo.")
    st.stop()


# ── PROCESAR ───────────────────────────────────────────────────────────────────
file_key = f"{uploaded_file.name}_{uploaded_file.size}"

if "result" not in st.session_state or st.session_state.get("file_key") != file_key or st.sidebar.button("🔄 Reprocesar"):
    with st.spinner("Analizando tu archivo..."):
        suffix = Path(uploaded_file.name).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        progress_bar = st.progress(0)
        status_text = st.empty()

        def update_progress(step, msg):
            progress_bar.progress(step / 5)
            status_text.text(f"[{step}/5] {msg}")

        result = run_pipeline(
            input_source=tmp_path,
            api_key=api_key or None,
            client_name=client_name,
            progress_callback=update_progress,
        )

        try:
            Path(tmp_path).unlink()
        except Exception:
            pass

        progress_bar.empty()
        status_text.empty()
        st.session_state["result"] = result
        st.session_state["file_key"] = file_key

result = st.session_state.get("result", {})

if not result.get("success"):
    error_msg = result.get("error", "Error desconocido")
    st.error(f"❌ No pudimos procesar el archivo")
    st.markdown(f"**Detalle del error:** `{error_msg}`")
    st.markdown("""
    **Posibles causas:**
    - El archivo no tiene columna de fecha → renómbrala como `fecha` o `date`
    - El archivo no tiene columna de ventas → renómbrala como `total`, `ventas` o `sales`
    - El archivo está vacío o corrupto

    **¿Necesitas ayuda?** Escríbenos por WhatsApp y te ayudamos a preparar el archivo.
    """)
    st.stop()

kpis        = result["kpis"]
insights    = result.get("insights", {})
df          = result["df_clean"]
clean_report = result["clean_report"]
charts      = result.get("charts", {})

# ── AVISOS DE LIMPIEZA ─────────────────────────────────────────────────────────
if clean_report.get("issues"):
    with st.expander("⚠️ El sistema encontró y corrigió estos problemas en tus datos"):
        for issue in clean_report["issues"]:
            st.warning(issue)

st.success(f"✅ Análisis completado en {result['duration_sec']}s · {clean_report['clean_rows']:,} ventas procesadas")

# ── SEMÁFORO ─────────────────────────────────────────────────────────────────────
if insights:
    semaforo = insights.get("semaforo", "amarillo")
    icon = {"verde": "🟢", "amarillo": "🟡", "rojo": "🔴"}.get(semaforo, "⚪")
    st.markdown(f"""
    <div class="semaforo-{semaforo}">
      <strong>{icon} Estado del negocio: {semaforo.upper()}</strong><br>
      <span style="color:#94a3b8;font-size:0.85rem">{insights.get('semaforo_razon','')}</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("")

# ── KPI CARDS ──────────────────────────────────────────────────────────────────
st.markdown("### KPIs principales")
cols = st.columns(6)
kpi_items = [
    ("Revenue total",     f"${kpis['revenue_total']:,.0f}",           f"{kpis['n_dias']} días"),
    ("Transacciones",     f"{kpis['n_transacciones']:,}",             f"Ticket ${kpis['ticket_promedio']:,.0f}"),
    ("Promedio diario",   f"${kpis['promedio_diario']:,.0f}",         "por día"),
    ("Crecimiento MoM",   f"{kpis.get('mom_growth_pct', 0)}%",        f"Mejor: {kpis.get('mejor_mes','N/A')}"),
    ("Categoría #1",      kpis.get("categoria_top", "N/A"),           "mayor revenue"),
    ("Región #1",         kpis.get("region_top", "N/A"),              "mayor revenue"),
]
for i, (label, value, sub) in enumerate(kpi_items):
    with cols[i]:
        st.markdown(f"""
        <div class="metric-card">
          <div class="metric-label">{label}</div>
          <div class="metric-value">{value}</div>
          <div class="metric-sub">{sub}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("")

# ── CHARTS ─────────────────────────────────────────────────────────────────────
st.markdown("### Visualizaciones")
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Tendencia", "🏆 Productos", "🍕 Categorías", "🗺️ Regiones", "📅 Días"])

with tab1:
    if "tendencia_mensual" in charts:
        st.plotly_chart(charts["tendencia_mensual"], use_container_width=True)
    else:
        st.info("No hay suficientes datos para mostrar la tendencia mensual.")

with tab2:
    if "top_productos" in charts:
        st.plotly_chart(charts["top_productos"], use_container_width=True)
    else:
        st.info("Tu archivo no tiene columna de producto.")

with tab3:
    if "categorias" in charts:
        st.plotly_chart(charts["categorias"], use_container_width=True)
    else:
        st.info("Tu archivo no tiene columna de categoría.")

with tab4:
    if "regiones" in charts:
        st.plotly_chart(charts["regiones"], use_container_width=True)
    else:
        st.info("Tu archivo no tiene columna de región o sucursal.")

with tab5:
    if "dias_semana" in charts:
        st.plotly_chart(charts["dias_semana"], use_container_width=True)

# ── AI INSIGHTS ────────────────────────────────────────────────────────────────
if insights:
    st.markdown("### 🤖 Insights de negocio · IA")
    st.info(f"**Resumen ejecutivo:** {insights.get('resumen_ejecutivo','')}")

    st.markdown(f"""
    <div style="background:rgba(59,130,246,0.12);border:1px solid rgba(59,130,246,0.3);border-radius:10px;padding:1rem 1.25rem;margin-bottom:1rem">
      <div style="font-size:0.72rem;color:#3b82f6;text-transform:uppercase;letter-spacing:0.1em;font-weight:600;margin-bottom:0.4rem">⚡ Recomendación prioritaria</div>
      <div style="font-size:0.95rem;color:#f1f5f9;font-weight:500">{insights.get('recomendacion_top','')}</div>
      <div style="font-size:0.8rem;color:#64748b;margin-top:0.5rem">📅 Proyección 30 días: {insights.get('proyeccion_proximos_30_dias','')}</div>
    </div>
    """, unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    for i, ins in enumerate(insights.get("insights", [])):
        col = col_a if i % 2 == 0 else col_b
        impact_color = {"alto": "#ef4444", "medio": "#f59e0b", "bajo": "#64748b"}.get(ins.get("impacto",""), "#64748b")
        with col:
            st.markdown(f"""
            <div class="insight-card">
              <div style="display:flex;justify-content:space-between;margin-bottom:0.5rem">
                <strong style="font-size:0.9rem;color:#f1f5f9">{ins.get('titulo','')}</strong>
                <span style="font-size:0.65rem;color:{impact_color};font-weight:700;text-transform:uppercase;border:1px solid {impact_color};border-radius:20px;padding:1px 8px">{ins.get('impacto','').upper()}</span>
              </div>
              <p style="font-size:0.82rem;color:#94a3b8;margin-bottom:0.6rem">{ins.get('descripcion','')}</p>
              <p style="font-size:0.82rem;color:#06b6d4;border-left:2px solid #06b6d4;padding-left:0.6rem">▶ {ins.get('accion','')}</p>
            </div>
            """, unsafe_allow_html=True)

    if insights.get("alertas"):
        st.markdown("**Alertas detectadas**")
        for alerta in insights["alertas"]:
            tipo = alerta.get("tipo", "tendencia")
            icon = {"oportunidad": "✅", "riesgo": "⚠️", "tendencia": "📈"}.get(tipo, "ℹ️")
            color = {"oportunidad": "success", "riesgo": "error", "tendencia": "info"}.get(tipo, "info")
            getattr(st, color)(f"{icon} **{tipo.capitalize()}:** {alerta.get('mensaje','')}")

# ── EXPORTAR ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Exportar reporte")
st.markdown("Descarga el reporte completo para presentarle a tu equipo o a tu cliente.")

col_dl1, col_dl2, _ = st.columns([2, 2, 4])

report_html = result.get("report_html")
if report_html:
    with col_dl1:
        st.download_button(
            label="⬇️ Reporte HTML",
            data=report_html.encode("utf-8"),
            file_name=f"reporte_{client_name.replace(' ','_')}.html",
            mime="text/html",
            use_container_width=True,
        )

    kpis_scalar = {k: v for k, v in kpis.items() if not isinstance(v, list)}
    kpis_csv = pd.DataFrame([kpis_scalar]).to_csv(index=False).encode("utf-8")
    with col_dl2:
        st.download_button(
            label="⬇️ KPIs CSV",
            data=kpis_csv,
            file_name=f"kpis_{client_name.replace(' ','_')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

# ── CTA FINAL ──────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.3);border-radius:12px;padding:1.25rem;text-align:center">
  <div style="font-size:1rem;font-weight:600;color:#f1f5f9;margin-bottom:0.5rem">¿Quieres este análisis cada mes para tu negocio?</div>
  <div style="font-size:0.85rem;color:#94a3b8">Plan mensual desde $400.000 COP · Escríbenos por WhatsApp</div>
</div>
""", unsafe_allow_html=True)

# ── DATA EXPLORER ──────────────────────────────────────────────────────────────
with st.expander("🔍 Ver datos procesados"):
    st.dataframe(df.head(100), use_container_width=True)
    st.caption(f"{len(df):,} filas totales · mostrando primeras 100")
