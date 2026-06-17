import { useEffect, useRef } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { X, Check } from "lucide-react";

gsap.registerPlugin(ScrollTrigger);

const G = "#b8860b";

const CONTRASTS = [
  {
    industry: "CDTs que gravan tus rendimientos cada año sin diferimiento.",
    ours:     "FVP y AFC: exención inmediata al aportar + interés compuesto sobre la porción fiscal diferida.",
  },
  {
    industry: "Dividendos distribuidos sin planificación que escalan la tarifa marginal.",
    ours:     "Controlar el monto anual de dividendos para mantenerse en tramos bajos de la tabla Art. 241.",
  },
  {
    industry: "Bases PILA subvaloradas que atraen requerimientos de la UGPP.",
    ours:     "Cotizar correctamente: la UGPP cruza con DIAN. El aporte es deducible y protege tu historial.",
  },
  {
    industry: "Vender inmuebles sin ajustar el costo fiscal primero.",
    ours:     "Aplicar Art. 70/73 ET antes de vender: reduce la ganancia ocasional gravable legalmente.",
  },
];

export default function Philosophy() {
  const sectionRef = useRef(null);
  const titleRef   = useRef(null);
  const itemsRef   = useRef([]);

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.fromTo(titleRef.current, { opacity: 0, y: 40 }, {
        opacity: 1, y: 0, duration: 1, ease: "power3.out",
        scrollTrigger: { trigger: titleRef.current, start: "top 80%" },
      });
      itemsRef.current.forEach((el, i) => {
        gsap.fromTo(el, { opacity: 0, x: -30 }, {
          opacity: 1, x: 0, duration: 0.7, ease: "power3.out", delay: i * 0.1,
          scrollTrigger: { trigger: el, start: "top 88%" },
        });
      });
    }, sectionRef);
    return () => ctx.revert();
  }, []);

  return (
    <section id="filosofía" ref={sectionRef} className="relative py-32 px-6 md:px-16 overflow-hidden">
      {/* Fondo */}
      <div className="absolute inset-0 z-0">
        <img
          src="https://images.unsplash.com/photo-1618005198919-d3d4b5a92ead?w=1600&q=70&auto=format&fit=crop"
          alt="" className="w-full h-full object-cover"
          style={{ filter: "brightness(0.05) saturate(0)", transform: "scale(1.08)" }}
        />
        <div className="absolute inset-0" style={{ background: "linear-gradient(to bottom, #000000, transparent, #000000)" }} />
      </div>

      <div className="relative z-10 max-w-5xl mx-auto">
        <div ref={titleRef} className="mb-16" style={{ opacity: 0 }}>
          <div className="font-jetbrains text-[0.68rem] tracking-[0.12em] uppercase mb-4" style={{ color: G }}>
            Filosofía
          </div>
          <h2 className="font-inter font-semibold text-white leading-tight" style={{ fontSize: "clamp(1.8rem,4vw,3rem)" }}>
            La diferencia entre<br />
            <span className="font-playfair italic" style={{ color: G }}>pagar e invertir.</span>
          </h2>
          <p className="font-inter text-base mt-5 max-w-md leading-relaxed" style={{ color: "#555555" }}>
            La industria te da un producto. Aquí recibes una estrategia basada en el Estatuto Tributario real.
          </p>
        </div>

        <div className="space-y-4">
          {CONTRASTS.map((c, i) => (
            <div key={i} ref={el => (itemsRef.current[i] = el)} className="grid md:grid-cols-2 gap-4" style={{ opacity: 0 }}>
              <div className="flex gap-3 rounded-[1.5rem] border px-5 py-4"
                style={{ background: "#0f0505", borderColor: "#2a1010" }}>
                <X size={14} className="shrink-0 mt-0.5" style={{ color: "#7a3030" }} />
                <p className="font-inter text-[0.82rem] leading-relaxed" style={{ color: "#664444" }}>{c.industry}</p>
              </div>
              <div className="flex gap-3 rounded-[1.5rem] border px-5 py-4"
                style={{ background: "#050f05", borderColor: "#0a2a0a" }}>
                <Check size={14} className="shrink-0 mt-0.5" style={{ color: "#3a7a3a" }} />
                <p className="font-inter text-[0.82rem] leading-relaxed" style={{ color: "#4a7a4a" }}>{c.ours}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
