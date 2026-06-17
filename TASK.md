# Asesor_Colombia — Asesor Tributario y de Inversiones

## Descripción
Chatbot de asesoría financiera, contable, tributaria y de inversiones para Colombia. Usa Claude como
motor de razonamiento y el Estatuto Tributario (ET) + Ley 2277/2022 como base de conocimiento.
Incluye calculadoras tributarias reales: renta, dividendos, ganancias ocasionales, seguridad social
e ingresos del exterior. Asesora sobre asset allocation, vehículos de inversión y optimización fiscal.

## Cuándo usar este script
- "¿Cuánto pago de renta?"
- "¿Cómo bajo mi tarifa marginal?"
- "¿Cuánto pago si vendo mis acciones / mi inmueble?"
- "¿Me conviene FVP o AFC?"
- "Tengo dividendos de mi empresa, ¿cuánto pago?"
- "Tengo ingresos del exterior, ¿cómo tributo?"
- "¿Cuánto debo cotizar a la UGPP?"
- "¿Cómo optimizo mi portafolio para pagar menos a la DIAN?"
- Cualquier consulta de planificación fiscal, inversiones o tributos colombianos.

## Prerequisitos
- Variable de entorno: `ANTHROPIC_API_KEY` en el archivo `.env`
- Python 3.11+
- Dependencias instaladas: `pip install -r requirements.txt`

## Cómo ejecutar

### Ejecución básica (con banner)
```bash
cd asesor/
python main.py
```

### Modo rápido (sin banner)
```bash
python main.py --modo rapido
```

### Modo debug (muestra herramientas y tokens)
```bash
python main.py --debug
```

### Todos los parámetros
| Parámetro | Opciones | Default | Descripción |
|---|---|---|---|
| `--modo` | `completo`, `rapido` | `completo` | Con o sin banner de bienvenida |
| `--debug` | flag | False | Muestra herramientas usadas, tokens y resultados raw |

## Output esperado
Sesión interactiva de chat en terminal. El asesor responde en lenguaje natural con:
- Explicaciones legales con referencia a artículos del ET.
- Cálculos exactos usando las calculadoras tributarias.
- Estrategias de optimización proactivas.
- Alertas sobre UGPP, DIAN, topes y plazos.

## Calculadoras disponibles (activadas automáticamente por Claude)
| Calculadora | Qué calcula |
|---|---|
| `calcular_renta` | Impuesto renta personas naturales (Art. 241 ET) |
| `calcular_dividendos` | Impuesto dividendos (Art. 242 ET, Ley 2277/2022) |
| `calcular_ganancia_ocasional` | GO en venta activos, inmuebles (Art. 314 ET, 15%) |
| `calcular_seguridad_social` | PILA independientes (salud 12.5% + pensión 16%) |
| `calcular_ingresos_exterior` | Renta mundial, CDT, descuento Art. 254 ET |
| `analizar_tarifa_marginal` | Diagnóstico tramo marginal y ahorro por FVP/AFC |
| `comparar_vehiculos_inversion` | CDT vs FIC vs FVP vs Acciones BVC vs AFC |

## Errores comunes y soluciones
| Error | Causa | Solución |
|---|---|---|
| `ANTHROPIC_API_KEY not found` | Falta .env | Crear `.env` con la clave de Anthropic |
| `ModuleNotFoundError: anthropic` | Dependencias no instaladas | `pip install -r requirements.txt` |
| `AuthenticationError` | API key inválida | Verificar clave en console.anthropic.com |

## Actualización anual (obligatoria)
Cada enero, actualizar en `.env`:
- `UVT_VIGENTE`: valor del decreto DIAN (publicado en diciembre del año anterior)
- `SMLMV_VIGENTE`: valor del decreto de gobierno (publicado en diciembre)
Referencia: [DIAN - UVT](https://www.dian.gov.co/)

## Notas
- No reemplaza asesoría jurídica profesional para situaciones complejas.
- El UVT 2026 (~$52.669) es estimado; verificar decreto DIAN oficial.
- Las tarifas son las vigentes tras la Ley 2277 de 2022 (reforma tributaria más reciente).
- La DIAN participa en el sistema CRS de la OCDE: ingresos del exterior son visibles.
