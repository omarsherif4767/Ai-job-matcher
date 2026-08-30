"use client";
import { useState, useRef, useEffect } from "react";

const suggestions = [
  "Find remote AI internships",
  "Show jobs above a 90% match",
  "Explain why a job scored 72%",
  "Which skills am I missing?",
  "Show only jobs in Germany",
  "What should I learn next?",
  "Summarize Anthropic as a company",
  "Generate another cover letter",
];

export default function ChatPage() {
  const [messages, setMessages] = useState([
    { role: "assistant", content: "Hi! I'm your AI career assistant on A Job in AI Era. Ask me about job search, resume tips, salary negotiation, or anything career-related!" }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef();

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async (text) => {
    if (!text.trim()) return;
    setMessages(prev => [...prev, { role: "user", content: text }]);
    setInput("");
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, history: [] })
      });
      const data = await res.json();
      if (res.ok) {
        setMessages(prev => [...prev, { role: "assistant", content: data.reply || "No response received." }]);
      } else {
        setMessages(prev => [...prev, { role: "assistant", content: `⚠️ Server error: ${data.detail || "Unable to process request."}` }]);
      }
    } catch {
      setMessages(prev => [...prev, { role: "assistant", content: "⚠️ Could not reach backend server at http://localhost:8000. Ensure `python run.py` is active." }]);
    }
    setLoading(false);
  };

  return (
    <div style={{ maxWidth: 900, display: "flex", flexDirection: "column", height: "calc(100vh - 64px)" }}>
      <h1 style={{ color: "#fff", fontSize: 28, fontWeight: 700, margin: "0 0 8px" }}>Chat Assistant</h1>
      <p style={{ color: "#64748b", marginBottom: 20 }}>Powered by Qwen3 30B via OpenRouter — your intelligent career advisor</p>

      {/* Message History */}
      <div style={{
        flex: 1, overflowY: "auto", background: "#0f1117", borderRadius: 16,
        border: "1px solid #1e2130", padding: "20px", marginBottom: 16,
        display: "flex", flexDirection: "column", gap: 16
      }}>
        {messages.map((msg, i) => (
          <div key={i} style={{ display: "flex", justifyContent: msg.role === "user" ? "flex-end" : "flex-start" }}>
            {msg.role === "assistant" && (
              <div style={{
                width: 32, height: 32, background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
                borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: 16, marginRight: 10, flexShrink: 0, marginTop: 2
              }}>🚀</div>
            )}
            <div style={{
              maxWidth: "70%", padding: "12px 16px", borderRadius: msg.role === "user" ? "16px 16px 4px 16px" : "16px 16px 16px 4px",
              background: msg.role === "user" ? "linear-gradient(135deg, #6366f1, #8b5cf6)" : "#1a1f2e",
              color: "#e2e8f0", fontSize: 14, lineHeight: 1.7, whiteSpace: "pre-wrap"
            }}>{msg.content}</div>
          </div>
        ))}
        {loading && (
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div style={{
              width: 32, height: 32, background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
              borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 16
            }}>🚀</div>
            <div style={{ display: "flex", gap: 6 }}>
              {[0, 1, 2].map(i => (
                <div key={i} style={{
                  width: 8, height: 8, background: "#6366f1", borderRadius: "50%",
                  animation: `bounce 1.2s infinite ${i * 0.2}s`
                }} />
              ))}
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Suggestions */}
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 12 }}>
        {suggestions.map(s => (
          <button key={s} onClick={() => send(s)} style={{
            padding: "6px 14px", background: "#1a1f2e", color: "#94a3b8",
            border: "1px solid #1e2130", borderRadius: 20, fontSize: 12, cursor: "pointer",
            transition: "all 0.2s"
          }}>{s}</button>
        ))}
      </div>

      {/* Input */}
      <div style={{ display: "flex", gap: 12 }}>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && !e.shiftKey && send(input)}
          placeholder="Ask about your career, jobs, resume, or skills..."
          style={{
            flex: 1, padding: "14px 18px", background: "#0f1117",
            border: "1px solid #1e2130", borderRadius: 12, color: "#e2e8f0",
            fontSize: 14, outline: "none"
          }}
        />
        <button
          onClick={() => send(input)}
          disabled={loading || !input.trim()}
          style={{
            padding: "14px 24px", background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
            color: "#fff", border: "none", borderRadius: 12, cursor: loading ? "not-allowed" : "pointer",
            fontWeight: 600, opacity: loading ? 0.6 : 1
          }}
        >Send</button>
      </div>
      <style>{`@keyframes bounce { 0%, 80%, 100% { transform: translateY(0); } 40% { transform: translateY(-8px); } }`}</style>
    </div>
  );
}
