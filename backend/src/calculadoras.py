"""
Calculadoras tributarias colombianas — basadas en el Estatuto Tributario
y Ley 2277 de 2022. Todas las cifras en pesos colombianos (COP).

UVT 2024: $47.065 | UVT 2025: $49.799 | UVT 2026: $52.374 (Decreto DIAN oficial)
SMLMV 2026: $1.750.905
"""

from dataclasses import dataclass
from typing import Optional


# ── Constantes vigentes ─────────────────────────────────────────────────────

UVT_2024 = 47_065
UVT_2025 = 49_799
UVT_2026 = 52_374   # Decreto DIAN — valor oficial 2026
UVT_VIGENTE = UVT_2026

SMLMV_2026 = 1_750_905
SMLMV_VIGENTE = SMLMV_2026


# ── Tipos de resultado ───────────────────────────────────────────────────────

@dataclass
class ResultadoRenta:
    ingreso_bruto_anual: float
    renta_exenta_25pct: float
    aporte_pension_obligatoria: float
    aporte_salud_obligatoria: float
    aporte_fvp: float           # Fondos voluntarios de pensión
    aporte_afc: float
    deduccion_intereses_vivienda: float
    deduccion_dependientes: float
    deduccion_facturas_electronicas: float
    renta_liquida_gravable_uvt: float
    impuesto_uvt: float
    impuesto_cop: float
    tarifa_efectiva: float
    tarifa_marginal: float
    resumen: dict


@dataclass
class ResultadoDividendos:
    dividendos_no_gravados: float
    dividendos_gravados_sociedad: float
    impuesto_35_gravados: float
    base_tabla_241: float
    base_tabla_241_uvt: float
    impuesto_tabla_241: float
    descuento_art_254_1: float
    impuesto_neto: float
    tarifa_efectiva: float
    resumen: dict


@dataclass
class ResultadoGananciaOcasional:
    precio_venta: float
    costo_fiscal: float
    ajuste_inflacion_art70: float
    ganancia_bruta: float
    exencion_casa_habitacion: float
    ganancia_gravable: float
    impuesto: float        # 15% (Ley 2277/2022)
    tarifa: float
    resumen: dict


@dataclass
class ResultadoSeguridadSocial:
    ingreso_mensual: float
    base_cotizacion: float      # 40% del ingreso bruto (independientes)
    salud_mensual: float        # 12.5% de la base
    pension_mensual: float      # 16% de la base
    total_mensual: float
    total_anual: float
    resumen: dict


@dataclass
class ResultadoExterior:
    ingreso_bruto_exterior: float
    tipo_ingreso: str
    tarifa_retencion: float
    retencion_cop: float
    credito_impuesto_exterior: float
    impuesto_neto_colombia: float
    resumen: dict


# ── Utilidades internas ──────────────────────────────────────────────────────

def _a_uvt(valor_cop: float, uvt: float = UVT_VIGENTE) -> float:
    return valor_cop / uvt


def _a_cop(valor_uvt: float, uvt: float = UVT_VIGENTE) -> float:
    return valor_uvt * uvt


def _tabla_renta_241(base_uvt: float) -> tuple[float, float]:
    """
    Art. 241 ET — tabla progresiva personas naturales residentes.
    Retorna (impuesto_en_uvt, tarifa_marginal).
    Rangos y fórmulas según Ley 2010/2019 (vigente para 2024-2026).
    """
    if base_uvt <= 0:
        return 0.0, 0.0
    elif base_uvt <= 1_090:
        return 0.0, 0.0
    elif base_uvt <= 1_700:
        return (base_uvt - 1_090) * 0.19, 0.19
    elif base_uvt <= 4_100:
        return (base_uvt - 1_700) * 0.28 + 116, 0.28
    elif base_uvt <= 8_670:
        return (base_uvt - 4_100) * 0.33 + 788, 0.33
    elif base_uvt <= 18_970:
        return (base_uvt - 8_670) * 0.35 + 2_296, 0.35
    elif base_uvt <= 31_000:
        return (base_uvt - 18_970) * 0.37 + 5_901, 0.37
    else:
        return (base_uvt - 31_000) * 0.39 + 10_352, 0.39


