"""
app.py
------
RetailInsights.ai — Interfaz SaaS completa en Streamlit.

Uso: streamlit run app.py
"""

import os
import sys
import io
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
    page_title="RetailInsights.ai",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS personalizado ──────────────────────────────────────────────────────────
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
  .stButton > button { border-radius: 8px; font-weight: 600; }
  h1, h2, h3 { color: #f1f5f9 !important; }
</style>
""", unsafe_allow_html=True)


# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📊 RetailInsights.ai")
    st.markdown("---")

    client_name = st.text_input("Nombre del cliente", value="Mi Empresa", placeholder="Ej: Supermercados XYZ")

    api_key = st.text_input(
        "Anthropic API Key",
        type="password",
        placeholder="sk-ant-...",
        help="Opcional. Sin API key se generan insights con reglas automáticas.",
        value=os.environ.get("ANTHROPIC_API_KEY", ""),
    )

    st.markdown("---")
    st.markdown("**Columnas esperadas**")
    st.markdown("""
- `fecha` / `date` → fecha de venta
- `ventas` / `sales` → monto
- `producto` / `product` → nombre
- `categoria` / `category` → tipo
- `region` / `branch` → sucursal
    """)
    st.markdown("---")
    st.caption("Powered by Python · Plotly · Claude AI")


# ── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown("# 📊 RetailInsights.ai")
st.markdown("Sube tu archivo de ventas → obtén KPIs, visualizaciones e insights de IA en segundos.")
st.markdown("---")


# ── UPLOAD ─────────────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader(
    "Sube tu archivo de ventas (Excel o CSV)",
    type=["xlsx", "xls", "csv"],
    help="El sistema detecta automáticamente los nombres de columnas.",
)

if not uploaded_file:
    # Pantalla de bienvenida
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**Paso 1**\nSube tu Excel o CSV de ventas")
    with col2:
        st.info("**Paso 2**\nEl pipeline limpia y calcula KPIs automáticamente")
    with col3:
        st.info("**Paso 3**\nDescarga el reporte ejecutivo con insights de IA")
    st.stop()


# ── PROCESAR ───────────────────────────────────────────────────────────────────
if "result" not in st.session_state or st.sidebar.button("🔄 Reprocesar"):
    with st.spinner("Procesando tu archivo..."):
        # Guardar a temp file para mantener compatibilidad con pipeline
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

        progress_bar.empty()
        status_text.empty()
        st.session_state["result"] = result

result = st.session_state.get("result", {})

if not result.get("success"):
    st.error(f"❌ Error al procesar el archivo: {result.get('error', 'Error desconocido')}")
    st.stop()

kpis = result["kpis"]
insights = result.get("insights", {})
df = result["df_clean"]
clean_report = result["clean_report"]

# ── NOTIFICACIÓN DE LIMPIEZA ───────────────────────────────────────────────────
if clean_report.get("issues"):
    with st.expander("⚠️ Avisos de limpieza de datos"):
        for issue in clean_report["issues"]:
            st.warning(issue)

st.success(f"✅ Análisis completado en {result['duration_sec']}s · {clean_report['clean_rows']:,} filas procesadas")

# ── SEMÁFORO IA ────────────────────────────────────────────────────────────────
if insights:
    semaforo = insights.get("semaforo", "amarillo")
    css_class = f"semaforo-{semaforo}"
    icon = {"verde": "🟢", "amarillo": "🟡", "rojo": "🔴"}.get(semaforo, "⚪")
    st.markdown(f"""
    <div class="{css_class}">
      <strong>{icon} Estado del negocio: {semaforo.upper()}</strong><br>
      <span style="color:#94a3b8;font-size:0.85rem">{insights.get('semaforo_razon','')}</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("")

# ── KPI CARDS ──────────────────────────────────────────────────────────────────
st.markdown("### KPIs principales")
cols = st.columns(6)
kpi_items = [
    ("Revenue total", f"${kpis['revenue_total']:,.0f}", f"{kpis['n_dias']} días"),
    ("Transacciones", f"{kpis['n_transacciones']:,}", f"Ticket ${kpis['ticket_promedio']:,.2f}"),
    ("Prom. diario", f"${kpis['promedio_diario']:,.0f}", "por día"),
    ("Crecimiento MoM", f"{kpis.get('mom_growth_pct',0)}%", f"Mejor: {kpis.get('mejor_mes','N/A')}"),
    ("Categoría #1", kpis.get("categoria_top", "N/A"), "mayor revenue"),
    ("Región #1", kpis.get("region_top", "N/A"), "mayor revenue"),
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
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Tendencia", "Productos", "Categorías", "Regiones", "Días"])

with tab1:
    if kpis.get("ventas_mensuales"):
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
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    if kpis.get("top_productos"):
        data = pd.DataFrame(kpis["top_productos"]).head(10)
        fig = px.bar(data, x="ventas", y="producto", orientation="h",
                     color="ventas", color_continuous_scale=["#1e3a5f","#3b82f6"],
                     text=data["ventas"].apply(lambda x: f"${x:,.0f}"))
        fig.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)", height=400,
            yaxis=dict(autorange="reversed"), coloraxis_showscale=False,
            margin=dict(l=0, r=0, t=10, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    if kpis.get("ventas_categoria"):
        data = pd.DataFrame(kpis["ventas_categoria"])
        fig = px.pie(data, values="ventas", names="categoria", hole=0.45,
                     color_discrete_sequence=["#3b82f6","#06b6d4","#8b5cf6","#10b981","#f59e0b","#ef4444"])
        fig.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
            height=380, margin=dict(l=0, r=0, t=10, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)

with tab4:
    if kpis.get("ventas_region"):
        data = pd.DataFrame(kpis["ventas_region"])
        fig = px.bar(data, x="region", y="ventas",
                     color="ventas", color_continuous_scale=["#1e3a5f","#06b6d4"],
                     text=data["ventas"].apply(lambda x: f"${x:,.0f}"))
        fig.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)", height=380,
            coloraxis_showscale=False, margin=dict(l=0, r=0, t=10, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)

with tab5:
    if kpis.get("ventas_por_dia"):
        data = pd.DataFrame(kpis["ventas_por_dia"])
        fig = px.bar(data, x="dia", y="ventas",
                     color="ventas", color_continuous_scale=["#1e3a5f","#8b5cf6"],
                     text=data["ventas"].apply(lambda x: f"${x:,.0f}"))
        fig.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)", height=360,
            coloraxis_showscale=False, margin=dict(l=0, r=0, t=10, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)


