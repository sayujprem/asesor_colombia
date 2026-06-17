import { useEffect, useRef } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

const G = "#b8860b";

const STEPS = [
  {
    num: "01", accent: "#b8860b",
    title: "Diagnóstico de base gravable",
    body: "Identificamos tus fuentes de ingreso (laboral, honorarios, capital, dividendos, exterior) y calculamos tu renta líquida gravable real con la tabla Art. 241 ET.",
    svg: (
      <svg viewBox="0 0 120 60" className="w-full h-12" style={{ opacity: 0.25 }}>
        <polyline points="0,50 20,35 40,40 60,20 80,28 100,10 120,15"
          fill="none" stroke="#b8860b" strokeWidth="1.5" strokeLinecap="round" />
        <circle cx="60" cy="20" r="3" fill="#b8860b" />
        <circle cx="100" cy="10" r="3" fill="#b8860b" />
      </svg>
    ),
  },
  {
    num: "02", accent: "#888888",
    title: "Análisis de tarifa marginal",
    body: "Determinamos en qué tramo de la tabla estás (0%-39%) y cuánto ahorras por cada peso que destinas a FVP, AFC o deducciones permitidas.",
    svg: (
      <svg viewBox="0 0 120 60" className="w-full h-12" style={{ opacity: 0.25 }}>
        {[10,18,28,40,48,54,58].map((h, i) => (
          <rect key={i} x={i * 18} y={60 - h} width="14" height={h} fill="#888888" rx="2" opacity={0.4 + i * 0.09} />
        ))}
        <text x="95" y="12" fill="#888888" fontSize="8" fontFamily="monospace">39%</text>
      </svg>
    ),
  },
  {
    num: "03", accent: "#b8860b",
    title: "Optimización de vehículos",
    body: "Comparamos FVP, AFC, FIC, acciones BVC y CDTs en capital neto a 5 y 10 años, con tus ingresos y tarifa marginal real como variables.",
    svg: (
      <svg viewBox="0 0 120 60" className="w-full h-12" style={{ opacity: 0.25 }}>
        <circle cx="20" cy="30" r="18" fill="none" stroke="#b8860b" strokeWidth="1" />
        <circle cx="60" cy="30" r="14" fill="none" stroke="#888888" strokeWidth="1" />
        <circle cx="95" cy="30" r="10" fill="none" stroke="#666666" strokeWidth="1" />
        <line x1="38" y1="30" x2="46" y2="30" stroke="#b8860b" strokeWidth="0.8" />
        <line x1="74" y1="30" x2="85" y2="30" stroke="#888888" strokeWidth="0.8" />
      </svg>
    ),
  },
  {
    num: "04", accent: "#ffffff",
    title: "Estrategia fiscal anual",
    body: "Diseñamos el protocolo de cierre del año gravable: cuándo distribuir dividendos, cuándo aportar al FVP, cuándo vender activos para optimizar la base.",
    svg: (
      <svg viewBox="0 0 120 60" className="w-full h-12" style={{ opacity: 0.2 }}>
        {["Ene","Mar","May","Ago","Dic"].map((m, i) => (
          <g key={m}>
            <circle cx={12 + i * 24} cy="30" r="6"
              fill={i < 2 ? "#ffffff" : "none"} stroke="#ffffff" strokeWidth="1" />
            {i < 4 && <line x1={18 + i*24} y1="30" x2={30 + i*24} y2="30"
              stroke="#ffffff" strokeWidth="0.8" strokeDasharray={i >= 2 ? "3,2" : undefined} />}
            <text x={9 + i * 24} y="52" fill="#ffffff" fontSize="6" fontFamily="monospace">{m}</text>
          </g>
        ))}
      </svg>
    ),
  },
];

export default function Protocol() {
  const sectionRef = useRef(null);
  const cardsRef   = useRef([]);

  useEffect(() => {
    const ctx = gsap.context(() => {
      cardsRef.current.forEach((card, i) => {
        gsap.fromTo(card, { opacity: 0, scale: 0.95, y: 40 }, {
          opacity: 1, scale: 1, y: 0, duration: 0.9, ease: "power3.out",
          scrollTrigger: { trigger: card, start: "top 82%", toggleActions: "play none none none" },
        });
      });
    }, sectionRef);
    return () => ctx.revert();
  }, []);

  return (
    <section id="protocolo" ref={sectionRef} className="py-32 px-6 md:px-16" style={{ background: "#050505" }}>
      <div className="max-w-6xl mx-auto">
        <div className="mb-16">
          <div className="font-jetbrains text-[0.68rem] tracking-[0.12em] uppercase mb-4" style={{ color: G }}>
            Protocolo
          </div>
          <h2 className="font-inter font-semibold text-white" style={{ fontSize: "clamp(1.8rem,4vw,3rem)" }}>
            De la consulta a la{" "}
            <span className="font-playfair italic" style={{ color: G }}>estrategia.</span>
          </h2>
        </div>

        <div className="grid md:grid-cols-2 gap-5">
          {STEPS.map((step, i) => (
            <div key={i} ref={el => (cardsRef.current[i] = el)}
              className="relative rounded-[2rem] border overflow-hidden p-8 transition-colors duration-300"
              style={{ background: "#0a0a0a", borderColor: "#1a1a1a", opacity: 0 }}
              onMouseEnter={e => (e.currentTarget.style.borderColor = "#b8860b22")}
              onMouseLeave={e => (e.currentTarget.style.borderColor = "#1a1a1a")}
            >
              {/* Número decorativo */}
              <div className="absolute -right-3 -top-3 font-inter font-bold select-none pointer-events-none"
                style={{ fontSize: "7rem", lineHeight: 1, color: `${step.accent}06` }}>
                {step.num}
              </div>

              <div className="relative z-10">
                <div className="font-jetbrains text-[0.65rem] tracking-[0.1em] mb-5" style={{ color: step.accent }}>
                  PASO {step.num}
                </div>
                <div className="mb-5">{step.svg}</div>
                <h3 className="font-inter font-semibold text-white text-base mb-3">{step.title}</h3>
                <p className="font-inter text-[0.82rem] leading-relaxed" style={{ color: "#444444" }}>{step.body}</p>
                <div className="mt-6 h-px w-12 rounded-full" style={{ background: `${step.accent}44` }} />
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