# ── Calculadora 1: Impuesto de Renta — Persona Natural ──────────────────────

def calcular_renta_persona_natural(
    ingreso_laboral_anual: float = 0.0,
    ingreso_honorarios_anual: float = 0.0,
    ingreso_capital_anual: float = 0.0,       # intereses, arrendamientos, etc.
    ingreso_no_laboral_anual: float = 0.0,
    aporte_fvp: float = 0.0,                  # Fondo Voluntario de Pensión
    aporte_afc: float = 0.0,                  # Cuenta AFC
    deduccion_intereses_vivienda: float = 0.0,
    deduccion_dependientes: float = 0.0,       # hasta 10% ingreso, máx 32 UVT/mes
    tiene_pension_obligatoria: bool = True,
    uvt: float = UVT_VIGENTE,
) -> ResultadoRenta:
    """
    Calcula impuesto de renta cédula general (trabajo + capital + no laborales).
    Art. 241 ET, modificado por Ley 2010/2019 y Ley 2277/2022.

    Supuestos:
    - Persona natural residente, empleado o independiente.
    - No incluye cédula de dividendos (ver calcular_impuesto_dividendos).
    - Pensión obligatoria: 16% sobre ingreso, deducible.
    - Salud obligatoria: 12.5% sobre IBC, deducible.
    - Renta exenta 25% laboral aplica SOLO sobre ingresos laborales.
    - Límite total rentas exentas + deducciones especiales: 40% ingresos netos,
      máximo 1.340 UVT anuales (Art. 336 ET, Ley 2277/2022).
    """
    ingreso_laboral = max(0.0, ingreso_laboral_anual)
    ingreso_honorarios = max(0.0, ingreso_honorarios_anual)
    ingreso_capital = max(0.0, ingreso_capital_anual)
    ingreso_no_laboral = max(0.0, ingreso_no_laboral_anual)

    ingreso_bruto_total = ingreso_laboral + ingreso_honorarios + ingreso_capital + ingreso_no_laboral

    # Aportes obligatorios (deducibles — Art. 107 y 126-1 ET)
    base_ibc = ingreso_laboral + ingreso_honorarios
    if tiene_pension_obligatoria:
        aporte_pension_obligatoria = min(base_ibc * 0.16, _a_cop(25, uvt) * 12)
    else:
        aporte_pension_obligatoria = 0.0
    aporte_salud_obligatoria = min(base_ibc * 0.125, _a_cop(25, uvt) * 12)

    # Renta exenta 25% — solo sobre ingresos laborales y honorarios con relación laboral
    # Art. 206 num. 10 ET — límite 240 UVT/mes = 2.880 UVT/año
    renta_exenta_25_anual = ingreso_laboral * 0.25
    limite_exenta_25_cop = _a_cop(2_880, uvt)
    renta_exenta_25_anual = min(renta_exenta_25_anual, limite_exenta_25_cop)

    # Deducción por compras con factura electrónica: 1%, máx 240 UVT/año (Art. 107-2 ET)
    deduccion_facturas = min(ingreso_bruto_total * 0.01, _a_cop(240, uvt))

    # Ingreso neto (base para calcular el tope del 40%)
    ingreso_neto = ingreso_bruto_total - aporte_pension_obligatoria - aporte_salud_obligatoria

    # Tope 40% / 1.340 UVT (rentas exentas + deducciones especiales)
    tope_40_pct = ingreso_neto * 0.40
    tope_1340_uvt = _a_cop(1_340, uvt)
    tope_beneficios = min(tope_40_pct, tope_1340_uvt)

    # Acumular beneficios sujetos al tope
    beneficios_acumulados = (
        renta_exenta_25_anual
        + aporte_fvp
        + aporte_afc
        + deduccion_intereses_vivienda
        + deduccion_dependientes
        + deduccion_facturas
    )

    # Aplicar tope
    if beneficios_acumulados > tope_beneficios:
        factor_reduccion = tope_beneficios / beneficios_acumulados
        renta_exenta_25_aplicada = renta_exenta_25_anual * factor_reduccion
        fvp_aplicado = aporte_fvp * factor_reduccion
        afc_aplicado = aporte_afc * factor_reduccion
        ded_vivienda_aplicada = deduccion_intereses_vivienda * factor_reduccion
        ded_dep_aplicada = deduccion_dependientes * factor_reduccion
        ded_facturas_aplicada = deduccion_facturas * factor_reduccion
    else:
        renta_exenta_25_aplicada = renta_exenta_25_anual
        fvp_aplicado = aporte_fvp
        afc_aplicado = aporte_afc
        ded_vivienda_aplicada = deduccion_intereses_vivienda
        ded_dep_aplicada = deduccion_dependientes
        ded_facturas_aplicada = deduccion_facturas

    # Renta líquida gravable
    renta_liquida_gravable = (
        ingreso_neto
        - renta_exenta_25_aplicada
        - fvp_aplicado
        - afc_aplicado
        - ded_vivienda_aplicada
        - ded_dep_aplicada
        - ded_facturas_aplicada
    )
    renta_liquida_gravable = max(0.0, renta_liquida_gravable)
    rlg_uvt = _a_uvt(renta_liquida_gravable, uvt)

    impuesto_uvt, tarifa_marginal = _tabla_renta_241(rlg_uvt)
    impuesto_cop = _a_cop(impuesto_uvt, uvt)
    tarifa_efectiva = (impuesto_cop / ingreso_bruto_total) if ingreso_bruto_total > 0 else 0.0

    return ResultadoRenta(
        ingreso_bruto_anual=ingreso_bruto_total,
        renta_exenta_25pct=renta_exenta_25_aplicada,
        aporte_pension_obligatoria=aporte_pension_obligatoria,
        aporte_salud_obligatoria=aporte_salud_obligatoria,
        aporte_fvp=fvp_aplicado,
        aporte_afc=afc_aplicado,
        deduccion_intereses_vivienda=ded_vivienda_aplicada,
        deduccion_dependientes=ded_dep_aplicada,
        deduccion_facturas_electronicas=ded_facturas_aplicada,
        renta_liquida_gravable_uvt=rlg_uvt,
        impuesto_uvt=impuesto_uvt,
        impuesto_cop=impuesto_cop,
        tarifa_efectiva=tarifa_efectiva,
        tarifa_marginal=tarifa_marginal,
        resumen={
            "ingreso_bruto_anual_cop": f"${ingreso_bruto_total:,.0f}",
            "ingreso_bruto_anual_uvt": f"{_a_uvt(ingreso_bruto_total, uvt):.1f} UVT",
            "deducciones_y_exenciones_cop": f"${beneficios_acumulados:,.0f}",
            "renta_liquida_gravable_cop": f"${renta_liquida_gravable:,.0f}",
            "renta_liquida_gravable_uvt": f"{rlg_uvt:.1f} UVT",
            "impuesto_renta_cop": f"${impuesto_cop:,.0f}",
            "tarifa_marginal": f"{tarifa_marginal * 100:.0f}%",
            "tarifa_efectiva": f"{tarifa_efectiva * 100:.2f}%",
            "uvt_usado": f"${uvt:,.0f}",
        },
    )


