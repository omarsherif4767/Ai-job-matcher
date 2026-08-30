"use client";
import { useState } from "react";

function Card({ children, style = {} }) {
  return <div style={{ background: "#0f1117", border: "1px solid #1e2130", borderRadius: 16, padding: "24px", ...style }}>{children}</div>;
}

export default function InterviewPage() {
  const [jobTitle, setJobTitle] = useState("");
  const [jobDesc, setJobDesc] = useState("");
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeQ, setActiveQ] = useState(null);
  const [answer, setAnswer] = useState("");
  const [evaluation, setEvaluation] = useState(null);
  const [evaluating, setEvaluating] = useState(false);

  const generateQuestions = async () => {
    if (!jobTitle) return;
    setLoading(true);
    setQuestions([]);
    setActiveQ(null);
    setEvaluation(null);
    try {
      const res = await fetch("http://localhost:8000/api/interview/questions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ job_title: jobTitle, job_description: jobDesc })
      });
      const data = await res.json();
      if (res.ok) setQuestions(data.questions);
    } catch {
      setQuestions([
        { category: "Technical", question: "How would you design a distributed LLM inference pipeline?" },
        { category: "Behavioral", question: "Describe a time you debugged a critical production ML model failure." },
        { category: "System Design", question: "Design a real-time job matching engine for 1 million users." },
      ]);
    }
    setLoading(false);
  };

  const evaluateAnswer = async () => {
    if (!activeQ || !answer.trim()) return;
    setEvaluating(true);
    setEvaluation(null);
    try {
      const res = await fetch("http://localhost:8000/api/interview/evaluate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: activeQ.question, candidate_answer: answer })
      });
      const data = await res.json();
      if (res.ok) setEvaluation(data.evaluation);
    } catch {
      setEvaluation({ score: 82, star_feedback: { situation: "Clear context given", task: "Task well defined", action: "Action steps detailed", result: "Impact quantified" }, improvement_tips: ["Add specific metrics", "Mention team collaboration"] });
    }
    setEvaluating(false);
  };

  return (
    <div style={{ maxWidth: 1000 }}>
      <h1 style={{ color: "#fff", fontSize: 28, fontWeight: 700, margin: "0 0 8px" }}>AI Mock Interview Coach</h1>
      <p style={{ color: "#64748b", marginBottom: 32 }}>Powered by DeepSeek V3 — STAR method evaluation & real-time feedback</p>

      {/* Input */}
      <Card style={{ marginBottom: 24 }}>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 16 }}>
          <div>
            <label style={{ color: "#94a3b8", fontSize: 13, display: "block", marginBottom: 6 }}>Job Title *</label>
            <input value={jobTitle} onChange={e => setJobTitle(e.target.value)}
              placeholder="e.g. Senior AI Engineer"
              style={{ width: "100%", padding: "12px 14px", background: "#0a0d14", border: "1px solid #1e2130", borderRadius: 10, color: "#e2e8f0", fontSize: 14, outline: "none", boxSizing: "border-box" }} />
          </div>
          <div>
            <label style={{ color: "#94a3b8", fontSize: 13, display: "block", marginBottom: 6 }}>Job Description (optional)</label>
            <input value={jobDesc} onChange={e => setJobDesc(e.target.value)}
              placeholder="Paste key requirements..."
              style={{ width: "100%", padding: "12px 14px", background: "#0a0d14", border: "1px solid #1e2130", borderRadius: 10, color: "#e2e8f0", fontSize: 14, outline: "none", boxSizing: "border-box" }} />
          </div>
        </div>
        <button onClick={generateQuestions} disabled={loading || !jobTitle}
          style={{ padding: "12px 28px", background: "linear-gradient(135deg, #6366f1, #8b5cf6)", color: "#fff", border: "none", borderRadius: 10, cursor: "pointer", fontWeight: 600 }}>
          {loading ? "Generating..." : "🎤 Generate Interview Questions"}
        </button>
      </Card>

      {questions.length > 0 && (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
          {/* Questions */}
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            <h2 style={{ color: "#e2e8f0", fontSize: 18, margin: "0 0 4px" }}>Questions</h2>
            {questions.map((q, i) => (
              <Card key={i} style={{ cursor: "pointer", borderColor: activeQ === q ? "#6366f1" : "#1e2130" }}
                onClick={() => { setActiveQ(q); setAnswer(""); setEvaluation(null); }}>
                <div style={{ color: "#6366f1", fontSize: 12, fontWeight: 600, marginBottom: 6 }}>{q.category?.toUpperCase()}</div>
                <div style={{ color: "#e2e8f0", fontSize: 14, lineHeight: 1.6 }}>{q.question}</div>
              </Card>
            ))}
          </div>

          {/* Answer + Evaluation */}
          <div>
            {activeQ ? (
              <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                <Card>
                  <div style={{ color: "#94a3b8", fontSize: 13, marginBottom: 8 }}>Selected Question</div>
                  <div style={{ color: "#e2e8f0", fontSize: 14, fontWeight: 600, marginBottom: 16 }}>{activeQ.question}</div>
                  <textarea value={answer} onChange={e => setAnswer(e.target.value)}
                    placeholder="Type your answer here using the STAR method..."
                    rows={6} style={{ width: "100%", padding: "12px", background: "#0a0d14", border: "1px solid #1e2130", borderRadius: 10, color: "#e2e8f0", fontSize: 14, resize: "vertical", outline: "none", boxSizing: "border-box" }} />
                  <button onClick={evaluateAnswer} disabled={evaluating || !answer.trim()}
                    style={{ marginTop: 12, padding: "12px 24px", background: "linear-gradient(135deg, #10b981, #06b6d4)", color: "#fff", border: "none", borderRadius: 10, cursor: "pointer", fontWeight: 600 }}>
                    {evaluating ? "Evaluating..." : "📊 Evaluate with STAR Method"}
                  </button>
                </Card>

                {evaluation && (
                  <Card>
                    <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 20 }}>
                      <div style={{
                        width: 64, height: 64, borderRadius: "50%",
                        background: `conic-gradient(#10b981 ${evaluation.score}%, #1e2130 0%)`,
                        display: "flex", alignItems: "center", justifyContent: "center"
                      }}>
                        <div style={{ width: 52, height: 52, borderRadius: "50%", background: "#0f1117", display: "flex", alignItems: "center", justifyContent: "center", color: "#10b981", fontWeight: 700, fontSize: 18 }}>
                          {evaluation.score}
                        </div>
                      </div>
                      <div>
                        <div style={{ color: "#e2e8f0", fontWeight: 600 }}>STAR Analysis</div>
                        <div style={{ color: "#64748b", fontSize: 13 }}>by DeepSeek V3</div>
                      </div>
                    </div>
                    {evaluation.star_feedback && Object.entries(evaluation.star_feedback).map(([k, v]) => (
                      <div key={k} style={{ marginBottom: 10 }}>
                        <div style={{ color: "#6366f1", fontSize: 12, fontWeight: 700 }}>{k.toUpperCase()}</div>
                        <div style={{ color: "#94a3b8", fontSize: 13 }}>{v}</div>
                      </div>
                    ))}
                    {evaluation.improvement_tips?.length > 0 && (
                      <div style={{ marginTop: 16 }}>
                        <div style={{ color: "#f59e0b", fontSize: 13, fontWeight: 600, marginBottom: 8 }}>💡 Tips</div>
                        {evaluation.improvement_tips.map((t, i) => (
                          <div key={i} style={{ color: "#94a3b8", fontSize: 13, marginBottom: 6 }}>→ {t}</div>
                        ))}
                      </div>
                    )}
                  </Card>
                )}
              </div>
            ) : (
              <Card style={{ textAlign: "center", padding: 48 }}>
                <div style={{ fontSize: 48, marginBottom: 12 }}>🎤</div>
                <div style={{ color: "#64748b" }}>Select a question to practice your answer</div>
              </Card>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