# ── AI INSIGHTS ────────────────────────────────────────────────────────────────
if insights:
    st.markdown("### Insights de negocio · IA")

    # Resumen ejecutivo
    st.info(f"**Resumen ejecutivo:** {insights.get('resumen_ejecutivo','')}")

    # Recomendación top
    st.markdown(f"""
    <div style="background:rgba(59,130,246,0.12);border:1px solid rgba(59,130,246,0.3);border-radius:10px;padding:1rem 1.25rem;margin-bottom:1rem">
      <div style="font-size:0.72rem;color:#3b82f6;text-transform:uppercase;letter-spacing:0.1em;font-weight:600;margin-bottom:0.4rem">Recomendación prioritaria</div>
      <div style="font-size:0.95rem;color:#f1f5f9;font-weight:500">{insights.get('recomendacion_top','')}</div>
      <div style="font-size:0.8rem;color:#64748b;margin-top:0.5rem">Proyección 30 días: {insights.get('proyeccion_proximos_30_dias','')}</div>
    </div>
    """, unsafe_allow_html=True)

    # Grid de insights
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
              <p style="font-size:0.82rem;color:#06b6d4;border-left:2px solid #06b6d4;padding-left:0.6rem">{ins.get('accion','')}</p>
            </div>
            """, unsafe_allow_html=True)

    # Alertas
    if insights.get("alertas"):
        st.markdown("**Alertas**")
        for alerta in insights["alertas"]:
            tipo = alerta.get("tipo", "tendencia")
            icon = {"oportunidad": "✅", "riesgo": "⚠️", "tendencia": "📈"}.get(tipo, "ℹ️")
            color = {"oportunidad": "success", "riesgo": "error", "tendencia": "info"}.get(tipo, "info")
            getattr(st, color)(f"{icon} **{tipo.capitalize()}:** {alerta.get('mensaje','')}")


# ── EXPORTAR ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Exportar reporte")

col_dl1, col_dl2, col_dl3 = st.columns([2, 2, 4])

report_path = result.get("report_path")
if report_path and Path(report_path).exists():
    with open(report_path, "r", encoding="utf-8") as f:
        html_bytes = f.read().encode("utf-8")

    with col_dl1:
        st.download_button(
            label="⬇️ Descargar HTML",
            data=html_bytes,
            file_name=f"retail_report_{client_name.replace(' ','_')}.html",
            mime="text/html",
            use_container_width=True,
        )

    # CSV de KPIs
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

# ── DATA EXPLORER ──────────────────────────────────────────────────────────────
with st.expander("🔍 Explorar datos limpios"):
    st.dataframe(df.head(100), use_container_width=True)
    st.caption(f"{len(df):,} filas totales · mostrando primeras 100")