# ── Calculadora 2: Impuesto a Dividendos ────────────────────────────────────

def calcular_impuesto_dividendos(
    dividendos_no_gravados: float,   # Art. 49 num. 3 — utilidades no gravadas en la soc.
    dividendos_gravados: float = 0.0,  # Art. 49 par. 2 — utilidades gravadas en la soc.
    otras_rentas_cedula_general_uvt: float = 0.0,  # RLG cédula general ya calculada
    uvt: float = UVT_VIGENTE,
) -> ResultadoDividendos:
    """
    Tributación de dividendos — persona natural residente.
    Art. 242 ET modificado por Ley 2277/2022.

    Tras la reforma:
    - Dividendos no gravados se SUMAN a la cédula general → tabla Art. 241.
    - Descuento Art. 254-1: 19% sobre dividendos > 1.090 UVT.
    - Dividendos gravados en sociedad: 35% en cabeza sociedad, luego suman a 241.
    - Retención sobre dividendos no gravados > 1.090 UVT: 15%.
    """
    # Impuesto en cabeza de la sociedad sobre dividendos gravados
    impuesto_35_sociedad = dividendos_gravados * 0.35
    dividendos_gravados_netos = dividendos_gravados - impuesto_35_sociedad

    # Base que entra a tabla 241 (dividendos no gravados + netos de gravados)
    base_tabla_241 = dividendos_no_gravados + dividendos_gravados_netos
    base_total_uvt = _a_uvt(base_tabla_241, uvt) + otras_rentas_cedula_general_uvt

    # Impuesto sobre base total con dividendos incluidos (tabla 241)
    impuesto_con_dividendos_uvt, tarifa_marginal = _tabla_renta_241(base_total_uvt)

    # Impuesto sin dividendos (para aislar impuesto atribuible a dividendos)
    impuesto_sin_dividendos_uvt, _ = _tabla_renta_241(otras_rentas_cedula_general_uvt)
    impuesto_dividendos_uvt = impuesto_con_dividendos_uvt - impuesto_sin_dividendos_uvt
    impuesto_dividendos_cop = _a_cop(impuesto_dividendos_uvt, uvt)

    # Descuento Art. 254-1: 19% sobre dividendos no gravados > 1.090 UVT
    dividendos_no_grav_uvt = _a_uvt(dividendos_no_gravados, uvt)
    exceso_1090 = max(0.0, dividendos_no_grav_uvt - 1_090)
    descuento_254_1_uvt = exceso_1090 * 0.19
    descuento_254_1_cop = _a_cop(descuento_254_1_uvt, uvt)

    impuesto_neto = max(0.0, impuesto_dividendos_cop - descuento_254_1_cop)
    tarifa_efectiva = (impuesto_neto / (dividendos_no_gravados + dividendos_gravados)) if (dividendos_no_gravados + dividendos_gravados) > 0 else 0.0

    return ResultadoDividendos(
        dividendos_no_gravados=dividendos_no_gravados,
        dividendos_gravados_sociedad=dividendos_gravados,
        impuesto_35_gravados=impuesto_35_sociedad,
        base_tabla_241=base_tabla_241,
        base_tabla_241_uvt=base_total_uvt,
        impuesto_tabla_241=impuesto_dividendos_cop,
        descuento_art_254_1=descuento_254_1_cop,
        impuesto_neto=impuesto_neto,
        tarifa_efectiva=tarifa_efectiva,
        resumen={
            "dividendos_no_gravados": f"${dividendos_no_gravados:,.0f}",
            "dividendos_no_gravados_uvt": f"{_a_uvt(dividendos_no_gravados, uvt):.1f} UVT",
            "impuesto_35_en_sociedad": f"${impuesto_35_sociedad:,.0f}",
            "impuesto_tabla_241": f"${impuesto_dividendos_cop:,.0f}",
            "descuento_art_254_1": f"${descuento_254_1_cop:,.0f}",
            "impuesto_neto_dividendos": f"${impuesto_neto:,.0f}",
            "tarifa_efectiva": f"{tarifa_efectiva * 100:.2f}%",
            "retencion_fuente_aplicable": f"15% sobre exceso de 1.090 UVT en dividendos no gravados",
        },
    )


