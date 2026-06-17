import { useEffect, useRef, useState, useCallback } from "react";
import { gsap } from "gsap";
import { X, Send, AlertTriangle, Scale, ChevronRight } from "lucide-react";

const API_BASE = import.meta.env.VITE_API_URL || "";
const G = "#b8860b";

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
      <p className="text-[0.58rem] text-center tracking-wide" style={{ color: "#2a2a2a" }}>
        Orientación informativa · No constituye asesoría de inversión · Consulta un profesional para decisiones financieras
      </p>
    );
  }
  return (
    <div className="flex gap-3 rounded-[1.2rem] border px-4 py-3 mx-4 mb-2"
      style={{ background: "#100a00", borderColor: "#2a1800" }}>
      <AlertTriangle size={14} className="shrink-0 mt-0.5" style={{ color: "#b8860b88" }} />
      <p className="text-[0.7rem] leading-relaxed" style={{ color: "#6a5020" }}>
        <strong style={{ color: G }}>Aviso legal.</strong>{" "}
        Las respuestas son meramente <strong>orientativas e informativas</strong>.
        No constituyen recomendaciones de inversión ni asesoría jurídica o tributaria profesional.
        Antes de tomar decisiones fiscales o de inversión, consulta siempre a un{" "}
        <strong>contador público titulado o abogado tributarista</strong>.
      </p>
    </div>
  );
}

