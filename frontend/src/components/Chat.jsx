import { useEffect, useRef, useState, useCallback } from "react";
import { gsap } from "gsap";
import { X, Send, AlertTriangle, Scale, ChevronRight } from "lucide-react";

const API_BASE = import.meta.env.VITE_API_URL || "";
const G     = "#b8860b";
const DARK  = "#1C1711";
const MUTED = "#8A8075";
const CREAM = "#FDFBF7";
const CARD  = "#F5F1EB";
const BORDE = "#E8E3D9";

const QUICK_PROMPTS = [
  "¿Cuánto pago de renta si gano $150M al año?",
  "¿Cuánto ahorro en impuestos con un FVP de $10M?",
  "Vendo un inmueble en $800M comprado en $300M",
  "¿Cuánto cotizo a la UGPP si gano $12M/mes?",
  "Recibo dividendos de $100M — ¿cuánto pago?",
  "Tengo $50M — ¿FIC, FVP o acciones en bolsa?",
  "¿Cómo bajo mi tarifa marginal del 33%?",
  "Tengo ingresos del exterior — ¿cómo tributo?",
];

function Disclaimer({ compact = false }) {
  if (compact) {
    return (
      <p className="text-[0.58rem] text-center tracking-wide" style={{ color: "#B8B0A6" }}>
        Orientación informativa · No constituye asesoría de inversión · Consulta un profesional
      </p>
    );
  }
  return (
    <div className="flex gap-3 rounded-none border px-4 py-3 mx-4 mb-2"
      style={{ background: "#FBF8F0", borderColor: "#E8D9A0", borderLeft: `2px solid ${G}` }}>
      <AlertTriangle size={13} className="shrink-0 mt-0.5" style={{ color: `${G}99` }} />
      <p className="text-[0.69rem] leading-relaxed" style={{ color: MUTED }}>
        <strong style={{ color: G }}>Aviso legal.</strong>{" "}
        Las respuestas son meramente <strong style={{ color: DARK }}>orientativas e informativas</strong>.
        No constituyen recomendaciones de inversión ni asesoría jurídica o tributaria profesional.
        Consulta siempre a un <strong style={{ color: DARK }}>contador público titulado o abogado tributarista</strong>.
      </p>
    </div>
  );
}