# ── Calculadora 3: Ganancia Ocasional ───────────────────────────────────────

def calcular_ganancia_ocasional(
    precio_venta: float,
    costo_fiscal_original: float,
    tipo_activo: str = "acciones",   # "acciones", "inmueble", "casa_habitacion", "otro"
    aplica_ajuste_art70: bool = False,
    porcentaje_ajuste_art70: float = 0.0,   # % de inflación acumulada (IPC DANE)
    uvt: float = UVT_VIGENTE,
) -> ResultadoGananciaOcasional:
    """
    Ganancias ocasionales — Art. 300-317 ET.
    Tarifa: 15% (Ley 2277/2022 subió de 10% a 15%).
    Exención casa de habitación: primeras 5.000 UVT (antes 7.500 UVT).

    Art. 70 ET: ajuste fiscal optativo por inflación (IPC) para preservar
    poder adquisitivo del costo fiscal de activos fijos.
    """
    # Ajuste Art. 70 ET (opcional)
    ajuste_inflacion = costo_fiscal_original * porcentaje_ajuste_art70 / 100 if aplica_ajuste_art70 else 0.0
    costo_fiscal_ajustado = costo_fiscal_original + ajuste_inflacion

    ganancia_bruta = max(0.0, precio_venta - costo_fiscal_ajustado)

    # Exención casa de habitación: Art. 311-1 ET (Ley 2277/2022 redujo a 5.000 UVT)
    exencion_cop = 0.0
    if tipo_activo == "casa_habitacion":
        exencion_cop = min(ganancia_bruta, _a_cop(5_000, uvt))

    ganancia_gravable = max(0.0, ganancia_bruta - exencion_cop)
    tarifa = 0.15  # Art. 314 ET — 15% para personas naturales residentes
    impuesto = ganancia_gravable * tarifa

    return ResultadoGananciaOcasional(
        precio_venta=precio_venta,
        costo_fiscal=costo_fiscal_ajustado,
        ajuste_inflacion_art70=ajuste_inflacion,
        ganancia_bruta=ganancia_bruta,
        exencion_casa_habitacion=exencion_cop,
        ganancia_gravable=ganancia_gravable,
        impuesto=impuesto,
        tarifa=tarifa,
        resumen={
            "precio_venta": f"${precio_venta:,.0f}",
            "costo_fiscal_ajustado": f"${costo_fiscal_ajustado:,.0f}",
            "ajuste_inflacion_art70": f"${ajuste_inflacion:,.0f}" if aplica_ajuste_art70 else "No aplicado",
            "ganancia_bruta": f"${ganancia_bruta:,.0f}",
            "exencion_casa_habitacion": f"${exencion_cop:,.0f} (5.000 UVT)" if exencion_cop > 0 else "N/A",
            "ganancia_gravable": f"${ganancia_gravable:,.0f}",
            "impuesto_ganancia_ocasional": f"${impuesto:,.0f}",
            "tarifa": "15% (Art. 314 ET — Ley 2277/2022)",
            "nota_acciones_bolsa": "Venta de acciones en BVC exenta si ≤3% circulación (INCR — Art. 36-1 ET)" if tipo_activo == "acciones" else "",
        },
    )


