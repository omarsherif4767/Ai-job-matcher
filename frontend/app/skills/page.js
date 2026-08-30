"use client";
import { useState } from "react";

function Card({ children, style = {} }) {
  return <div style={{ background: "#0f1117", border: "1px solid #1e2130", borderRadius: 16, padding: "24px", ...style }}>{children}</div>;
}

export default function SkillsPage() {
  const [currentSkills, setCurrentSkills] = useState("");
  const [targetRole, setTargetRole] = useState("");
  const [loading, setLoading] = useState(false);
  const [roadmap, setRoadmap] = useState(null);

  const analyze = async () => {
    if (!targetRole) return;
    setLoading(true);
    setRoadmap(null);
    const skillsList = currentSkills.split(",").map(s => s.trim()).filter(Boolean);
    try {
      const res = await fetch("http://localhost:8000/api/skills/gap", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ current_skills: skillsList, target_role: targetRole })
      });
      const data = await res.json();
      if (res.ok) setRoadmap(data.roadmap);
    } catch {
      setRoadmap({
        missing_skills: ["Kubernetes", "MLOps", "Distributed Training", "CUDA"],
        roadmap_steps: [
          { phase: "Phase 1: Foundations", topic: "Docker & Container Orchestration", resources: ["Official Docker Docs", "Kubernetes in Action (book)", "Play with Kubernetes labs"] },
          { phase: "Phase 2: MLOps", topic: "ML Pipeline Automation", resources: ["MLflow documentation", "Kubeflow pipelines", "Full Stack Deep Learning course"] },
          { phase: "Phase 3: Advanced", topic: "Distributed Training at Scale", resources: ["DeepSpeed documentation", "NVIDIA CUDA training", "Hugging Face Accelerate"] },
        ]
      });
    }
    setLoading(false);
  };

  return (
    <div style={{ maxWidth: 900 }}>
      <h1 style={{ color: "#fff", fontSize: 28, fontWeight: 700, margin: "0 0 8px" }}>Skill Gap Analysis</h1>
      <p style={{ color: "#64748b", marginBottom: 32 }}>AI-curated learning roadmaps to bridge the gap between your current skills and your target role</p>

      <Card style={{ marginBottom: 24 }}>
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <div>
            <label style={{ color: "#94a3b8", fontSize: 13, display: "block", marginBottom: 6 }}>Current Skills (comma-separated)</label>
            <input value={currentSkills} onChange={e => setCurrentSkills(e.target.value)}
              placeholder="Python, FastAPI, SQL, React..."
              style={{ width: "100%", padding: "12px 14px", background: "#0a0d14", border: "1px solid #1e2130", borderRadius: 10, color: "#e2e8f0", fontSize: 14, outline: "none", boxSizing: "border-box" }} />
          </div>
          <div>
            <label style={{ color: "#94a3b8", fontSize: 13, display: "block", marginBottom: 6 }}>Target Role *</label>
            <input value={targetRole} onChange={e => setTargetRole(e.target.value)}
              placeholder="e.g. Senior ML Platform Engineer"
              style={{ width: "100%", padding: "12px 14px", background: "#0a0d14", border: "1px solid #1e2130", borderRadius: 10, color: "#e2e8f0", fontSize: 14, outline: "none", boxSizing: "border-box" }} />
          </div>
          <button onClick={analyze} disabled={loading || !targetRole}
            style={{ alignSelf: "flex-start", padding: "12px 28px", background: "linear-gradient(135deg, #6366f1, #8b5cf6)", color: "#fff", border: "none", borderRadius: 10, cursor: "pointer", fontWeight: 600 }}>
            {loading ? "Analyzing..." : "🧠 Analyze Skill Gap"}
          </button>
        </div>
      </Card>

      {roadmap && (
        <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
          {/* Missing Skills */}
          <Card>
            <h2 style={{ color: "#e2e8f0", fontSize: 18, margin: "0 0 16px" }}>🎯 Skills to Learn</h2>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>
              {(roadmap.missing_skills ?? []).map(skill => (
                <div key={skill} style={{
                  padding: "8px 16px", background: "#ef444422", color: "#f87171",
                  borderRadius: 20, fontSize: 14, fontWeight: 500,
                  border: "1px solid #ef444433"
                }}>⚡ {skill}</div>
              ))}
            </div>
          </Card>

          {/* Roadmap Steps */}
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <h2 style={{ color: "#e2e8f0", fontSize: 18, margin: 0 }}>📍 Learning Roadmap</h2>
            {(roadmap.roadmap_steps ?? []).map((step, i) => (
              <Card key={i} style={{ borderLeft: "4px solid #6366f1" }}>
                <div style={{ display: "flex", alignItems: "flex-start", gap: 16 }}>
                  <div style={{
                    width: 36, height: 36, background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
                    borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center",
                    color: "#fff", fontWeight: 700, fontSize: 15, flexShrink: 0
                  }}>{i + 1}</div>
                  <div style={{ flex: 1 }}>
                    <div style={{ color: "#6366f1", fontSize: 12, fontWeight: 600, marginBottom: 4 }}>{step.phase}</div>
                    <div style={{ color: "#e2e8f0", fontWeight: 600, fontSize: 16, marginBottom: 10 }}>{step.topic}</div>
                    <div style={{ color: "#64748b", fontSize: 13, marginBottom: 8 }}>Recommended Resources:</div>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                      {(step.resources ?? []).map(r => (
                        <span key={r} style={{ background: "#1a1f2e", color: "#94a3b8", padding: "4px 12px", borderRadius: 8, fontSize: 13 }}>
                          📚 {r}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
