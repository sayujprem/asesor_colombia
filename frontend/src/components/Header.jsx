import { useEffect, useState } from "react";

const G    = "#b8860b";
const DARK = "#1C1711";

export default function Header({ onOpenChat }) {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 50);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header
      className="fixed top-0 left-0 right-0 z-50 transition-all duration-400"
      style={{
        background: scrolled ? "rgba(253,251,247,0.96)" : "transparent",
        backdropFilter: scrolled ? "blur(20px)" : "none",
        borderBottom: scrolled ? "1px solid #E8E3D9" : "1px solid transparent",
      }}
    >
      <div className="max-w-6xl mx-auto px-8 md:px-20 h-16 flex items-center justify-between">
        {/* Brand */}
        <span
          className="text-xs font-semibold tracking-[0.2em] uppercase"
          style={{ color: DARK, letterSpacing: "0.2em" }}
        >
          Asesor Colombia
        </span>

        {/* CTA */}
        <button
          onClick={onOpenChat}
          className="btn-magnetic text-[0.65rem] font-semibold tracking-[0.14em] uppercase px-6 py-2.5 border"
          style={{ borderColor: G, color: G, borderRadius: "0" }}
        >
          <div className="btn-fill" />
          <span className="btn-label">Consultar</span>
        </button>
      </div>
    </header>
  );
}
