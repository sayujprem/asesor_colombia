"""
Asesor_Colombia — Interfaz web Streamlit
Diseño: Midnight Luxe — Obsidiana · Champán · Marfil · Pizarra
Stateless: sin almacenamiento de datos, sin cookies persistentes.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import streamlit as st
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
)

# ── Tools ────────────────────────────────────────────────────────────────────

TOOLS: list[dict] = [
    {
        "name": "calcular_renta",
        "description": (
            "Calcula el impuesto de renta para personas naturales residentes en Colombia. "
            "Tabla progresiva Art. 241 ET (Ley 2010/2019). Cédula general: trabajo, capital, no laborales. "
            "Aplica exenciones (25% laboral, FVP, AFC) y tope Art. 336 ET."
        ),
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
        "description": "Calcula impuesto dividendos persona natural residente. Art. 242 ET, Ley 2277/2022. Integración a cédula general y descuento Art. 254-1.",
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
        "description": "Calcula impuesto ganancia ocasional: venta acciones, inmuebles, herencias. Tarifa 15% Art. 314 ET (Ley 2277/2022). Exención casa habitación 5.000 UVT.",
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
        "description": "Calcula aportes PILA independientes. Base 40% ingreso bruto. Salud 12.5% + Pensión 16%.",
        "input_schema": {
            "type": "object",
            "properties": {"ingreso_mensual": {"type": "number"}},
            "required": ["ingreso_mensual"],
        },
    },
    {
        "name": "calcular_ingresos_exterior",
        "description": "Calcula impuesto ingresos del exterior. Renta mundial Art. 9 ET. Descuento Art. 254 ET.",
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
        "description": "Diagnóstica tramo marginal, ahorro por cada peso en FVP/AFC y distancia al siguiente tramo.",
        "input_schema": {
            "type": "object",
            "properties": {"ingreso_anual": {"type": "number"}},
            "required": ["ingreso_anual"],
        },
    },
    {
        "name": "comparar_vehiculos_inversion",
        "description": "Compara CDT, FIC, FVP, Acciones BVC y AFC en capital neto después de impuestos.",
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
            return json.dumps(calcular_renta_persona_natural(**inputs, uvt=UVT_VIGENTE).resumen, ensure_ascii=False, indent=2)
        elif name == "calcular_dividendos":
            return json.dumps(calcular_impuesto_dividendos(**inputs, uvt=UVT_VIGENTE).resumen, ensure_ascii=False, indent=2)
        elif name == "calcular_ganancia_ocasional":
            return json.dumps(calcular_ganancia_ocasional(**inputs, uvt=UVT_VIGENTE).resumen, ensure_ascii=False, indent=2)
        elif name == "calcular_seguridad_social":
            return json.dumps(calcular_seguridad_social_independiente(**inputs, smlmv=SMLMV_VIGENTE).resumen, ensure_ascii=False, indent=2)
        elif name == "calcular_ingresos_exterior":
            return json.dumps(calcular_impuesto_ingresos_exterior(**inputs, uvt=UVT_VIGENTE).resumen, ensure_ascii=False, indent=2)
        elif name == "analizar_tarifa_marginal":
            return json.dumps(analizar_tarifa_marginal(**inputs, uvt=UVT_VIGENTE), ensure_ascii=False, indent=2)
        elif name == "comparar_vehiculos_inversion":
            return json.dumps(comparar_vehiculos_inversion(**inputs, uvt=UVT_VIGENTE), ensure_ascii=False, indent=2)
        else:
            return json.dumps({"error": f"Herramienta '{name}' no reconocida."})
    except Exception as e:
        return json.dumps({"error": str(e)})


# ── Config de página ─────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Asesor Colombia",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Midnight Luxe — Sistema de Diseño ────────────────────────────────────────
# Paleta: Obsidiana #0D0D12 · Champán #C9A84C · Marfil #FAF8F5 · Pizarra #2A2A35
# Tipografía: Inter (títulos) · Playfair Display Italic (drama) · JetBrains Mono (datos)

st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@1,400;1,500;1,700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">

<!-- Textura de ruido SVG (feTurbulence 0.05 opacity) -->
<div id="noise-overlay" style="
    position: fixed; top: 0; left: 0;
    width: 100vw; height: 100vh;
    pointer-events: none;
    z-index: 999999;
    opacity: 0.045;
    background-image: url('data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%22300%22 height=%22300%22><filter id=%22n%22><feTurbulence type=%22fractalNoise%22 baseFrequency=%220.75%22 numOctaves=%224%22 stitchTiles=%22stitch%22/><feColorMatrix type=%22saturate%22 values=%220%22/></filter><rect width=%22300%22 height=%22300%22 filter=%22url(%23n)%22 opacity=%221%22/></svg>');
"></div>

<style>
    /* ── Reset y base ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@1,400;1,500;1,700&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, .stApp {
        background-color: #0D0D12 !important;
        font-family: 'Inter', sans-serif !important;
        color: #FAF8F5 !important;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background-color: #0f0f16 !important;
        border-right: 1px solid #1e1e2a !important;
    }
    [data-testid="stSidebar"] * { color: #FAF8F5 !important; }
    [data-testid="stSidebarNav"] { display: none; }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-track { background: #0D0D12; }
    ::-webkit-scrollbar-thumb { background: #C9A84C33; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #C9A84C66; }

    /* ── Mensajes de chat ── */
    [data-testid="stChatMessage"] {
        background: transparent !important;
        border: none !important;
        padding: 4px 0 !important;
    }

    /* Burbuja usuario */
    [data-testid="stChatMessage"][data-testid*="user"],
    .stChatMessage:has([data-testid="chatAvatarIcon-user"]) {
        background: #1a1a24 !important;
        border-radius: 1.5rem !important;
        border: 1px solid #2A2A3580 !important;
        padding: 12px 18px !important;
        margin: 6px 0 !important;
    }

    /* ── Input de chat ── */
    [data-testid="stChatInputContainer"] {
        background: #13131a !important;
        border-top: 1px solid #1e1e2a !important;
        padding: 12px 0 !important;
    }
    [data-testid="stChatInput"] textarea {
        background: #1a1a26 !important;
        border: 1px solid #2A2A4080 !important;
        border-radius: 1.5rem !important;
        color: #FAF8F5 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.9rem !important;
        padding: 14px 20px !important;
        transition: border-color 0.2s ease !important;
    }
    [data-testid="stChatInput"] textarea:focus {
        border-color: #C9A84C66 !important;
        box-shadow: 0 0 0 2px #C9A84C15 !important;
    }
    [data-testid="stChatInput"] textarea::placeholder { color: #4a4a60 !important; }

    /* Botón enviar */
    [data-testid="stChatInputSubmitButton"] button {
        background: #C9A84C !important;
        border-radius: 50% !important;
        border: none !important;
        color: #0D0D12 !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease !important;
    }
    [data-testid="stChatInputSubmitButton"] button:hover {
        transform: scale(1.06) !important;
        box-shadow: 0 0 16px #C9A84C40 !important;
    }

    /* ── Botones quick-prompt ── */
    .stButton > button {
        background: #13131e !important;
        border: 1px solid #2A2A3880 !important;
        border-radius: 2rem !important;
        color: #9a9ab0 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.77rem !important;
        font-weight: 400 !important;
        padding: 8px 14px !important;
        text-align: left !important;
        width: 100% !important;
        line-height: 1.4 !important;
        transition: all 0.2s ease !important;
        letter-spacing: 0.01em !important;
    }
    .stButton > button:hover {
        background: #1a1a2a !important;
        border-color: #C9A84C66 !important;
        color: #C9A84C !important;
        transform: translateX(2px) !important;
        box-shadow: 0 0 12px #C9A84C10 !important;
    }

    /* ── Divisores ── */
    hr { border-color: #1e1e2a !important; }
    [data-testid="stDivider"] { border-color: #1e1e2a !important; }

    /* ── Markdown body ── */
    .stMarkdown p, .stMarkdown li {
        color: #c8c8d8 !important;
        font-size: 0.88rem !important;
        line-height: 1.7 !important;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        color: #FAF8F5 !important;
    }
    .stMarkdown code {
        font-family: 'JetBrains Mono', monospace !important;
        background: #1a1a26 !important;
        color: #C9A84C !important;
        border-radius: 6px !important;
        padding: 2px 6px !important;
        font-size: 0.82rem !important;
    }
    .stMarkdown pre {
        background: #13131e !important;
        border: 1px solid #2A2A38 !important;
        border-radius: 1rem !important;
        padding: 16px !important;
    }
    .stMarkdown table {
        border-collapse: collapse !important;
        width: 100% !important;
    }
    .stMarkdown th {
        background: #1a1a26 !important;
        color: #C9A84C !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.78rem !important;
        padding: 8px 12px !important;
        border: 1px solid #2A2A38 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }
    .stMarkdown td {
        color: #c8c8d8 !important;
        font-size: 0.85rem !important;
        padding: 8px 12px !important;
        border: 1px solid #1e1e2a !important;
    }
    .stMarkdown tr:hover td { background: #1a1a2430 !important; }

    /* ── Tabs / selectbox ── */
    .stSelectbox > div > div {
        background: #1a1a26 !important;
        border-color: #2A2A38 !important;
        border-radius: 1rem !important;
        color: #FAF8F5 !important;
    }

    /* ── Spinner ── */
    .stSpinner > div { border-top-color: #C9A84C !important; }

    /* ── Ocultar elementos Streamlit ── */
    #MainMenu, footer, header { visibility: hidden !important; }
    [data-testid="stToolbar"] { display: none !important; }
    [data-testid="stDecoration"] { display: none !important; }
    [data-testid="stStatusWidget"] { display: none !important; }

    /* ── Avatar del asesor ── */
    [data-testid="chatAvatarIcon-assistant"] {
        background: linear-gradient(135deg, #C9A84C22, #C9A84C44) !important;
        border: 1px solid #C9A84C44 !important;
    }

    /* ── Main container padding ── */
    .main .block-container {
        padding-top: 0 !important;
        padding-bottom: 80px !important;
        max-width: 820px !important;
    }
</style>
""", unsafe_allow_html=True)


