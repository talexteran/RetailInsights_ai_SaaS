"""
export_report.py
----------------
Genera el reporte HTML ejecutivo con KPIs, charts e insights de IA.
Soporta exportación a PDF vía WeasyPrint (opcional).
"""

from pathlib import Path
from jinja2 import Template

TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>RetailInsights.ai — {{ client_name }}</title>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono&display=swap');
  :root {
    --bg: #0a0f1e; --surface: #111827; --card: #1a2236;
    --border: #1e2d45; --accent: #3b82f6; --accent2: #06b6d4;
    --success: #10b981; --warning: #f59e0b; --danger: #ef4444;
    --text: #f1f5f9; --muted: #64748b; --subtle: #334155;
  }
  * { margin:0; padding:0; box-sizing:border-box; }
  body { background:var(--bg); color:var(--text); font-family:'DM Sans',sans-serif; line-height:1.6; }
  .wrapper { max-width:1200px; margin:0 auto; padding:2rem 1.5rem; }

  /* HEADER */
  .header { border-bottom:1px solid var(--border); padding-bottom:1.5rem; margin-bottom:2rem; display:flex; justify-content:space-between; align-items:flex-end; flex-wrap:wrap; gap:1rem; }
  .brand { display:flex; align-items:center; gap:0.75rem; }
  .brand-icon { width:40px; height:40px; background:var(--accent); border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:1.2rem; }
  .brand-name { font-size:1.4rem; font-weight:700; color:var(--text); }
  .brand-sub { font-size:0.8rem; color:var(--muted); }
  .meta { text-align:right; font-size:0.8rem; color:var(--muted); }
  .meta strong { color:var(--text); }

  /* SEMAFORO */
  .semaforo-bar { border-radius:12px; padding:1rem 1.5rem; margin-bottom:2rem; display:flex; align-items:center; gap:1rem; }
  .semaforo-bar.verde  { background:rgba(16,185,129,0.12); border:1px solid rgba(16,185,129,0.3); }
  .semaforo-bar.amarillo { background:rgba(245,158,11,0.12); border:1px solid rgba(245,158,11,0.3); }
  .semaforo-bar.rojo   { background:rgba(239,68,68,0.12); border:1px solid rgba(239,68,68,0.3); }
  .dot { width:14px; height:14px; border-radius:50%; flex-shrink:0; }
  .verde  .dot { background:var(--success); box-shadow:0 0 8px var(--success); }
  .amarillo .dot { background:var(--warning); box-shadow:0 0 8px var(--warning); }
  .rojo   .dot { background:var(--danger); box-shadow:0 0 8px var(--danger); }
  .semaforo-text strong { font-size:0.9rem; }
  .semaforo-text p { font-size:0.8rem; color:var(--muted); margin-top:0.15rem; }

  /* KPI GRID */
  .kpi-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:1rem; margin-bottom:2rem; }
  .kpi-card { background:var(--card); border:1px solid var(--border); border-radius:12px; padding:1.25rem; position:relative; overflow:hidden; }
  .kpi-card::before { content:''; position:absolute; top:0; left:0; right:0; height:3px; background:linear-gradient(90deg,var(--accent),var(--accent2)); }
  .kpi-label { font-size:0.72rem; color:var(--muted); text-transform:uppercase; letter-spacing:0.08em; margin-bottom:0.5rem; }
  .kpi-value { font-size:1.7rem; font-weight:700; color:var(--text); line-height:1; }
  .kpi-sub { font-size:0.75rem; color:var(--muted); margin-top:0.4rem; }
  .kpi-badge { display:inline-block; font-size:0.72rem; padding:2px 8px; border-radius:20px; margin-top:0.4rem; font-weight:600; }
  .badge-pos { background:rgba(16,185,129,0.15); color:var(--success); }
  .badge-neg { background:rgba(239,68,68,0.15); color:var(--danger); }

  /* SECTION */
  .section-title { font-size:1rem; font-weight:600; color:var(--muted); text-transform:uppercase; letter-spacing:0.1em; margin:2rem 0 1rem; padding-bottom:0.5rem; border-bottom:1px solid var(--border); }

  /* CHARTS */
  .chart-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(480px,1fr)); gap:1.25rem; margin-bottom:2rem; }
  .chart-card { background:var(--card); border:1px solid var(--border); border-radius:12px; padding:1rem; overflow:hidden; }

  /* AI INSIGHTS */
  .insights-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:1rem; margin-bottom:2rem; }
  .insight-card { background:var(--card); border:1px solid var(--border); border-radius:12px; padding:1.25rem; }
  .insight-header { display:flex; justify-content:space-between; align-items:flex-start; gap:0.5rem; margin-bottom:0.75rem; }
  .insight-title { font-size:0.9rem; font-weight:600; color:var(--text); }
  .impact-badge { font-size:0.65rem; padding:2px 8px; border-radius:20px; font-weight:700; text-transform:uppercase; flex-shrink:0; }
  .impact-alto   { background:rgba(239,68,68,0.15); color:var(--danger); }
  .impact-medio  { background:rgba(245,158,11,0.15); color:var(--warning); }
  .impact-bajo   { background:rgba(100,116,139,0.2); color:var(--muted); }
  .insight-desc { font-size:0.82rem; color:var(--muted); margin-bottom:0.75rem; line-height:1.5; }
  .insight-action { font-size:0.82rem; color:var(--accent2); padding-left:0.75rem; border-left:2px solid var(--accent2); line-height:1.4; }

  /* ALERTAS */
  .alertas-list { display:flex; flex-direction:column; gap:0.75rem; margin-bottom:2rem; }
  .alerta { border-radius:10px; padding:0.9rem 1.1rem; display:flex; gap:0.75rem; align-items:flex-start; border:1px solid; }
  .alerta.oportunidad { background:rgba(16,185,129,0.08); border-color:rgba(16,185,129,0.25); }
  .alerta.riesgo      { background:rgba(239,68,68,0.08); border-color:rgba(239,68,68,0.25); }
  .alerta.tendencia   { background:rgba(59,130,246,0.08); border-color:rgba(59,130,246,0.25); }
  .alerta-icon { font-size:1rem; flex-shrink:0; margin-top:1px; }
  .alerta-msg  { font-size:0.83rem; color:var(--text); line-height:1.5; }

  /* RECOMENDACION TOP */
  .rec-top { background:linear-gradient(135deg,rgba(59,130,246,0.15),rgba(6,182,212,0.15)); border:1px solid rgba(59,130,246,0.3); border-radius:12px; padding:1.5rem; margin-bottom:2rem; }
  .rec-top .label { font-size:0.72rem; color:var(--accent); text-transform:uppercase; letter-spacing:0.1em; font-weight:600; margin-bottom:0.5rem; }
  .rec-top .texto { font-size:1rem; color:var(--text); font-weight:500; line-height:1.5; }
  .rec-top .proyeccion { font-size:0.82rem; color:var(--muted); margin-top:0.75rem; }

  /* FOOTER */
  footer { border-top:1px solid var(--border); padding-top:1.5rem; margin-top:2rem; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem; }
  footer p { font-size:0.75rem; color:var(--muted); }
  .powered { font-size:0.72rem; color:var(--subtle); }
