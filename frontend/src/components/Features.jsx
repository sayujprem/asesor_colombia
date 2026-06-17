import { useEffect, useRef } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

const G    = "#b8860b";
const DARK = "#1C1711";
const MUTED = "#8A8075";

const TOOLS = [
  { num: "01", title: "Impuesto de renta",       body: "Tabla progresiva Art. 241 ET. Exención 25% laboral, FVP y AFC incluidos." },
  { num: "02", title: "Dividendos",               body: "Art. 242 ET (Ley 2277/2022). Integración cédula general y descuento Art. 254-1." },
  { num: "03", title: "Ganancia ocasional",        body: "Art. 314 ET, tarifa 15%. Ajuste costo fiscal Art. 70/73 y exención casa habitación." },
  { num: "04", title: "Seguridad social PILA",    body: "Independientes: base 40% del ingreso. Salud 12.5% + Pensión 16%. Cruce UGPP." },
  { num: "05", title: "Ingresos del exterior",    body: "Renta mundial Art. 9 ET. Descuento impuesto pagado en el exterior Art. 254." },
  { num: "06", title: "Vehículos de inversión",   body: "FVP, AFC, FIC, acciones BVC y CDT: comparación de capital neto tras impuestos." },
];

export default function Features({ onOpenChat }) {
  const sectionRef = useRef(null);
  const cardsRef   = useRef([]);

  useEffect(() => {
    const ctx = gsap.context(() => {
      cardsRef.current.forEach((card, i) => {
        if (!card) return;
        gsap.fromTo(card,
          { opacity: 0, y: 20 },
          {
            opacity: 1, y: 0, duration: 0.75, ease: "power3.out",
            scrollTrigger: { trigger: card, start: "top 90%", toggleActions: "play none none none" },
            delay: (i % 3) * 0.07,
          }
        );
      });
    }, sectionRef);
    return () => ctx.revert();
  }, []);

  return (
    <section id="herramientas" ref={sectionRef} className="py-28 px-8 md:px-20" style={{ background: "#F5F1EB" }}>
      <div className="max-w-6xl mx-auto">

        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-8 mb-16">
          <div>
            <p className="text-[0.65rem] font-semibold tracking-[0.22em] uppercase mb-5" style={{ color: G }}>
              Calculadoras integradas
            </p>
            <h2 className="font-bold tracking-tight leading-[1.05]" style={{ fontSize: "clamp(1.8rem,3.5vw,2.8rem)", color: DARK }}>
              No hay pasos adicionales.<br />Consulta en lenguaje natural.
            </h2>
          </div>
          <p className="text-sm leading-relaxed max-w-xs" style={{ color: MUTED, letterSpacing: "0.01em" }}>
            El asesor identifica qué calcular y lo ejecuta automáticamente — sin que tengas que activar nada.
          </p>
        </div>

        {/* Grid */}
        <div className="grid md:grid-cols-3 gap-px" style={{ background: "#E8E3D9" }}>
          {TOOLS.map((tool, i) => (
            <div
              key={i}
              ref={el => (cardsRef.current[i] = el)}
              className="p-8 transition-colors duration-250"
              style={{ background: "#F5F1EB", opacity: 0 }}
              onMouseEnter={e => (e.currentTarget.style.background = "#FDFBF7")}
              onMouseLeave={e => (e.currentTarget.style.background = "#F5F1EB")}
            >
              <span className="block text-[0.62rem] font-semibold tracking-[0.18em] uppercase mb-5" style={{ color: G }}>
                {tool.num}
              </span>
              <h3 className="font-semibold text-sm mb-3 leading-tight" style={{ color: DARK }}>{tool.title}</h3>
              <p className="text-xs leading-relaxed" style={{ color: MUTED }}>{tool.body}</p>
            </div>
          ))}
        </div>

        {/* CTA */}
        <div className="mt-16 flex justify-center">
          <button
            onClick={onOpenChat}
            className="btn-magnetic inline-flex items-center gap-3 font-semibold text-[0.65rem] tracking-[0.14em] uppercase px-10 py-4 border"
            style={{ borderColor: DARK, color: DARK, borderRadius: 0 }}
          >
            <div className="btn-fill" style={{ background: DARK }} />
            <span className="btn-label">Iniciar consulta →</span>
          </button>
        </div>
      </div>
    </section>
  );
}
