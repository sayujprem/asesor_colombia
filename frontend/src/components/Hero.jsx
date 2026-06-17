import { useEffect, useRef } from "react";
import { gsap } from "gsap";

const G = "#b8860b";
const DARK = "#1C1711";
const MUTED = "#8A8075";

export default function Hero({ onOpenChat }) {
  const ref = useRef(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.fromTo(
        ref.current.querySelectorAll("[data-anim]"),
        { opacity: 0, y: 32 },
        { opacity: 1, y: 0, duration: 1, ease: "power3.out", stagger: 0.14, delay: 0.1 }
      );
    }, ref);
    return () => ctx.revert();
  }, []);

  return (
    <section
      ref={ref}
      className="min-h-[100dvh] flex flex-col justify-center px-8 md:px-20 pt-24 pb-20"
      style={{ background: "#FDFBF7" }}
    >
      <div className="max-w-4xl">
        {/* Overline */}
        <p
          data-anim
          className="text-[0.65rem] font-semibold tracking-[0.22em] uppercase mb-10"
          style={{ color: G, opacity: 0 }}
        >
          Asesor Colombia — Tributario &amp; Inversiones
        </p>

        {/* Headline */}
        <h1
          data-anim
          className="font-bold leading-[1.02] tracking-[-0.02em] mb-10"
          style={{ fontSize: "clamp(3rem, 7.5vw, 6.2rem)", color: DARK, opacity: 0 }}
        >
          La estrategia fiscal<br />
          que merece tu<br />
          <span style={{ color: G }}>patrimonio.</span>
        </h1>

        {/* Thin rule */}
        <div data-anim className="w-12 h-px mb-8" style={{ background: G, opacity: 0 }} />

        {/* Body */}
        <p
          data-anim
          className="text-base leading-[1.8] mb-12 max-w-md"
          style={{ color: MUTED, opacity: 0, letterSpacing: "0.01em" }}
        >
          Consulta sobre impuesto de renta, dividendos, ganancias ocasionales,
          seguridad social y vehículos de inversión — basado en el Estatuto
          Tributario vigente de Colombia.
        </p>

        {/* CTA */}
        <div data-anim style={{ opacity: 0 }}>
          <button
            onClick={onOpenChat}
            className="btn-magnetic inline-flex items-center gap-3 font-semibold text-sm tracking-[0.06em] uppercase px-10 py-4 rounded-none border"
            style={{ borderColor: DARK, color: DARK, letterSpacing: "0.08em" }}
          >
            <div className="btn-fill" style={{ background: DARK }} />
            <span className="btn-label">Consultar ahora</span>
            <span className="btn-label" style={{ fontSize: "1rem" }}>→</span>
          </button>
        </div>

        {/* Caption */}
        <p data-anim className="mt-6 text-xs" style={{ color: "#B8B0A6", opacity: 0, letterSpacing: "0.04em" }}>
          Las calculadoras tributarias se activan automáticamente dentro de la consulta.
        </p>
      </div>
    </section>
  );
}