function formatMessage(text) {
  if (!text) return "";
  return text
    .replace(/\*\*(.+?)\*\*/g, `<strong style="color:${DARK};font-weight:600">$1</strong>`)
    .replace(/`(.+?)`/g, `<code style="font-family:monospace;background:#EDE9E1;color:${G};padding:1px 5px;border-radius:3px;font-size:0.78em">$1</code>`)
    .replace(/^###\s(.+)/gm, `<h4 style="color:${DARK};font-weight:600;font-size:0.88rem;margin:12px 0 4px">$1</h4>`)
    .replace(/^##\s(.+)/gm, `<h3 style="color:${G};font-weight:600;font-size:0.92rem;margin:14px 0 6px">$1</h3>`)
    .replace(/^-\s(.+)/gm, `<li style="margin:3px 0;padding-left:4px;color:${MUTED}">$1</li>`)
    .replace(/\n\n/g, `</p><p style="margin:8px 0">`)
    .replace(/\n/g, "<br/>");
}

function Message({ role, content, isStreaming }) {
  const isUser = role === "user";
  return (
    <div className={`msg-in flex gap-3 ${isUser ? "flex-row-reverse" : "flex-row"} items-start mb-5`}>
      {/* Avatar */}
      <div
        className="shrink-0 w-7 h-7 flex items-center justify-center border text-[0.62rem] font-semibold"
        style={isUser
          ? { background: CARD, borderColor: BORDE, color: MUTED }
          : { background: "#FBF8F0", borderColor: `${G}55`, color: G }
        }
      >
        {isUser ? "Tú" : <Scale size={12} />}
      </div>

      {/* Burbuja */}
      <div
        className="max-w-[82%] px-5 py-3.5 text-[0.84rem] leading-relaxed"
        style={isUser
          ? {
              background: CARD,
              border: `1px solid ${BORDE}`,
              color: DARK,
              borderRadius: "0 0 0 0",
            }
          : {
              background: "#FBF8F0",
              border: `1px solid #E8D9A0`,
              borderLeft: `2px solid ${G}`,
              color: DARK,
              borderRadius: "0 0 0 0",
            }
        }
      >
        {isStreaming && !content ? (
          <div className="flex gap-1 items-center py-1">
            {[0,1,2].map(i => (
              <div key={i} className="w-1.5 h-1.5 rounded-full"
                style={{ background: G, opacity: 0.5, animation: `blink 1.2s ${i * 0.2}s ease-in-out infinite` }} />
            ))}
          </div>
        ) : (
          <div dangerouslySetInnerHTML={{ __html: formatMessage(content) }} />
        )}
        {isStreaming && content && (
          <span className="cursor-blink text-xs ml-0.5" style={{ color: G }}>▋</span>
        )}
      </div>
    </div>
  );
}

export default function Chat({ isOpen, onClose }) {
  const overlayRef     = useRef(null);
  const panelRef       = useRef(null);
  const messagesEndRef = useRef(null);
  const inputRef       = useRef(null);

  const [messages,   setMessages]   = useState([]);
  const [input,      setInput]      = useState("");
  const [streaming,  setStreaming]  = useState(false);
  const [toolStatus, setToolStatus] = useState("");

  useEffect(() => {
    if (!overlayRef.current || !panelRef.current) return;
    const ctx = gsap.context(() => {
      if (isOpen) {
        gsap.set(overlayRef.current, { display: "flex" });
        gsap.fromTo(overlayRef.current, { opacity: 0 }, { opacity: 1, duration: 0.3, ease: "power2.out" });
        gsap.fromTo(panelRef.current,
          { y: 40, opacity: 0, scale: 0.98 },
          { y: 0, opacity: 1, scale: 1, duration: 0.45, ease: "power3.out" }
        );
        setTimeout(() => inputRef.current?.focus(), 500);
      } else {
        gsap.to(panelRef.current, { y: 30, opacity: 0, scale: 0.98, duration: 0.3, ease: "power2.in" });
        gsap.to(overlayRef.current, {
          opacity: 0, duration: 0.3, delay: 0.1, ease: "power2.in",
          onComplete: () => gsap.set(overlayRef.current, { display: "none" }),
        });
      }
    });
    return () => ctx.revert();
  }, [isOpen]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, toolStatus]);

  const sendMessage = useCallback(async (text) => {
    if (!text.trim() || streaming) return;

    const userMsg = { role: "user", content: text.trim() };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setStreaming(true);
    setToolStatus("");
    setMessages(prev => [...prev, { role: "assistant", content: "", isStreaming: true }]);

    try {
      const history = [...messages, userMsg]
        .map(m => ({ role: m.role === "assistant" ? "assistant" : "user", content: m.content || "" }))
        .filter(m => m.content);

      const res = await fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: history }),
      });

      const reader  = res.body.getReader();
      const decoder = new TextDecoder();
      let assistantText = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const lines = decoder.decode(value).split("\n");
        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          try {
            const evt = JSON.parse(line.slice(6));
            if (evt.type === "text_delta") {
              assistantText = evt.text;
              setMessages(prev => {
                const next = [...prev];
                next[next.length - 1] = { role: "assistant", content: assistantText, isStreaming: true };
                return next;
              });
              setToolStatus("");
            } else if (evt.type === "tool_call") {
              setToolStatus(`Calculando ${evt.tool}...`);
            } else if (evt.type === "done") {
              setMessages(prev => {
                const next = [...prev];
                next[next.length - 1] = { role: "assistant", content: assistantText, isStreaming: false };
                return next;
              });
              setToolStatus("");
            }
          } catch { /* skip */ }
        }
      }
    } catch {
      setMessages(prev => {
        const next = [...prev];
        next[next.length - 1] = {
          role: "assistant",
          content: "Error de conexión. Verifica tu conexión e intenta de nuevo.",
          isStreaming: false,
        };
        return next;
      });
    } finally {
      setStreaming(false);
      setToolStatus("");
    }
  }, [messages, streaming]);

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(input); }
  };

  return (
    <div
      ref={overlayRef}
      className="fixed inset-0 z-[1000] items-end md:items-center justify-center p-0 md:p-8"
      style={{ display: "none", background: "rgba(28,23,17,0.5)", backdropFilter: "blur(8px)" }}
      onClick={e => e.target === overlayRef.current && onClose()}
    >
      <div
        ref={panelRef}
        className="relative w-full md:max-w-2xl flex flex-col overflow-hidden"
        style={{
          height: "92dvh",
          maxHeight: "86vh",
          background: CREAM,
          border: `1px solid ${BORDE}`,
          boxShadow: "0 32px 80px rgba(28,23,17,0.18)",
        }}
      >
        {/* Header */}
        <div
          className="flex items-center justify-between px-6 py-4 shrink-0"
          style={{ borderBottom: `1px solid ${BORDE}`, background: CREAM }}
        >
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 flex items-center justify-center border"
              style={{ background: "#FBF8F0", borderColor: `${G}44` }}>
              <Scale size={13} style={{ color: G }} />
            </div>
            <div>
              <div className="text-sm font-semibold tracking-tight" style={{ color: DARK }}>
                Asesor Colombia
              </div>
              <div className="text-[0.59rem] tracking-[0.1em] uppercase" style={{ color: "#B8B0A6" }}>
                Tributario · Fiscal · Inversiones
              </div>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1.5">
              <div className="pulse-dot w-1.5 h-1.5 rounded-full" style={{ background: "#4ade80" }} />
              <span className="text-[0.58rem] tracking-[0.1em] uppercase" style={{ color: "#B8B0A6" }}>
                Sin datos guardados
              </span>
            </div>
            <button
              onClick={onClose}
              className="w-7 h-7 flex items-center justify-center border transition-colors"
              style={{ background: CARD, borderColor: BORDE }}
              onMouseEnter={e => (e.currentTarget.style.borderColor = G)}
              onMouseLeave={e => (e.currentTarget.style.borderColor = BORDE)}
            >
              <X size={13} style={{ color: MUTED }} />
            </button>
          </div>
        </div>

        {/* Disclaimer */}
        <div className="shrink-0 pt-3"><Disclaimer /></div>

        {/* Mensajes */}
        <div className="flex-1 overflow-y-auto px-5 py-4" style={{ background: CREAM }}>
          {messages.length === 0 && (
            <div className="py-4">
              <p className="text-[0.7rem] font-semibold tracking-[0.14em] uppercase mb-5" style={{ color: G }}>
                Consultas frecuentes
              </p>
              <div className="grid grid-cols-1 gap-1.5">
                {QUICK_PROMPTS.map((p, i) => (
                  <button
                    key={i}
                    onClick={() => sendMessage(p)}
                    className="flex items-center gap-2.5 text-left border px-4 py-3 transition-all duration-200"
                    style={{ background: CARD, borderColor: BORDE }}
                    onMouseEnter={e => { e.currentTarget.style.borderColor = G; e.currentTarget.style.background = "#FBF8F0"; }}
                    onMouseLeave={e => { e.currentTarget.style.borderColor = BORDE; e.currentTarget.style.background = CARD; }}
                  >
                    <ChevronRight size={11} style={{ color: `${G}88`, flexShrink: 0 }} />
                    <span className="text-[0.78rem]" style={{ color: MUTED }}>{p}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg, i) => (
            <Message key={i} role={msg.role} content={msg.content} isStreaming={msg.isStreaming} />
          ))}

          {toolStatus && (
            <div className="flex items-center gap-2.5 px-2 py-2 mb-3">
              <div className="shimmer w-3.5 h-3.5" style={{ borderRadius: 0 }} />
              <span className="text-[0.66rem] tracking-[0.08em] uppercase" style={{ color: `${G}99` }}>
                {toolStatus}
              </span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Disclaimer compacto */}
        <div className="shrink-0 px-5 py-1.5" style={{ borderTop: `1px solid ${BORDE}` }}>
          <Disclaimer compact />
        </div>

        {/* Input */}
        <div className="shrink-0 px-5 pb-5 pt-3" style={{ background: CREAM }}>
          <div
            className="flex gap-3 items-end border px-4 py-3 transition-colors"
            style={{ background: CARD, borderColor: BORDE }}
            onFocusCapture={e => (e.currentTarget.style.borderColor = G)}
            onBlurCapture={e  => (e.currentTarget.style.borderColor = BORDE)}
          >
            <textarea
              ref={inputRef}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Escribe tu consulta tributaria o de inversiones..."
              rows={1}
              className="flex-1 bg-transparent text-[0.84rem] resize-none outline-none leading-relaxed"
              style={{ maxHeight: "120px", color: DARK, caretColor: G }}
              onInput={e => {
                e.target.style.height = "auto";
                e.target.style.height = `${Math.min(e.target.scrollHeight, 120)}px`;
              }}
              disabled={streaming}
            />
            <button
              onClick={() => sendMessage(input)}
              disabled={!input.trim() || streaming}
              className="shrink-0 w-8 h-8 flex items-center justify-center transition-all duration-200 disabled:opacity-30"
              style={{ background: G, borderRadius: 0 }}
              onMouseEnter={e => !e.currentTarget.disabled && (e.currentTarget.style.background = "#a07a0a")}
              onMouseLeave={e => (e.currentTarget.style.background = G)}
            >
              <Send size={13} style={{ color: "#ffffff" }} />
            </button>
          </div>

          {/* Crédito */}
          <p className="mt-3 text-center text-[0.58rem] tracking-[0.1em] uppercase" style={{ color: "#D0C8BC" }}>
            Creado por <span style={{ color: G }}>Sayuj</span>
          </p>
        </div>
      </div>
    </div>
  );
}