</style>
</head>
<body>
<div class="wrapper">

  <!-- HEADER -->
  <div class="header">
    <div class="brand">
      <div class="brand-icon">📊</div>
      <div>
        <div class="brand-name">RetailInsights.ai</div>
        <div class="brand-sub">Analytics automatizado para retail</div>
      </div>
    </div>
    <div class="meta">
      <strong>{{ client_name }}</strong><br>
      Período: {{ kpis.fecha_inicio }} → {{ kpis.fecha_fin }}<br>
      {{ kpis.n_dias }} días analizados
    </div>
  </div>

  <!-- SEMAFORO IA -->
  {% if insights %}
  <div class="semaforo-bar {{ insights.semaforo }}">
    <div class="dot"></div>
    <div class="semaforo-text">
      <strong>Estado del negocio: {{ insights.semaforo | upper }}</strong>
      <p>{{ insights.semaforo_razon }}</p>
    </div>
  </div>
  {% endif %}

  <!-- KPI GRID -->
  <div class="kpi-grid">
    <div class="kpi-card">
      <div class="kpi-label">Revenue total</div>
      <div class="kpi-value">${{ "{:,.0f}".format(kpis.revenue_total) }}</div>
      <div class="kpi-sub">{{ kpis.n_dias }} días · ${{ "{:,.0f}".format(kpis.promedio_diario) }}/día</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Transacciones</div>
      <div class="kpi-value">{{ "{:,}".format(kpis.n_transacciones) }}</div>
      <div class="kpi-sub">Ticket prom. ${{ "{:,.2f}".format(kpis.ticket_promedio) }}</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Crecimiento MoM</div>
      <div class="kpi-value">{{ kpis.mom_growth_pct }}%</div>
      <span class="kpi-badge {% if kpis.mom_growth_pct >= 0 %}badge-pos{% else %}badge-neg{% endif %}">
        {% if kpis.mom_growth_pct >= 0 %}▲{% else %}▼{% endif %} vs mes anterior
      </span>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Mejor mes</div>
      <div class="kpi-value" style="font-size:1.1rem;padding-top:0.3rem">{{ kpis.mejor_mes }}</div>
      <div class="kpi-sub">Peor: {{ kpis.peor_mes }}</div>
    </div>
    {% if kpis.categoria_top is defined %}
    <div class="kpi-card">
      <div class="kpi-label">Categoría #1</div>
      <div class="kpi-value" style="font-size:1rem;padding-top:0.3rem">{{ kpis.categoria_top }}</div>
    </div>
    {% endif %}
    {% if kpis.region_top is defined %}
    <div class="kpi-card">
      <div class="kpi-label">Región #1</div>
      <div class="kpi-value" style="font-size:1rem;padding-top:0.3rem">{{ kpis.region_top }}</div>
    </div>
    {% endif %}
  </div>

  <!-- RECOMENDACION TOP -->
  {% if insights %}
  <div class="rec-top">
    <div class="label">Recomendación prioritaria · IA</div>
    <div class="texto">{{ insights.recomendacion_top }}</div>
    <div class="proyeccion">Proyección 30 días: {{ insights.proyeccion_proximos_30_dias }}</div>
  </div>
  {% endif %}

  <!-- CHARTS -->
  <div class="section-title">Visualizaciones</div>
  <div class="chart-grid">
    {% for name, path in charts.items() %}
    <div class="chart-card">{{ chart_html[name] }}</div>
    {% endfor %}
  </div>

  <!-- AI INSIGHTS -->
  {% if insights and insights.insights %}
  <div class="section-title">Insights de negocio · IA</div>
  <div class="insights-grid">
    {% for ins in insights.insights %}
    <div class="insight-card">
      <div class="insight-header">
        <div class="insight-title">{{ ins.titulo }}</div>
        <span class="impact-badge impact-{{ ins.impacto }}">{{ ins.impacto }}</span>
      </div>
      <div class="insight-desc">{{ ins.descripcion }}</div>
      <div class="insight-action">{{ ins.accion }}</div>
    </div>
    {% endfor %}
  </div>
  {% endif %}

  <!-- ALERTAS -->
  {% if insights and insights.alertas %}
  <div class="section-title">Alertas</div>
  <div class="alertas-list">
    {% for alerta in insights.alertas %}
    <div class="alerta {{ alerta.tipo }}">
      <div class="alerta-icon">
        {% if alerta.tipo == 'oportunidad' %}✅{% elif alerta.tipo == 'riesgo' %}⚠️{% else %}📈{% endif %}
      </div>
      <div class="alerta-msg">{{ alerta.mensaje }}</div>
    </div>
    {% endfor %}
  </div>
  {% endif %}

  <footer>
    <p>Generado por RetailInsights.ai · {{ kpis.fecha_fin }}</p>
    <p class="powered">Powered by Python · Plotly · Claude AI</p>
  </footer>

</div>
</body>
</html>"""


def export_report(
    kpis: dict,
    charts: dict,
    insights: dict = None,
    client_name: str = "Cliente",
    output_path: str = "reports/automated_report.html",
) -> str:
    chart_html = {}
    for name, path in charts.items():
        try:
            with open(path, "r", encoding="utf-8") as f:
                chart_html[name] = f.read()
        except FileNotFoundError:
            chart_html[name] = f"<p style='color:#64748b'>Chart no disponible: {name}</p>"

    tmpl = Template(TEMPLATE)
    html = tmpl.render(
        kpis=kpis,
        charts=charts,
        chart_html=chart_html,
        insights=insights or {},
        client_name=client_name,
    )

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Reporte HTML generado: {output_path}")

    # PDF opcional con WeasyPrint
    try:
        from weasyprint import HTML as WH
        pdf_path = output_path.replace(".html", ".pdf")
        WH(filename=output_path).write_pdf(pdf_path)
        print(f"✅ Reporte PDF generado: {pdf_path}")
    except ImportError:
        pass  # WeasyPrint opcional
    except Exception as e:
        print(f"⚠️  PDF no generado: {e}")

    return output_path
