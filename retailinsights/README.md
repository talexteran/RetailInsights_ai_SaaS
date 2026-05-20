# 📊 RetailInsights.ai — SaaS de Analytics para Retail

Sistema automatizado de análisis de ventas retail con IA.  
El cliente sube su Excel → recibe KPIs + dashboard + insights en lenguaje natural.

---

## ⚡ Instalación y arranque en 4 comandos

```bash
# 1. Clonar / descomprimir el proyecto
cd RetailInsights.ai

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. (Opcional) Configurar API key de Claude para insights con IA real
export ANTHROPIC_API_KEY="sk-ant-..."       # Mac/Linux
set ANTHROPIC_API_KEY=sk-ant-...            # Windows CMD

# 4. Lanzar la app
streamlit run app.py
```

Abre http://localhost:8501 en tu navegador. Sube tu Excel. Listo.

---

## 📁 Estructura del proyecto

```
RetailInsights.ai/
├── app.py                    ← UI Streamlit (punto de entrada)
├── requirements.txt
├── .env                      ← ANTHROPIC_API_KEY aquí (opcional)
├── src/
│   ├── pipeline.py           ← Orquestador principal
│   ├── data_cleaning.py      ← Limpieza automática de datos
│   ├── generate_kpis.py      ← Cálculo de KPIs de negocio
│   ├── generate_charts.py    ← Visualizaciones Plotly
│   ├── export_report.py      ← Reporte HTML + PDF opcional
│   └── ai_insights.py        ← Insights con Claude API
├── data/
│   ├── raw/                  ← Dataset original (sin modificar)
│   ├── processed/            ← CSV limpio generado
│   └── exports/              ← KPIs exportados en CSV
└── reports/                  ← Reporte HTML generado
```

---

## 🔧 Uso por CLI (sin interfaz web)

```bash
python src/pipeline.py --input data/raw/ventas.xlsx --client "Supermercados XYZ"
```

Genera automáticamente:
- `reports/automated_report.html` — reporte ejecutivo
- `data/exports/kpis_summary.csv` — KPIs en CSV
- `data/processed/clean_data.csv` — datos limpios

---

## 📐 Columnas que detecta automáticamente

| Columna estándar | Aliases aceptados |
|---|---|
| `fecha` | date, dt, order_date, sale_date |
| `ventas` | sales, revenue, amount, total, monto |
| `producto` | product, item, sku, product_line |
| `categoria` | category, type, department, city |
| `region` | store, branch, location, zona |
| `cantidad` | quantity, qty, units |

El sistema detecta variantes automáticamente. No necesitas renombrar columnas.

---

## 🤖 IA con Claude API

Sin API key → el sistema genera insights con reglas automáticas (siempre funciona).  
Con API key → Claude analiza tus KPIs y produce insights contextuales en lenguaje natural.

Para agregar la API key, crea un archivo `.env` en la raíz:
```
ANTHROPIC_API_KEY=sk-ant-tu-clave-aqui
```

O ingrésala directamente en el sidebar de la app.

---

## 🚀 Despliegue en Streamlit Community Cloud (gratis)

1. Sube el proyecto a un repositorio de GitHub
2. Ve a https://share.streamlit.io
3. Haz clic en "New app"
4. Selecciona tu repo y pon `app.py` como archivo principal
5. En "Secrets" agrega: `ANTHROPIC_API_KEY = "sk-ant-..."`
6. Clic en Deploy

Tu SaaS estará en: `https://tu-app.streamlit.app`

---

## 💰 Cómo monetizarlo como SaaS (Fase 2)

### Opción A — Fiverr/Upwork (inmediato)
- Cobras por análisis: cliente te manda Excel, tú corres el pipeline, le entregas el reporte HTML
- Precio sugerido: $50–$150 por análisis dependiendo del volumen

### Opción B — SaaS con pago (3–6 semanas extra)
Agrega autenticación con Supabase + pagos con Stripe:

```bash
pip install supabase stripe
```

Flujo:
1. Cliente se registra → Stripe crea suscripción
2. Webhook Stripe activa cuenta en Supabase
3. Streamlit verifica token JWT en cada sesión
4. Límites de análisis por plan (Free: 3/mes, Pro: ilimitado)

### Opción C — API como servicio
Wrappea el pipeline con FastAPI:

```bash
pip install fastapi uvicorn python-multipart
uvicorn api:app --reload
```

Endpoints:
- `POST /analyze` — sube archivo, retorna JSON con KPIs + insights
- `GET /report/{id}` — descarga el reporte HTML

---

## 🗂️ Columnas del dataset de ejemplo (supermarket_sales.csv)

El dataset incluido tiene estas columnas mapeadas automáticamente:

| Original | Mapeado a |
|---|---|
| Date | fecha |
| Total | ventas |
| Product line | producto |
| City | región |
| Customer type | categoría |

---

## 📦 PDF export (opcional)

Para exportar reportes en PDF instala WeasyPrint:

```bash
# Linux/Mac
pip install weasyprint

# Windows — requiere GTK
# Ver: https://doc.courtbouillon.org/weasyprint/stable/first_steps.html
```

El PDF se genera automáticamente al lado del HTML cuando WeasyPrint está instalado.

---

*RetailInsights.ai — Sistema diseñado para ser replicable en múltiples clientes.*
