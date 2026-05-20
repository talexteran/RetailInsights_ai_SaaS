# RetailInsights.ai

Sube tu Excel o CSV de ventas → KPIs, gráficos e insights de IA automáticos.

## Cómo correr localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Cómo desplegar en Streamlit Cloud

1. Sube este repositorio a GitHub (rama `main`)
2. Ve a [share.streamlit.io](https://share.streamlit.io) → New app
3. Selecciona tu repo, rama `main`, archivo principal `app.py`
4. En **Settings → Secrets** agrega (opcional para insights con IA):
   ```
   ANTHROPIC_API_KEY = "sk-ant-..."
   ```
5. Haz clic en Deploy — la app queda pública con una URL compartible

## Columnas esperadas en el archivo de ventas

| Columna estándar | Aliases aceptados |
|---|---|
| fecha | date, fecha, order_date, sale_date, dt |
| ventas | sales, revenue, amount, total, monto, importe |
| producto | product, item, sku, product_line |
| categoria | category, tipo, department, city |
| region | store, branch, location, zona, sucursal |

Solo `fecha` y `ventas` son obligatorias. El resto es opcional.

## Estructura del proyecto

```
app.py              ← Punto de entrada (Streamlit)
requirements.txt    ← Dependencias
src/
  pipeline.py       ← Orquestador del flujo completo
  data_cleaning.py  ← Limpieza y detección de columnas
  generate_kpis.py  ← Cálculo de métricas de negocio
  generate_charts.py← Gráficos Plotly en memoria
  ai_insights.py    ← Insights con Claude API (+ fallback automático)
  export_report.py  ← Reporte HTML descargable
data/
  raw/              ← Datos de ejemplo
```
