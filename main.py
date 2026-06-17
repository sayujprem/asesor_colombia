#!/usr/bin/env python3
"""
Asesor_Colombia — Asesor financiero, contable, tributario y de inversiones.
Powered by Claude + Estatuto Tributario de Colombia (Ley 2277/2022).

Uso:
    python main.py
    python main.py --modo rapido  # Sin banner, respuesta directa
    python main.py --debug        # Muestra tokens y detalles técnicos
"""

import json
import sys
import argparse
from pathlib import Path

# Asegura que src/ esté en el path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import anthropic
from config import ANTHROPIC_API_KEY, MODEL, MAX_TOKENS, UVT_VIGENTE, SMLMV_VIGENTE
from conocimiento_tributario import get_system_prompt
from calculadoras import (
    calcular_renta_persona_natural,
    calcular_impuesto_dividendos,
    calcular_ganancia_ocasional,
    calcular_seguridad_social_independiente,
    calcular_impuesto_ingresos_exterior,
    analizar_tarifa_marginal,
    comparar_vehiculos_inversion,
    UVT_VIGENTE as UVT_DEFAULT,
    SMLMV_VIGENTE as SMLMV_DEFAULT,
)


# ── Definición de herramientas (tools) para Claude ──────────────────────────

TOOLS: list[dict] = [
    {
        "name": "calcular_renta",
        "description": (
            "Calcula el impuesto de renta para personas naturales residentes en Colombia. "
            "Usa la tabla progresiva del Art. 241 ET (Ley 2010/2019). "
            "Incluye cédula general: trabajo, capital, no laborales. "
            "Aplica exenciones (25% laboral, FVP, AFC), deducciones y el tope del Art. 336 ET. "
            "Úsala cuando el usuario pregunte cuánto paga de renta, cómo reducir su impuesto "
            "o cuál es su tarifa marginal."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "ingreso_laboral_anual": {
                    "type": "number",
                    "description": "Ingresos laborales anuales en COP (salarios, prestaciones). Default 0.",
                },
                "ingreso_honorarios_anual": {
                    "type": "number",
                    "description": "Honorarios y servicios profesionales anuales en COP. Default 0.",
                },
                "ingreso_capital_anual": {
                    "type": "number",
                    "description": "Rentas de capital anuales en COP (intereses, arrendamientos, regalías). Default 0.",
                },
                "ingreso_no_laboral_anual": {
                    "type": "number",
                    "description": "Rentas no laborales anuales en COP (actividades comerciales independientes). Default 0.",
                },
                "aporte_fvp": {
                    "type": "number",
                    "description": "Aportes anuales a Fondo Voluntario de Pensión en COP. Default 0.",
                },
                "aporte_afc": {
                    "type": "number",
                    "description": "Aportes anuales a cuenta AFC en COP. Default 0.",
                },
                "deduccion_intereses_vivienda": {
                    "type": "number",
                    "description": "Intereses pagados por crédito hipotecario o leasing habitacional en el año (COP). Default 0.",
                },
                "deduccion_dependientes": {
                    "type": "number",
                    "description": "Deducción por dependientes económicos en COP (máx 10% ingreso / 32 UVT/mes). Default 0.",
                },
                "tiene_pension_obligatoria": {
                    "type": "boolean",
                    "description": "Si el contribuyente cotiza pensión obligatoria. Default true.",
                },
            },
            "required": [],
        },
    },
    {
        "name": "calcular_dividendos",
        "description": (
            "Calcula el impuesto sobre dividendos recibidos por persona natural residente en Colombia. "
            "Aplica Art. 242 ET modificado por Ley 2277/2022: integración a cédula general (tabla 241) "
            "y descuento Art. 254-1. "
            "Úsala cuando el usuario tenga dividendos de empresas colombianas o pregunte por la "
            "tributación de dividendos, distribución de utilidades o sociedades."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "dividendos_no_gravados": {
                    "type": "number",
                    "description": "Dividendos no gravados en cabeza de la sociedad (Art. 49 num. 3) en COP.",
                },
                "dividendos_gravados": {
                    "type": "number",
                    "description": "Dividendos gravados en cabeza de la sociedad (Art. 49 par. 2) en COP. Default 0.",
                },
                "otras_rentas_cedula_general_uvt": {
                    "type": "number",
                    "description": "Renta líquida gravable de la cédula general ya calculada (en UVT). Para sumar con dividendos. Default 0.",
                },
            },
            "required": ["dividendos_no_gravados"],
        },
    },
    {
        "name": "calcular_ganancia_ocasional",
        "description": (
            "Calcula el impuesto de ganancia ocasional en Colombia: venta de acciones, inmuebles, "
            "herencias, loterías (Art. 300-317 ET). Tarifa: 15% (Ley 2277/2022). "
            "Aplica exención casa de habitación (5.000 UVT) y ajuste fiscal Art. 70 ET. "
            "Úsala cuando el usuario venda activos, inmuebles, empresas o reciba herencias."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "precio_venta": {
                    "type": "number",
                    "description": "Precio de venta del activo en COP.",
                },
                "costo_fiscal_original": {
                    "type": "number",
                    "description": "Costo fiscal (precio de compra o valor declarado) en COP.",
                },
                "tipo_activo": {
                    "type": "string",
                    "enum": ["acciones", "inmueble", "casa_habitacion", "otro"],
                    "description": "Tipo de activo vendido.",
                },
                "aplica_ajuste_art70": {
                    "type": "boolean",
                    "description": "Si aplica el ajuste por inflación del Art. 70 ET. Default false.",
                },
                "porcentaje_ajuste_art70": {
                    "type": "number",
                    "description": "Porcentaje acumulado de inflación (IPC DANE) para ajuste Art. 70 ET. Ej: 15 para 15%.",
                },
            },
            "required": ["precio_venta", "costo_fiscal_original"],
        },
    },
    {
        "name": "calcular_seguridad_social",
        "description": (
            "Calcula los aportes a seguridad social (PILA) para trabajadores independientes en Colombia. "
            "Base: 40% del ingreso bruto. Salud: 12.5% | Pensión: 16%. "
            "Úsala cuando el usuario sea independiente, freelance, o pregunte por UGPP, PILA, "
            "cotización de salud/pensión."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "ingreso_mensual": {
                    "type": "number",
                    "description": "Ingreso bruto mensual promedio en COP.",
                },
            },
            "required": ["ingreso_mensual"],
        },
    },
    {
        "name": "calcular_ingresos_exterior",
        "description": (
            "Calcula el impuesto sobre ingresos del exterior para residentes colombianos. "
            "Aplica renta mundial (Art. 9 ET), tarifas por tipo (dividendos 20%, portafolio variable 14%/25%, "
            "renta fija 5%), y descuento por impuesto pagado en el exterior (Art. 254 ET). "
            "Úsala cuando el usuario tenga inversiones, dividendos, cuentas o ingresos fuera de Colombia."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "ingreso_bruto_exterior": {
                    "type": "number",
                    "description": "Monto del ingreso proveniente del exterior en COP (convertido a la TRM del momento).",
                },
                "tipo_ingreso": {
                    "type": "string",
                    "enum": ["dividendos", "portafolio_renta_variable", "portafolio_renta_fija", "servicios", "otro"],
                    "description": "Tipo de ingreso del exterior.",
                },
                "pais_origen": {
                    "type": "string",
                    "enum": ["no_paraiso", "paraiso_fiscal"],
                    "description": "Si el país de origen es paraíso fiscal según DIAN. Default: no_paraiso.",
                },
                "impuesto_pagado_exterior": {
                    "type": "number",
                    "description": "Impuesto ya pagado en el país extranjero en COP. Para descuento Art. 254 ET. Default 0.",
                },
            },
            "required": ["ingreso_bruto_exterior"],
        },
    },
    {
        "name": "analizar_tarifa_marginal",
        "description": (
            "Analiza en qué tramo marginal está el contribuyente, cuánto ahorra por cada peso "
            "que mete a FVP/AFC, y cuánto le falta para el siguiente tramo. "
            "Úsala siempre que el usuario mencione sus ingresos, pregunte por su tarifa efectiva, "
            "o quiera entender cuánto le conviene invertir en vehículos exentos."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "ingreso_anual": {
                    "type": "number",
                    "description": "Ingreso anual total en COP (antes de exenciones).",
                },
            },
            "required": ["ingreso_anual"],
        },
    },
    {
        "name": "comparar_vehiculos_inversion",
        "description": (
            "Compara el resultado neto después de impuestos de diferentes vehículos de inversión "
            "colombianos: CDT, FIC, FVP, acciones BVC, AFC. "
            "Úsala cuando el usuario pregunte dónde invertir, qué le conviene más fiscalmente, "
            "o compare opciones de inversión."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "monto_a_invertir": {
                    "type": "number",
                    "description": "Capital a invertir en COP.",
                },
                "horizonte_anios": {
                    "type": "integer",
                    "description": "Horizonte de inversión en años. Default 5.",
                },
                "rentabilidad_esperada_anual": {
                    "type": "number",
                    "description": "Rentabilidad anual esperada como decimal (ej: 0.10 para 10%). Default 0.10.",
                },
                "tarifa_marginal": {
                    "type": "number",
                    "description": "Tarifa marginal de renta del contribuyente como decimal (ej: 0.33 para 33%). Default 0.33.",
                },
            },
            "required": ["monto_a_invertir"],
        },
    },
]