# ── Preguntas de inicio rápido ───────────────────────────────────────────────

QUICK_PROMPTS = [
    "¿Cuánto pago de renta si gano $150.000.000 al año?",
    "¿Cuánto ahorro en impuestos poniendo $10M en un FVP?",
    "Vendo un inmueble en $800M comprado en $300M — ¿cuánto pago?",
    "Gano $12M al mes como independiente — ¿cuánto me descuenta la UGPP?",
    "Recibo dividendos de mi empresa por $100M — ¿cuánto pago?",
    "Tengo $50M — ¿FIC, FVP, CDT o acciones en bolsa?",
    "Tengo ingresos del exterior — ¿cómo tributo en Colombia?",
    "¿Cómo bajo mi tarifa marginal si estoy en el tramo del 33%?",
]


# ── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
<div style="padding: 8px 0 20px 0;">
    <div style="font-family: 'Playfair Display', serif; font-style: italic; font-size: 1.1rem; color: #C9A84C; letter-spacing: 0.02em;">
        Asesor Colombia
    </div>
    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; color: #4a4a60; margin-top: 4px; letter-spacing: 0.08em; text-transform: uppercase;">
        Tributario · Fiscal · Inversiones
    </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div style="
    background: #13131e;
    border: 1px solid #C9A84C22;
    border-radius: 1rem;
    padding: 12px 14px;
    margin-bottom: 16px;
