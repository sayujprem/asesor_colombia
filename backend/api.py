"""
Asesor_Colombia — Backend FastAPI
Streaming SSE + agentic loop con calculadoras tributarias colombianas.
"""

import json
import sys
import asyncio
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).parent))

import anthropic
from src.config import ANTHROPIC_API_KEY, MODEL, MAX_TOKENS
from src.conocimiento_tributario import get_system_prompt
from src.calculadoras import (
    calcular_renta_persona_natural,
    calcular_impuesto_dividendos,
    calcular_ganancia_ocasional,
    calcular_seguridad_social_independiente,
    calcular_impuesto_ingresos_exterior,
    analizar_tarifa_marginal,
    comparar_vehiculos_inversion,
    UVT_VIGENTE,
    SMLMV_VIGENTE,
)

app = FastAPI(title="Asesor Colombia API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SYSTEM_PROMPT = get_system_prompt()
CLIENT = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# ── Tool definitions ─────────────────────────────────────────────────────────

TOOLS: list[dict] = [
    {
        "name": "calcular_renta",
        "description": "Calcula impuesto de renta personas naturales residentes. Art. 241 ET, tabla progresiva 0%-39%. Cédula general: trabajo, capital, no laborales. Exenciones: 25% laboral, FVP, AFC. Tope Art. 336 ET: 40% / 1.340 UVT.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ingreso_laboral_anual": {"type": "number"},
                "ingreso_honorarios_anual": {"type": "number"},
                "ingreso_capital_anual": {"type": "number"},
                "ingreso_no_laboral_anual": {"type": "number"},
                "aporte_fvp": {"type": "number"},
                "aporte_afc": {"type": "number"},
                "deduccion_intereses_vivienda": {"type": "number"},
                "deduccion_dependientes": {"type": "number"},
                "tiene_pension_obligatoria": {"type": "boolean"},
            },
            "required": [],
        },
    },
    {
        "name": "calcular_dividendos",
        "description": "Calcula impuesto dividendos persona natural residente. Art. 242 ET modificado Ley 2277/2022. Integración cédula general + descuento Art. 254-1.",
        "input_schema": {
            "type": "object",
            "properties": {
                "dividendos_no_gravados": {"type": "number"},
                "dividendos_gravados": {"type": "number"},
                "otras_rentas_cedula_general_uvt": {"type": "number"},
            },
            "required": ["dividendos_no_gravados"],
        },
    },
    {
        "name": "calcular_ganancia_ocasional",
        "description": "Calcula ganancia ocasional: venta activos, inmuebles. Tarifa 15% Art. 314 ET (Ley 2277/2022). Exención casa habitación 5.000 UVT. Ajuste Art. 70 ET.",
        "input_schema": {
            "type": "object",
            "properties": {
                "precio_venta": {"type": "number"},
                "costo_fiscal_original": {"type": "number"},
                "tipo_activo": {"type": "string", "enum": ["acciones", "inmueble", "casa_habitacion", "otro"]},
                "aplica_ajuste_art70": {"type": "boolean"},
                "porcentaje_ajuste_art70": {"type": "number"},
            },
            "required": ["precio_venta", "costo_fiscal_original"],
        },
    },
    {
        "name": "calcular_seguridad_social",
        "description": "Calcula PILA independientes. Base 40% ingreso bruto (mín 1 SMLMV, máx 25 SMLMV). Salud 12.5% + Pensión 16%.",
        "input_schema": {
            "type": "object",
            "properties": {"ingreso_mensual": {"type": "number"}},
            "required": ["ingreso_mensual"],
        },
    },
    {
        "name": "calcular_ingresos_exterior",
        "description": "Calcula impuesto ingresos exterior. Renta mundial Art. 9 ET. Dividendos 20%, portafolio variable 14%/25%, renta fija 5%. Descuento Art. 254 ET.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ingreso_bruto_exterior": {"type": "number"},
                "tipo_ingreso": {"type": "string", "enum": ["dividendos", "portafolio_renta_variable", "portafolio_renta_fija", "servicios", "otro"]},
                "pais_origen": {"type": "string", "enum": ["no_paraiso", "paraiso_fiscal"]},
                "impuesto_pagado_exterior": {"type": "number"},
            },
            "required": ["ingreso_bruto_exterior"],
        },
    },
    {
        "name": "analizar_tarifa_marginal",
        "description": "Diagnóstica tramo marginal, ahorro por $1M en FVP/AFC y distancia al siguiente tramo.",
        "input_schema": {
            "type": "object",
            "properties": {"ingreso_anual": {"type": "number"}},
            "required": ["ingreso_anual"],
        },
    },
    {
        "name": "comparar_vehiculos_inversion",
        "description": "Compara capital neto tras impuestos: CDT, FIC, FVP, Acciones BVC, AFC.",
        "input_schema": {
            "type": "object",
            "properties": {
                "monto_a_invertir": {"type": "number"},
                "horizonte_anios": {"type": "integer"},
                "rentabilidad_esperada_anual": {"type": "number"},
                "tarifa_marginal": {"type": "number"},
            },
            "required": ["monto_a_invertir"],
        },
    },
]