# ── Ejecución de herramientas ────────────────────────────────────────────────

def ejecutar_herramienta(name: str, inputs: dict) -> str:
    uvt = UVT_VIGENTE
    smlmv = SMLMV_VIGENTE

    try:
        if name == "calcular_renta":
            resultado = calcular_renta_persona_natural(**inputs, uvt=uvt)
            return json.dumps(resultado.resumen, ensure_ascii=False, indent=2)

        elif name == "calcular_dividendos":
            resultado = calcular_impuesto_dividendos(**inputs, uvt=uvt)
            return json.dumps(resultado.resumen, ensure_ascii=False, indent=2)

        elif name == "calcular_ganancia_ocasional":
            resultado = calcular_ganancia_ocasional(**inputs, uvt=uvt)
            return json.dumps(resultado.resumen, ensure_ascii=False, indent=2)

        elif name == "calcular_seguridad_social":
            resultado = calcular_seguridad_social_independiente(**inputs, smlmv=smlmv)
            return json.dumps(resultado.resumen, ensure_ascii=False, indent=2)

        elif name == "calcular_ingresos_exterior":
            resultado = calcular_impuesto_ingresos_exterior(**inputs, uvt=uvt)
            return json.dumps(resultado.resumen, ensure_ascii=False, indent=2)

        elif name == "analizar_tarifa_marginal":
            resultado = analizar_tarifa_marginal(**inputs, uvt=uvt)
            return json.dumps(resultado, ensure_ascii=False, indent=2)

        elif name == "comparar_vehiculos_inversion":
            resultado = comparar_vehiculos_inversion(**inputs, uvt=uvt)
            return json.dumps(resultado, ensure_ascii=False, indent=2)

        else:
            return json.dumps({"error": f"Herramienta '{name}' no reconocida."})

    except Exception as e:
        return json.dumps({"error": f"Error al ejecutar '{name}': {str(e)}"})