">
    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; color: #C9A84C; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px;">
        Cifras 2026
    </div>
    <div style="font-size: 0.78rem; color: #9a9ab0; line-height: 2;">
        UVT <span style="color: #FAF8F5; font-family: 'JetBrains Mono', monospace;">~$52.669</span><br>
        SMLMV <span style="color: #FAF8F5; font-family: 'JetBrains Mono', monospace;">$1.750.905</span><br>
        Renta máx. <span style="color: #FAF8F5; font-family: 'JetBrains Mono', monospace;">39%</span><br>
        G. Ocasional <span style="color: #FAF8F5; font-family: 'JetBrains Mono', monospace;">15%</span>
    </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div style="font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; color: #4a4a60; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 10px;">
    Consultas frecuentes
</div>
""", unsafe_allow_html=True)

    for i, prompt in enumerate(QUICK_PROMPTS):
        if st.button(f"{prompt}", key=f"qp_{i}"):
            st.session_state["quick_prompt"] = prompt
            st.rerun()

    st.markdown("<div style='height: 16px'></div>", unsafe_allow_html=True)
    st.divider()

    st.markdown("""
<div style="
    background: #13131e;
    border: 1px solid #1e1e2a;
    border-radius: 1rem;
    padding: 12px 14px;
    margin-top: 8px;