# ── Calculadora 4: Seguridad Social Independientes ──────────────────────────

def calcular_seguridad_social_independiente(
    ingreso_mensual: float,
    smlmv: float = SMLMV_VIGENTE,
) -> ResultadoSeguridadSocial:
    """
    Cotización PILA para trabajadores independientes.
    Decreto 1273/2018 y Ley 1955/2019.

    Base de cotización: 40% del ingreso bruto mensual.
    Mínimo: 1 SMLMV. Máximo: 25 SMLMV.
    Salud: 12.5% | Pensión: 16%.
    No obligado a pensión si ingreso < 1 SMLMV.
    """
    base_raw = ingreso_mensual * 0.40
    base_min = smlmv
    base_max = smlmv * 25
    base_cotizacion = max(base_min, min(base_raw, base_max))

    obliga_pension = ingreso_mensual >= smlmv
    salud_mensual = base_cotizacion * 0.125
    pension_mensual = base_cotizacion * 0.16 if obliga_pension else 0.0
    total_mensual = salud_mensual + pension_mensual

    return ResultadoSeguridadSocial(
        ingreso_mensual=ingreso_mensual,
        base_cotizacion=base_cotizacion,
        salud_mensual=salud_mensual,
        pension_mensual=pension_mensual,
        total_mensual=total_mensual,
        total_anual=total_mensual * 12,
        resumen={
            "ingreso_mensual": f"${ingreso_mensual:,.0f}",
            "base_cotizacion_40pct": f"${base_cotizacion:,.0f}",
            "salud_12_5pct": f"${salud_mensual:,.0f}/mes",
            "pension_16pct": f"${pension_mensual:,.0f}/mes" if obliga_pension else "No aplica (ingreso < 1 SMLMV)",
            "total_mensual": f"${total_mensual:,.0f}",
            "total_anual": f"${total_mensual * 12:,.0f}",
            "nota": "Base mínima: 1 SMLMV | Máxima: 25 SMLMV. Deducible en renta.",
        },
    )