# ── UI — Banner y formato ────────────────────────────────────────────────────

BANNER = """
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║              ASESOR_COLOMBIA — Asesor Tributario & Financiero            ║
║                                                                          ║
║   Experto en: Renta · Dividendos · Ganancias Ocasionales · SS           ║
║               Inversiones · Asset Allocation · Planificación Fiscal      ║
║                                                                          ║
║   Fuente: Estatuto Tributario ET + Ley 2277/2022 + Ley 2010/2019       ║
║   UVT 2026: ~$52.669 | SMLMV 2026: $1.750.905                          ║
║                                                                          ║
║   Escribe 'salir' o 'exit' para terminar · Ctrl+C para interrumpir     ║
╚══════════════════════════════════════════════════════════════════════════╝

Hola. Soy tu asesor tributario y de inversiones colombiano.

Puedo ayudarte con:
  • ¿Cuánto pago de renta? ¿Cómo bajo mi tarifa marginal?
  • ¿Qué me conviene más: FVP, AFC, CDT o acciones en bolsa?
  • ¿Cuánto pago de impuesto si vendo un inmueble o acciones?
  • ¿Cómo tributo mis dividendos de empresa colombiana?
  • ¿Qué pasa si tengo ingresos del exterior?
  • ¿Cuánto debo cotizar a la UGPP como independiente?
  • ¿Cómo optimizo mi asset allocation para pagar menos a la DIAN?

¿En qué te ayudo hoy?
"""

