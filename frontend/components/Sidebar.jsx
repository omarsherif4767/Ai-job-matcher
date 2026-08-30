"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  { label: "Dashboard", href: "/", icon: "📊" },
  { label: "Upload Resume", href: "/upload", icon: "📄" },
  { label: "Jobs", href: "/jobs", icon: "💼" },
  { label: "Chat", href: "/chat", icon: "💬" },
  { label: "Interview Prep", href: "/interview", icon: "🎤" },
  { label: "Skill Gap", href: "/skills", icon: "🧠" },
];

export default function Sidebar() {
  const pathname = usePathname();
  return (
    <aside style={{
      width: "220px", minHeight: "100vh", background: "#0f1117",
      borderRight: "1px solid #1e2130", display: "flex", flexDirection: "column",
      padding: "24px 0", position: "fixed", top: 0, left: 0, zIndex: 100
    }}>
      <div style={{ padding: "0 20px 28px", borderBottom: "1px solid #1e2130" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <div style={{
            width: 36, height: 36, background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
            borderRadius: 10, display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: 18
          }}>🚀</div>
          <div>
            <div style={{ color: "#fff", fontWeight: 700, fontSize: 15 }}>A Job in AI Era</div>
            <div style={{ color: "#6366f1", fontSize: 11 }}>Career Intelligence</div>
          </div>
        </div>
      </div>
      <nav style={{ flex: 1, padding: "16px 12px", display: "flex", flexDirection: "column", gap: 4 }}>
        {navItems.map(item => {
          const active = pathname === item.href;
          return (
            <Link key={item.href} href={item.href} style={{
              display: "flex", alignItems: "center", gap: 10, padding: "10px 12px",
              borderRadius: 10, textDecoration: "none",
              background: active ? "linear-gradient(135deg, #6366f1, #8b5cf6)" : "transparent",
              color: active ? "#fff" : "#94a3b8",
              fontWeight: active ? 600 : 400, fontSize: 14,
              transition: "all 0.2s"
            }}>
              <span>{item.icon}</span>
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>
      <div style={{ padding: "16px 20px", borderTop: "1px solid #1e2130" }}>
        <div style={{ color: "#475569", fontSize: 12 }}>v1.0 — AI Career Platform</div>
      </div>
    </aside>
  );
}