# ── Calculadora 5: Ingresos del Exterior ─────────────────────────────────────

def calcular_impuesto_ingresos_exterior(
    ingreso_bruto_exterior: float,
    tipo_ingreso: str = "dividendos",   # "dividendos", "portafolio_renta_variable",
                                         # "portafolio_renta_fija", "servicios", "otro"
    pais_origen: str = "no_paraiso",    # "no_paraiso" o "paraiso_fiscal"
    impuesto_pagado_exterior: float = 0.0,  # Para descuento Art. 254 ET
    uvt: float = UVT_VIGENTE,
) -> ResultadoExterior:
    """
    Tributación de ingresos del exterior para residentes colombianos.
    Arts. 9, 245, 18-1, 254, 408 ET.

    - Residentes tributan sobre renta mundial (Art. 9 ET).
    - Dividendos no residentes al emisor: 20% (Art. 245, Ley 2277/2022).
    - Capital de portafolio renta variable: 14% (no paraíso) o 25% (paraíso fiscal).
    - Capital de portafolio renta fija: 5%.
    - Descuento por impuesto pagado en el exterior: Art. 254 ET.
    """
    tarifas = {
        "dividendos": {"no_paraiso": 0.20, "paraiso_fiscal": 0.20},
        "portafolio_renta_variable": {"no_paraiso": 0.14, "paraiso_fiscal": 0.25},
        "portafolio_renta_fija": {"no_paraiso": 0.05, "paraiso_fiscal": 0.25},
        "servicios": {"no_paraiso": 0.15, "paraiso_fiscal": 0.33},
        "otro": {"no_paraiso": 0.35, "paraiso_fiscal": 0.35},
    }

    tarifa = tarifas.get(tipo_ingreso, tarifas["otro"]).get(pais_origen, 0.35)
    retencion_colombia = ingreso_bruto_exterior * tarifa

    # Descuento por impuesto pagado en el exterior (Art. 254 ET)
    # Tope: tarifa nominal en Colombia sobre el mismo ingreso
    credito_maximo = retencion_colombia
    credito_exterior = min(impuesto_pagado_exterior, credito_maximo)
    impuesto_neto = max(0.0, retencion_colombia - credito_exterior)

    nombres_tipo = {
        "dividendos": "Dividendos de empresa extranjera",
        "portafolio_renta_variable": "Inversión de capital — renta variable (Art. 18-1 ET)",
        "portafolio_renta_fija": "Inversión de capital — renta fija (Art. 18-1 ET)",
        "servicios": "Servicios prestados desde Colombia al exterior",
        "otro": "Otros rendimientos o ingresos del exterior",
    }

    return ResultadoExterior(
        ingreso_bruto_exterior=ingreso_bruto_exterior,
        tipo_ingreso=nombres_tipo.get(tipo_ingreso, tipo_ingreso),
        tarifa_retencion=tarifa,
        retencion_cop=retencion_colombia,
        credito_impuesto_exterior=credito_exterior,
        impuesto_neto_colombia=impuesto_neto,
        resumen={
            "ingreso_bruto": f"${ingreso_bruto_exterior:,.0f}",
            "tipo_ingreso": nombres_tipo.get(tipo_ingreso, tipo_ingreso),
            "pais_origen": pais_origen.replace("_", " ").title(),
            "tarifa_colombia": f"{tarifa * 100:.0f}%",
            "impuesto_colombia": f"${retencion_colombia:,.0f}",
            "credito_impuesto_exterior": f"${credito_exterior:,.0f}",
            "impuesto_neto_a_pagar": f"${impuesto_neto:,.0f}",
            "nota": "Como residente colombiano tributa sobre renta mundial (Art. 9 ET). Use el descuento Art. 254 ET para evitar doble tributación.",
        },
    )