SEPARADOR = "─" * 72


# ── Loop principal del chatbot ───────────────────────────────────────────────

def run_asesor(modo_rapido: bool = False, debug: bool = False) -> None:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    system_prompt = get_system_prompt()
    historial: list[dict] = []

    if not modo_rapido:
        print(BANNER)

    while True:
        try:
            print(f"\n{SEPARADOR}")
            pregunta = input("Tú: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nHasta luego. ¡Que le vaya bien con sus finanzas!")
            break

        if not pregunta:
            continue
        if pregunta.lower() in {"salir", "exit", "quit", "q"}:
            print("\nHasta luego. ¡Que le vaya bien con sus finanzas!")
            break

        historial.append({"role": "user", "content": pregunta})

        # Agentic loop: Claude puede usar múltiples herramientas en una respuesta
        while True:
            respuesta = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=system_prompt,
                tools=TOOLS,
                messages=historial,
            )

            if debug:
                print(f"\n[DEBUG] stop_reason={respuesta.stop_reason} | tokens entrada={respuesta.usage.input_tokens} | salida={respuesta.usage.output_tokens}")

            # Extraer texto y tool_use del response
            textos = []
            tool_uses = []

            for bloque in respuesta.content:
                if bloque.type == "text":
                    textos.append(bloque.text)
                elif bloque.type == "tool_use":
                    tool_uses.append(bloque)

            # Mostrar texto parcial si lo hay
            if textos:
                texto_parcial = "\n".join(textos)
                if texto_parcial.strip():
                    print(f"\n{SEPARADOR}")
                    print(f"Asesor_Colombia:\n\n{texto_parcial}")

            # Si no hay tool_use, terminamos el turno
            if respuesta.stop_reason == "end_turn" or not tool_uses:
                # Añadir respuesta completa al historial
                historial.append({"role": "assistant", "content": respuesta.content})
                break

            # Hay tool_use — ejecutar herramientas
            historial.append({"role": "assistant", "content": respuesta.content})

            tool_results = []
            for tool_use in tool_uses:
                if debug:
                    print(f"\n[DEBUG] Usando herramienta: {tool_use.name}")
                    print(f"[DEBUG] Inputs: {json.dumps(tool_use.input, ensure_ascii=False)}")

                resultado = ejecutar_herramienta(tool_use.name, tool_use.input)

                if debug:
                    print(f"[DEBUG] Resultado: {resultado}")

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": resultado,
                })

            historial.append({"role": "user", "content": tool_results})
            # Continúa el loop para que Claude procese los resultados


# ── Entry point ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Asesor_Colombia — Asesor tributario y de inversiones colombiano"
    )
    parser.add_argument(
        "--modo", choices=["completo", "rapido"], default="completo",
        help="Modo de inicio (default: completo con banner)"
    )
    parser.add_argument(
        "--debug", action="store_true",
        help="Muestra tokens, nombres de herramientas y resultados raw"
    )
    args = parser.parse_args()

    run_asesor(
        modo_rapido=(args.modo == "rapido"),
        debug=args.debug,
    )


if __name__ == "__main__":
    main()