">
    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #C9A84C; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px;">
        Herramientas activas
    </div>
    <div style="font-size: 0.75rem; color: #6a6a80; line-height: 2.1;">
        ◆ Impuesto de renta (Art. 241)<br>
        ◆ Dividendos (Art. 242)<br>
        ◆ Ganancia ocasional (Art. 314)<br>
        ◆ Seguridad social PILA<br>
        ◆ Ingresos del exterior<br>
        ◆ Análisis tarifa marginal<br>
        ◆ Comparación de vehículos
    </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<div style='height: 8px'></div>", unsafe_allow_html=True)

    if st.button("↺  Nueva conversación", key="clear_btn"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("""
<div style="margin-top: 20px; padding: 10px 0; border-top: 1px solid #1e1e2a;">
    <div style="font-size: 0.68rem; color: #3a3a50; line-height: 1.8; font-family: 'Inter', sans-serif;">
        🔒 Sin almacenamiento de datos<br>
        Esta sesión se borra al cerrar.<br>
        No se comparte información personal.<br><br>
        Fuente: ET Colombia + Ley 2277/2022<br>
        No reemplaza asesoría jurídica.
    </div>
</div>
""", unsafe_allow_html=True)


# ── Header ───────────────────────────────────────────────────────────────────

st.markdown("""
<div style="
    padding: 36px 0 20px 0;
    border-bottom: 1px solid #1e1e2a;
    margin-bottom: 24px;
">
    <div style="
        font-family: 'Playfair Display', serif;
        font-style: italic;
        font-size: 2.2rem;
        font-weight: 400;
        color: #FAF8F5;
        line-height: 1.1;
        letter-spacing: -0.01em;
    ">
        Asesor <span style="color: #C9A84C;">Colombia</span>
    </div>
    <div style="
        font-family: 'Inter', sans-serif;
        font-size: 0.82rem;
        color: #4a4a62;
        margin-top: 8px;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    ">
        Planificación fiscal · Tributaria · Inversiones
    </div>
    <div style="
        display: flex;
        gap: 8px;
        margin-top: 14px;
        flex-wrap: wrap;
    ">
        <span style="background:#1a1a26;border:1px solid #C9A84C22;border-radius:20px;padding:3px 10px;font-family:'JetBrains Mono',monospace;font-size:0.68rem;color:#C9A84C;">ET Colombia</span>
        <span style="background:#1a1a26;border:1px solid #2A2A38;border-radius:20px;padding:3px 10px;font-family:'JetBrains Mono',monospace;font-size:0.68rem;color:#6a6a80;">Ley 2277/2022</span>
        <span style="background:#1a1a26;border:1px solid #2A2A38;border-radius:20px;padding:3px 10px;font-family:'JetBrains Mono',monospace;font-size:0.68rem;color:#6a6a80;">DIAN · UGPP · BVC</span>
        <span style="background:#0f1a0f;border:1px solid #1a3a1a;border-radius:20px;padding:3px 10px;font-family:'JetBrains Mono',monospace;font-size:0.68rem;color:#4a8a4a;">● Sin almacenamiento</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ── Estado de sesión ─────────────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []

if "client" not in st.session_state:
    st.session_state.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = get_system_prompt()


# ── Mensaje de bienvenida ────────────────────────────────────────────────────

if not st.session_state.messages:
    with st.chat_message("assistant", avatar="⚖️"):
        st.markdown("""
<div style="font-family: 'Playfair Display', serif; font-style: italic; font-size: 1.05rem; color: #C9A84C; margin-bottom: 12px;">
    Bienvenido.
</div>

Soy tu asesor tributario y de inversiones colombiano. Conozco el **Estatuto Tributario**, la **Ley 2277 de 2022** y la normativa vigente de la **DIAN** y la **UGPP**.

Puedo ayudarte a:

- **Calcular tu impuesto de renta** y encontrar cómo reducirlo legalmente
- **Optimizar tu asset allocation** para pagar menos a la DIAN
- **Analizar dividendos** de tu empresa o inversiones
- **Calcular ganancia ocasional** en venta de inmuebles o acciones
- **Estructurar tus aportes** a FVP, AFC y seguridad social
- **Declarar ingresos del exterior** correctamente

*Esta conversación no almacena datos. Al cerrar la sesión, todo se borra.*
""", unsafe_allow_html=True)


# ── Historial de mensajes ────────────────────────────────────────────────────

for msg in st.session_state.messages:
    role = msg["role"]
    content = msg["content"]

    if role == "user":
        with st.chat_message("user"):
            if isinstance(content, str):
                st.markdown(content)
    elif role == "assistant":
        with st.chat_message("assistant", avatar="⚖️"):
            if isinstance(content, list):
                for bloque in content:
                    if hasattr(bloque, "type") and bloque.type == "text" and bloque.text.strip():
                        st.markdown(bloque.text)
            elif isinstance(content, str):
                st.markdown(content)


# ── Input ────────────────────────────────────────────────────────────────────

user_input = st.session_state.pop("quick_prompt", None)
chat_input = st.chat_input("Escribe tu consulta tributaria o de inversiones...")
if chat_input:
    user_input = chat_input

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)

    st.session_state.messages.append({"role": "user", "content": user_input})

    # Serializar historial para la API
    historial_api = []
    for msg in st.session_state.messages:
        content = msg["content"]
        if isinstance(content, list):
            bloques = []
            for b in content:
                if hasattr(b, "type"):
                    if b.type == "text":
                        bloques.append({"type": "text", "text": b.text})
                    elif b.type == "tool_use":
                        bloques.append({"type": "tool_use", "id": b.id, "name": b.name, "input": b.input})
                    else:
                        bloques.append(b)
                else:
                    bloques.append(b)
            historial_api.append({"role": msg["role"], "content": bloques})
        else:
            historial_api.append({"role": msg["role"], "content": content})

    # Agentic loop
    with st.chat_message("assistant", avatar="⚖️"):
        respuesta_placeholder = st.empty()
        status_placeholder = st.empty()

        while True:
            status_placeholder.markdown(
                '<div style="font-family: \'JetBrains Mono\', monospace; font-size: 0.72rem; color: #C9A84C55; letter-spacing: 0.05em;">analizando consulta...</div>',
                unsafe_allow_html=True,
            )

            respuesta = st.session_state.client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=st.session_state.system_prompt,
                tools=TOOLS,
                messages=historial_api,
            )

            status_placeholder.empty()

            textos = []
            tool_uses = []
            for bloque in respuesta.content:
                if bloque.type == "text" and bloque.text.strip():
                    textos.append(bloque.text)
                elif bloque.type == "tool_use":
                    tool_uses.append(bloque)

            if textos:
                respuesta_placeholder.markdown("\n\n".join(textos))

            if respuesta.stop_reason == "end_turn" or not tool_uses:
                st.session_state.messages.append({"role": "assistant", "content": respuesta.content})
                break

            st.session_state.messages.append({"role": "assistant", "content": respuesta.content})

            historial_api.append({
                "role": "assistant",
                "content": [
                    {"type": "text", "text": b.text} if b.type == "text"
                    else {"type": "tool_use", "id": b.id, "name": b.name, "input": b.input}
                    for b in respuesta.content
                ],
            })

            tool_results = []
            for tu in tool_uses:
                status_placeholder.markdown(
                    f'<div style="font-family: \'JetBrains Mono\', monospace; font-size: 0.72rem; color: #C9A84C88; letter-spacing: 0.05em;">calculando {tu.name.replace("_", " ")}...</div>',
                    unsafe_allow_html=True,
                )
                resultado = ejecutar_herramienta(tu.name, tu.input)
                tool_results.append({"type": "tool_result", "tool_use_id": tu.id, "content": resultado})

            status_placeholder.empty()
            historial_api.append({"role": "user", "content": tool_results})
            st.session_state.messages.append({"role": "user", "content": tool_results})