# ── Calculadora 6: Análisis de Tasa Marginal y Optimización ─────────────────

def analizar_tarifa_marginal(
    ingreso_anual: float,
    uvt: float = UVT_VIGENTE,
) -> dict:
    """
    Diagnóstico de en qué tramo marginal está el contribuyente
    y cuánto ahorra cada peso adicional en exenciones/deducciones.
    """
    base_uvt = _a_uvt(ingreso_anual, uvt)
    _, tarifa_marginal = _tabla_renta_241(base_uvt)

    tramos = [
        (0, 1_090, 0.0, "0% — Sin impuesto"),
        (1_090, 1_700, 0.19, "19% — Primer tramo gravable"),
        (1_700, 4_100, 0.28, "28%"),
        (4_100, 8_670, 0.33, "33%"),
        (8_670, 18_970, 0.35, "35%"),
        (18_970, 31_000, 0.37, "37%"),
        (31_000, float("inf"), 0.39, "39% — Tarifa máxima"),
    ]

    tramo_actual = next(
        (desc for lo, hi, t, desc in tramos if lo < base_uvt <= hi or (lo == 0 and base_uvt == 0)),
        "No determinado",
    )

    ahorro_por_peso_deduccion = tarifa_marginal
    ahorro_por_millon = tarifa_marginal * 1_000_000

    # Umbral del siguiente tramo
    siguiente_tramo_uvt = None
    for lo, hi, t, desc in tramos:
        if lo < base_uvt <= hi:
            siguiente_tramo_uvt = hi
            break

    distancia_siguiente_tramo = None
    if siguiente_tramo_uvt and siguiente_tramo_uvt != float("inf"):
        distancia_siguiente_tramo = (_a_cop(siguiente_tramo_uvt, uvt) - ingreso_anual)

    return {
        "ingreso_anual_cop": f"${ingreso_anual:,.0f}",
        "ingreso_anual_uvt": f"{base_uvt:.1f} UVT",
        "tarifa_marginal": f"{tarifa_marginal * 100:.0f}%",
        "tramo_actual": tramo_actual,
        "ahorro_por_cada_peso_en_exenciones": f"${ahorro_por_peso_deduccion:.2f}",
        "ahorro_por_millon_en_fvp_o_afc": f"${ahorro_por_millon:,.0f}",
        "distancia_al_siguiente_tramo": f"${distancia_siguiente_tramo:,.0f}" if distancia_siguiente_tramo else "Ya en el tramo máximo o sin siguiente",
        "recomendacion_clave": (
            f"Con tarifa marginal del {tarifa_marginal*100:.0f}%, cada $1.000.000 que "
            f"destines a FVP o AFC te ahorra ${ahorro_por_millon:,.0f} en impuesto de renta."
        ),
    }