def ejecutar_herramienta(name: str, inputs: dict) -> str:
    try:
        if name == "calcular_renta":
            return json.dumps(calcular_renta_persona_natural(**inputs, uvt=UVT_VIGENTE).resumen, ensure_ascii=False)
        elif name == "calcular_dividendos":
            return json.dumps(calcular_impuesto_dividendos(**inputs, uvt=UVT_VIGENTE).resumen, ensure_ascii=False)
        elif name == "calcular_ganancia_ocasional":
            return json.dumps(calcular_ganancia_ocasional(**inputs, uvt=UVT_VIGENTE).resumen, ensure_ascii=False)
        elif name == "calcular_seguridad_social":
            return json.dumps(calcular_seguridad_social_independiente(**inputs, smlmv=SMLMV_VIGENTE).resumen, ensure_ascii=False)
        elif name == "calcular_ingresos_exterior":
            return json.dumps(calcular_impuesto_ingresos_exterior(**inputs, uvt=UVT_VIGENTE).resumen, ensure_ascii=False)
        elif name == "analizar_tarifa_marginal":
            return json.dumps(analizar_tarifa_marginal(**inputs, uvt=UVT_VIGENTE), ensure_ascii=False)
        elif name == "comparar_vehiculos_inversion":
            return json.dumps(comparar_vehiculos_inversion(**inputs, uvt=UVT_VIGENTE), ensure_ascii=False)
        else:
            return json.dumps({"error": f"Tool '{name}' not found"})
    except Exception as e:
        return json.dumps({"error": str(e)})


# ── Modelos de request ───────────────────────────────────────────────────────

class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


# ── Endpoint de chat con SSE ─────────────────────────────────────────────────

async def run_agentic_loop(messages: list[dict]) -> AsyncGenerator[str, None]:
    """
    Ejecuta el agentic loop completo y emite eventos SSE.
    Formato: data: <json>\n\n
    Tipos de evento: "text_delta" | "tool_call" | "done" | "error"
    """
    history = list(messages)

    try:
        while True:
            # Llamada a Claude (síncrona en hilo separado para no bloquear)
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: CLIENT.messages.create(
                    model=MODEL,
                    max_tokens=MAX_TOKENS,
                    system=SYSTEM_PROMPT,
                    tools=TOOLS,
                    messages=history,
                ),
            )

            text_blocks = []
            tool_uses = []

            for block in response.content:
                if block.type == "text" and block.text.strip():
                    text_blocks.append(block.text)
                elif block.type == "tool_use":
                    tool_uses.append(block)

            # Emitir texto
            if text_blocks:
                full_text = "\n\n".join(text_blocks)
                yield f"data: {json.dumps({'type': 'text_delta', 'text': full_text}, ensure_ascii=False)}\n\n"

            # Si no hay tool_use, terminamos
            if response.stop_reason == "end_turn" or not tool_uses:
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
                break

            # Añadir respuesta del asistente al historial
            history.append({
                "role": "assistant",
                "content": [
                    {"type": "text", "text": b.text} if b.type == "text"
                    else {"type": "tool_use", "id": b.id, "name": b.name, "input": b.input}
                    for b in response.content
                ],
            })

            # Ejecutar herramientas
            tool_results = []
            for tu in tool_uses:
                yield f"data: {json.dumps({'type': 'tool_call', 'tool': tu.name.replace('_', ' ')}, ensure_ascii=False)}\n\n"
                result = await loop.run_in_executor(None, lambda tu=tu: ejecutar_herramienta(tu.name, tu.input))
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tu.id,
                    "content": result,
                })

            history.append({"role": "user", "content": tool_results})

    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"


@app.post("/api/chat")
async def chat(request: ChatRequest):
    messages = [{"role": m.role, "content": m.content} for m in request.messages]

    return StreamingResponse(
        run_agentic_loop(messages),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/health")
async def health():
    return {"status": "ok", "model": MODEL, "uvt": UVT_VIGENTE}


# ── Servir frontend en producción ────────────────────────────────────────────

FRONTEND_DIST = Path(__file__).parent.parent / "frontend" / "dist"

if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="static-assets")


@app.get("/")
async def serve_root():
    if FRONTEND_DIST.exists():
        return FileResponse(str(FRONTEND_DIST / "index.html"))
    return {"service": "Asesor Colombia API", "health": "/api/health", "docs": "/docs"}


@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """Sirve archivos estáticos del build de React. Fallback a index.html para rutas del SPA."""
    if not FRONTEND_DIST.exists():
        raise HTTPException(status_code=404, detail="Frontend no compilado. Ejecuta: cd frontend && npm run build")
    static_file = FRONTEND_DIST / full_path
    if static_file.is_file():
        return FileResponse(str(static_file))
    return FileResponse(str(FRONTEND_DIST / "index.html"))
