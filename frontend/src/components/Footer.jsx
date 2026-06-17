const G    = "#b8860b";
const DARK = "#1C1711";

export default function Footer() {
  return (
    <footer className="px-8 md:px-20 py-10" style={{ background: "#FDFBF7", borderTop: "1px solid #E8E3D9" }}>
      <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-start md:items-center justify-between gap-6">

        <div>
          <span className="text-[0.65rem] font-semibold tracking-[0.2em] uppercase" style={{ color: DARK }}>
            Asesor Colombia
          </span>
          <p className="text-[0.62rem] tracking-[0.08em] mt-1" style={{ color: "#B8B0A6" }}>
            Creado por <span style={{ color: G, fontWeight: 600 }}>Sayuj</span>
          </p>
        </div>

        <p className="text-xs leading-relaxed max-w-md text-center" style={{ color: "#B8B0A6", letterSpacing: "0.02em" }}>
          Orientación informativa. No constituye asesoría jurídica, tributaria ni de inversión.
          Consulta siempre a un contador público o abogado tributarista.
        </p>

        <div className="flex items-center gap-2">
          <div className="pulse-dot w-1.5 h-1.5 rounded-full" style={{ background: "#4ade80" }} />
          <span className="text-[0.62rem] tracking-[0.1em] uppercase" style={{ color: "#B8B0A6" }}>Sin datos guardados</span>
        </div>
      </div>
    </footer>
  );
}
