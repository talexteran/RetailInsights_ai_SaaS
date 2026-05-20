"""
ai_insights.py
--------------
Genera insights de negocio accionables en lenguaje natural usando Claude API.
Toma el dict de KPIs calculado por generate_kpis.py y retorna análisis estructurado.

Requiere: pip install anthropic
Variable de entorno: ANTHROPIC_API_KEY
"""

import os
import json

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


SYSTEM_PROMPT = """Eres un consultor senior de retail analytics con 15 años de experiencia.
Analizas KPIs de ventas retail y produces insights accionables en español.
Responde SIEMPRE con un JSON válido y nada más. Sin texto antes ni después.
Sin backticks ni markdown. Solo el objeto JSON."""


def _build_prompt(kpis: dict) -> str:
    kpis_resumen = {
        "revenue_total": kpis.get("revenue_total"),
        "n_transacciones": kpis.get("n_transacciones"),
        "ticket_promedio": kpis.get("ticket_promedio"),
        "mom_growth_pct": kpis.get("mom_growth_pct"),
        "mejor_mes": kpis.get("mejor_mes"),
        "peor_mes": kpis.get("peor_mes"),
        "promedio_diario": kpis.get("promedio_diario"),
        "fecha_inicio": kpis.get("fecha_inicio"),
        "fecha_fin": kpis.get("fecha_fin"),
        "n_dias": kpis.get("n_dias"),
        "top_productos": kpis.get("top_productos", [])[:5],
        "ventas_categoria": kpis.get("ventas_categoria", [])[:5],
        "ventas_region": kpis.get("ventas_region", [])[:5],
        "mejor_dia": kpis.get("mejor_dia"),
        "categoria_top": kpis.get("categoria_top"),
        "region_top": kpis.get("region_top"),
    }

    return f"""Analiza estos KPIs de ventas retail y genera insights accionables:

{json.dumps(kpis_resumen, ensure_ascii=False, indent=2)}

Devuelve exactamente este JSON con tus análisis:
{{
  "resumen_ejecutivo": "2-3 oraciones describiendo el estado general del negocio",
  "semaforo": "verde | amarillo | rojo",
  "semaforo_razon": "razón breve del semáforo en 1 oración",
  "insights": [
    {{
      "titulo": "título corto del insight",
      "descripcion": "qué está pasando y por qué importa",
      "accion": "qué debe hacer el negocio específicamente",
      "impacto": "alto | medio | bajo"
    }}
  ],
  "alertas": [
    {{
      "tipo": "oportunidad | riesgo | tendencia",
      "mensaje": "descripción de la alerta en 1-2 oraciones"
    }}
  ],
  "proyeccion_proximos_30_dias": "proyección cualitativa basada en la tendencia actual",
  "recomendacion_top": "la acción más importante que debe tomar el negocio ahora mismo"
}}

Genera entre 3 y 5 insights. Entre 2 y 3 alertas. Sé específico con los números del dataset."""


def generate_insights(kpis: dict, api_key: str = None) -> dict:
    """
    Genera insights usando Claude API.
    Retorna dict con insights estructurados.
    Si la API no está disponible, retorna insights de fallback basados en reglas.
    """
    key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")

    if not ANTHROPIC_AVAILABLE or not key:
        return _fallback_insights(kpis)

    try:
        client = anthropic.Anthropic(api_key=key)
        message = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=2000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": _build_prompt(kpis)}],
        )
        raw = message.content[0].text.strip()
        # Limpiar posibles backticks residuales
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)

    except json.JSONDecodeError:
        return _fallback_insights(kpis)
    except Exception as e:
        return _fallback_insights(kpis, error=str(e))


def _fallback_insights(kpis: dict, error: str = None) -> dict:
    """
    Insights basados en reglas simples cuando la API no está disponible.
    Garantiza que el sistema siempre entregue algo útil.
    """
    revenue = kpis.get("revenue_total", 0)
    mom = kpis.get("mom_growth_pct", 0)
    ticket = kpis.get("ticket_promedio", 0)
    categoria_top = kpis.get("categoria_top", "N/A")
    region_top = kpis.get("region_top", "N/A")
    mejor_dia = kpis.get("mejor_dia", "N/A")
    mejor_mes = kpis.get("mejor_mes", "N/A")

    semaforo = "verde" if mom >= 5 else ("amarillo" if mom >= 0 else "rojo")
    semaforo_razon = (
        f"Crecimiento MoM de {mom}% indica tendencia positiva" if mom >= 5
        else (f"Crecimiento plano ({mom}%) requiere atención" if mom >= 0
              else f"Caída MoM de {mom}% — acción urgente requerida")
    )

    insights = [
        {
            "titulo": "Desempeño de revenue",
            "descripcion": f"El negocio generó ${revenue:,.0f} en el período analizado con un ticket promedio de ${ticket:,.2f}.",
            "accion": "Enfocarse en aumentar el ticket promedio mediante bundles o upselling en las categorías top.",
            "impacto": "alto"
        },
        {
            "titulo": f"Categoría líder: {categoria_top}",
            "descripcion": f"La categoría {categoria_top} domina las ventas. Concentrar allí el inventario y promociones.",
            "accion": f"Aumentar stock y visibilidad de {categoria_top}. Crear campaña específica para esta categoría.",
            "impacto": "alto"
        },
        {
            "titulo": f"Mejor día de ventas: {mejor_dia}",
            "descripcion": f"Los {mejor_dia} concentran el mayor volumen de ventas de la semana.",
            "accion": f"Asegurar máximo stock y personal los {mejor_dia}. Lanzar promociones los días de menor tráfico.",
            "impacto": "medio"
        },
    ]

    if region_top and region_top != "N/A":
        insights.append({
            "titulo": f"Región top: {region_top}",
            "descripcion": f"La región {region_top} lidera en ventas. Replicar sus prácticas en otras regiones.",
            "accion": f"Documentar y escalar el modelo operativo de {region_top} a las demás sucursales.",
            "impacto": "medio"
        })

    alertas = [
        {
            "tipo": "tendencia",
            "mensaje": f"El mejor mes fue {mejor_mes}. Analizar qué factores lo impulsaron para replicarlos."
        },
        {
            "tipo": "oportunidad" if mom >= 0 else "riesgo",
            "mensaje": semaforo_razon
        }
    ]

    result = {
        "resumen_ejecutivo": (
            f"El negocio generó ${revenue:,.0f} con {kpis.get('n_transacciones', 0):,} transacciones "
            f"y un ticket promedio de ${ticket:,.2f}. "
            f"El crecimiento mensual es de {mom}%, liderado por {categoria_top}."
        ),
        "semaforo": semaforo,
        "semaforo_razon": semaforo_razon,
        "insights": insights,
        "alertas": alertas,
        "proyeccion_proximos_30_dias": (
            "Tendencia positiva si se mantienen las condiciones actuales. "
            "Priorizar las categorías y regiones de mayor rendimiento."
            if mom >= 0 else
            "Tendencia negativa requiere intervención inmediata en pricing y mix de productos."
        ),
        "recomendacion_top": (
            f"Concentrar esfuerzos en {categoria_top} los días {mejor_dia} "
            f"para maximizar el revenue en el corto plazo."
        ),
        "_source": "fallback_rules" + (f" | API error: {error}" if error else "")
    }

    return result