# ── Calculadora 7: Simulador de Vehículos de Inversión ──────────────────────

def comparar_vehiculos_inversion(
    monto_a_invertir: float,
    horizonte_anios: int = 5,
    rentabilidad_esperada_anual: float = 0.10,
    tarifa_marginal: float = 0.33,
    uvt: float = UVT_VIGENTE,
) -> dict:
    """
    Compara el impacto tributario de diferentes vehículos de inversión:
    1. Cuenta de ahorros / CDT (gravado anualmente)
    2. Fondo de Inversión Colectiva — FIC (diferimiento)
    3. Fondo Voluntario de Pensión — FVP (exento al aportar + diferimiento)
    4. Acciones BVC (INCR si ≤3% circulación)
    5. AFC (exento al aportar)
    """
    def capitalizar(capital, tasa, n):
        return capital * ((1 + tasa) ** n)

    # 1. CDT / cuenta gravada anualmente
    capital_cdt = monto_a_invertir
    for _ in range(horizonte_anios):
        rendimiento = capital_cdt * rentabilidad_esperada_anual
        rendimiento_neto = rendimiento * (1 - tarifa_marginal)
        capital_cdt += rendimiento_neto

    # 2. FIC — diferimiento (impuesto solo al retirar)
    capital_fic_bruto = capitalizar(monto_a_invertir, rentabilidad_esperada_anual, horizonte_anios)
    ganancia_fic = capital_fic_bruto - monto_a_invertir
    impuesto_fic = ganancia_fic * tarifa_marginal
    capital_fic_neto = capital_fic_bruto - impuesto_fic

    # 3. FVP — exención al aportar + diferimiento
    ahorro_fiscal_aporte = monto_a_invertir * tarifa_marginal
    capital_invertido_real_fvp = monto_a_invertir + ahorro_fiscal_aporte
    capital_fvp_bruto = capitalizar(capital_invertido_real_fvp, rentabilidad_esperada_anual, horizonte_anios)
    ganancia_fvp = capital_fvp_bruto - capital_invertido_real_fvp
    impuesto_fvp = ganancia_fvp * tarifa_marginal   # Tributa al retirar
    capital_fvp_neto = capital_fvp_bruto - impuesto_fvp

    # 4. Acciones BVC (INCR — sin impuesto si ≤3% circulación)
    capital_acciones = capitalizar(monto_a_invertir, rentabilidad_esperada_anual, horizonte_anios)
    # Solo si luego distribuyen dividendos habría tributación

    # 5. AFC — similar a FVP
    capital_afc_neto = capital_fvp_neto  # Mismo mecanismo fiscal

    return {
        "monto_invertido": f"${monto_a_invertir:,.0f}",
        "horizonte": f"{horizonte_anios} años",
        "rentabilidad_esperada": f"{rentabilidad_esperada_anual*100:.1f}% anual",
        "tarifa_marginal_aplicada": f"{tarifa_marginal*100:.0f}%",
        "resultados": {
            "CDT / cuenta gravada anualmente": f"${capital_cdt:,.0f}",
            "FIC (diferimiento al retiro)": f"${capital_fic_neto:,.0f}",
            "FVP (exención + diferimiento)": f"${capital_fvp_neto:,.0f}",
            "Acciones BVC (INCR ≤3% circulación)": f"${capital_acciones:,.0f}",
            "AFC (exención + diferimiento)": f"${capital_afc_neto:,.0f}",
        },
        "ganador_tributario": "FVP o AFC (mayor capital neto por exención al aportar y diferimiento)",
        "nota_acciones": "Las acciones en BVC generan la mayor acumulación bruta, pero los dividendos tributan. Estrategia óptima: reinversión sin distribución.",
        "nota_fic": "El FIC supera al CDT por el diferimiento del impuesto (interés compuesto sobre la porción fiscal no pagada cada año).",
    }