function formatMessage(text) {
  if (!text) return "";
  return text
    .replace(/\*\*(.+?)\*\*/g, `<strong style="color:#ffffff;font-weight:600">$1</strong>`)
    .replace(/`(.+?)`/g, `<code style="font-family:monospace;background:#111111;color:${G};padding:1px 5px;border-radius:4px;font-size:0.78em">$1</code>`)
    .replace(/^###\s(.+)/gm, `<h4 style="color:#ffffff;font-weight:600;font-size:0.88rem;margin:12px 0 4px">$1</h4>`)
    .replace(/^##\s(.+)/gm, `<h3 style="color:${G};font-weight:600;font-size:0.92rem;margin:14px 0 6px">$1</h3>`)
    .replace(/^-\s(.+)/gm, `<li style="margin:3px 0;padding-left:4px">$1</li>`)
    .replace(/\n\n/g, `</p><p style="margin:8px 0">`)
    .replace(/\n/g, "<br/>");
}

function Message({ role, content, isStreaming }) {
  const isUser = role === "user";
  return (
    <div className={`msg-in flex gap-3 ${isUser ? "flex-row-reverse" : "flex-row"} items-start mb-5`}>
      <div className="shrink-0 w-7 h-7 rounded-full flex items-center justify-center border text-xs"
        style={isUser
          ? { background: "#111111", borderColor: "#222222", color: "#555555" }
          : { background: "#100a00", borderColor: `${G}33`, color: G }
        }>
        {isUser ? "Tú" : <Scale size={12} />}
      </div>

      <div className="max-w-[82%] rounded-[1.5rem] px-5 py-3.5 text-[0.84rem] leading-relaxed"
        style={isUser
          ? { background: "#111111", border: "1px solid #222222", color: "#cccccc", borderRadius: "1.5rem 0.4rem 1.5rem 1.5rem" }
          : { background: "#0a0800", border: `1px solid ${G}18`, color: "#ccbf8a", borderRadius: "0.4rem 1.5rem 1.5rem 1.5rem" }
        }>
        {isStreaming && !content ? (
          <div className="flex gap-1 items-center py-1">
            {[0,1,2].map(i => (
              <div key={i} className="w-1.5 h-1.5 rounded-full" style={{ background: G, opacity: 0.6, animation: `blink 1.2s ${i * 0.2}s ease-in-out infinite` }} />
            ))}
          </div>
        ) : (
          <div dangerouslySetInnerHTML={{ __html: formatMessage(content) }} />
        )}
        {isStreaming && content && <span className="cursor-blink text-xs ml-0.5" style={{ color: G }}>▋</span>}
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
          { y: 40, opacity: 0, scale: 0.97 },
          { y: 0, opacity: 1, scale: 1, duration: 0.45, ease: "power3.out" }
        );
        setTimeout(() => inputRef.current?.focus(), 500);
      } else {
        gsap.to(panelRef.current, { y: 30, opacity: 0, scale: 0.97, duration: 0.3, ease: "power2.in" });
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
          content: "Error de conexión. Asegúrate de que el backend esté corriendo en el puerto 8000.",
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
      className="fixed inset-0 z-[1000] items-end md:items-center justify-center p-0 md:p-6"
      style={{ display: "none", background: "rgba(0,0,0,0.7)", backdropFilter: "blur(10px)" }}
      onClick={e => e.target === overlayRef.current && onClose()}
    >
      <div
        ref={panelRef}
        className="relative w-full md:max-w-2xl flex flex-col border rounded-t-[2.5rem] md:rounded-[2.5rem] overflow-hidden"
        style={{
          height: "92dvh",
          maxHeight: "85vh",
          background: "#000000",
          borderColor: "#1a1a1a",
          boxShadow: `0 40px 100px #000000cc, 0 0 60px ${G}0a`,
        }}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 shrink-0" style={{ borderBottom: "1px solid #111111" }}>
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-full flex items-center justify-center border"
              style={{ background: "#0a0800", borderColor: `${G}33` }}>
              <Scale size={14} style={{ color: G }} />
            </div>
            <div>
              <div className="text-sm font-semibold text-white">Asesor Colombia</div>
              <div className="text-[0.6rem] tracking-wide" style={{ color: "#333333" }}>Tributario · Fiscal · Inversiones</div>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5">
              <div className="pulse-dot w-1.5 h-1.5 rounded-full" style={{ background: "#4ade80" }} />
              <span className="text-[0.6rem] tracking-wide uppercase" style={{ color: "#2a2a2a" }}>Sin datos guardados</span>
            </div>
            <button onClick={onClose}
              className="w-8 h-8 rounded-full flex items-center justify-center border transition-colors"
              style={{ background: "#0a0a0a", borderColor: "#1a1a1a" }}
              onMouseEnter={e => (e.currentTarget.style.borderColor = `${G}44`)}
              onMouseLeave={e => (e.currentTarget.style.borderColor = "#1a1a1a")}
            >
              <X size={14} style={{ color: "#555555" }} />
            </button>
          </div>
        </div>

        <div className="shrink-0 pt-3"><Disclaimer /></div>

        {/* Mensajes */}
        <div className="flex-1 overflow-y-auto px-4 py-4">
          {messages.length === 0 && (
            <div className="py-6">
              <p className="text-[0.82rem] text-center mb-6" style={{ color: "#333333" }}>
                Consultas frecuentes — haz clic para preguntar
              </p>
              <div className="grid grid-cols-1 gap-2">
                {QUICK_PROMPTS.map((p, i) => (
                  <button key={i} onClick={() => sendMessage(p)}
                    className="flex items-center gap-2 text-left rounded-[1.2rem] border px-4 py-3 transition-all duration-200"
                    style={{ background: "#0a0a0a", borderColor: "#1a1a1a" }}
                    onMouseEnter={e => { e.currentTarget.style.borderColor=`${G}33`; e.currentTarget.style.background="#0f0e0a"; }}
                    onMouseLeave={e => { e.currentTarget.style.borderColor="#1a1a1a"; e.currentTarget.style.background="#0a0a0a"; }}
                  >
                    <ChevronRight size={12} style={{ color: "#333333", flexShrink: 0 }} />
                    <span className="text-[0.78rem]" style={{ color: "#555555" }}>{p}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg, i) => (
            <Message key={i} role={msg.role} content={msg.content} isStreaming={msg.isStreaming} />
          ))}

          {toolStatus && (
            <div className="flex items-center gap-2 px-4 py-2 mb-3">
              <div className="shimmer w-4 h-4 rounded-full" />
              <span className="text-[0.68rem] tracking-wide" style={{ color: `${G}66` }}>{toolStatus}</span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <div className="shrink-0 px-5 py-1"><Disclaimer compact /></div>

        {/* Input */}
        <div className="shrink-0 px-4 pb-5 pt-2" style={{ borderTop: "1px solid #111111" }}>
          <div className="flex gap-2.5 items-end rounded-[2rem] px-4 py-3 border transition-colors"
            style={{ background: "#0a0a0a", borderColor: "#1a1a1a" }}
            onFocusCapture={e => (e.currentTarget.style.borderColor = `${G}33`)}
            onBlurCapture={e  => (e.currentTarget.style.borderColor = "#1a1a1a")}
          >
            <textarea
              ref={inputRef}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Escribe tu consulta tributaria o de inversiones..."
              rows={1}
              className="flex-1 bg-transparent text-[0.85rem] text-white resize-none outline-none leading-relaxed"
              style={{ maxHeight: "120px", caretColor: G }}
              onInput={e => { e.target.style.height = "auto"; e.target.style.height = `${Math.min(e.target.scrollHeight, 120)}px`; }}
              disabled={streaming}
            />
            <button
              onClick={() => sendMessage(input)}
              disabled={!input.trim() || streaming}
              className="shrink-0 w-9 h-9 rounded-full flex items-center justify-center transition-all duration-200 disabled:opacity-30"
              style={{ background: G }}
              onMouseEnter={e => !e.currentTarget.disabled && (e.currentTarget.style.boxShadow = `0 0 16px ${G}55`)}
              onMouseLeave={e => (e.currentTarget.style.boxShadow = "none")}
            >
              <Send size={14} style={{ color: "#000000" }} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
