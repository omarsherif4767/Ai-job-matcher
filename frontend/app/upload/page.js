"use client";
import { useRef, useState } from "react";
import Link from "next/link";

function Card({ children, style = {} }) {
  return (
    <div
      style={{
        background: "#0f1117",
        border: "1px solid #1e2130",
        borderRadius: 16,
        padding: "28px",
        ...style,
      }}
    >
      {children}
    </div>
  );
}

const RESUME_STORAGE_KEY = "antigravity:lastResumeProfile";

export default function UploadPage() {
  const [dragging, setDragging] = useState(false);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const inputRef = useRef();

  const handleFile = async (f) => {
    setFile(f);
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const fd = new FormData();
      fd.append("file", f);

      let res;
      try {
        res = await fetch("http://127.0.0.1:8000/api/resume/upload", {
          method: "POST",
          body: fd,
        });
      } catch {
        res = await fetch("http://localhost:8000/api/resume/upload", {
          method: "POST",
          body: fd,
        });
      }

      const data = await res.json();
      if (res.ok) {
        setResult(data);
        if (typeof window !== "undefined" && data.parsed_profile) {
          const profile = {
            ...data.parsed_profile,
            file_name: data.file_name,
            uploaded_at: new Date().toISOString(),
          };
          window.localStorage.setItem(RESUME_STORAGE_KEY, JSON.stringify(profile));
          await fetch("http://localhost:8000/api/profile/save", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ profile, file_name: data.file_name }),
          }).catch(() => {});
          await fetch("http://localhost:8000/api/jobs/recommend", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ candidate_profile: profile, country: "All", limit: 20 }),
          }).catch(() => {});
        }
      } else {
        setError(data.detail || "Resume parsing failed.");
      }
    } catch (e) {
      setError(
        `Connection error (${e.message || e.toString()}). Make sure the backend server is running.`
      );
    }

    setLoading(false);
  };

  const onDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files[0];
    if (f) handleFile(f);
  };

  return (
    <div style={{ maxWidth: 800 }}>
      <h1 style={{ color: "#fff", fontSize: 28, fontWeight: 700, margin: "0 0 8px" }}>
        Upload Resume
      </h1>
      <p style={{ color: "#64748b", marginBottom: 32 }}>
        Upload your PDF or DOCX resume. The parsed profile will drive your job
        recommendations.
      </p>

      <Card style={{ marginBottom: 24 }}>
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={onDrop}
          onClick={() => inputRef.current?.click()}
          style={{
            border: `2px dashed ${dragging ? "#6366f1" : "#1e2130"}`,
            borderRadius: 12,
            padding: "60px 32px",
            textAlign: "center",
            cursor: "pointer",
            transition: "all 0.2s",
            background: dragging ? "#6366f111" : "transparent",
          }}
        >
          <div style={{ fontSize: 48, marginBottom: 16 }}>📄</div>
          <div style={{ color: "#e2e8f0", fontSize: 18, fontWeight: 600, marginBottom: 8 }}>
            {file ? file.name : "Drop your resume here"}
          </div>
          <div style={{ color: "#64748b", fontSize: 14 }}>PDF or DOCX • Click or drag to upload</div>
          <input
            ref={inputRef}
            type="file"
            accept=".pdf,.docx,.doc"
            style={{ display: "none" }}
            onChange={(e) => e.target.files[0] && handleFile(e.target.files[0])}
          />
        </div>
      </Card>

      {loading && (
        <Card>
          <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
            <div
              style={{
                width: 36,
                height: 36,
                border: "3px solid #6366f1",
                borderTopColor: "transparent",
                borderRadius: "50%",
                animation: "spin 1s linear infinite",
              }}
            />
            <div>
              <div style={{ color: "#e2e8f0", fontWeight: 600 }}>Parsing resume with AI...</div>
              <div style={{ color: "#64748b", fontSize: 13 }}>
                Extracting skills, experience, education, projects, and languages
              </div>
            </div>
          </div>
          <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
        </Card>
      )}

      {error && (
        <Card style={{ borderColor: "#ef4444" }}>
          <div style={{ color: "#ef4444", fontWeight: 600 }}>⚠️ {error}</div>
        </Card>
      )}

      {result && (
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <Card>
            <h2 style={{ color: "#e2e8f0", margin: "0 0 16px", fontSize: 18 }}>ATS Score</h2>
            <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
              <div
                style={{
                  width: 80,
                  height: 80,
                  borderRadius: "50%",
                  background: `conic-gradient(#6366f1 ${result.parsed_profile?.ats_score ?? 0}%, #1e2130 0%)`,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <div
                  style={{
                    width: 64,
                    height: 64,
                    borderRadius: "50%",
                    background: "#0f1117",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    color: "#fff",
                    fontWeight: 700,
                    fontSize: 18,
                  }}
                >
                  {result.parsed_profile?.ats_score ?? "N/A"}
                </div>
              </div>
              <div>
                <div style={{ color: "#e2e8f0", fontWeight: 700 }}>
                  {result.parsed_profile?.candidate_name || "Resume parsed"}
                </div>
                <div style={{ color: "#94a3b8", fontSize: 13, marginTop: 4 }}>Parsed from: {result.file_name}</div>
                <div style={{ color: "#64748b", fontSize: 13 }}>Embedding dimensions: {result.embedding_dimensions}</div>
              </div>
            </div>
          </Card>

          <Card>
            <h3 style={{ color: "#e2e8f0", margin: "0 0 12px", fontSize: 15 }}>Skills</h3>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
              {(result.parsed_profile?.skills ?? []).map((skill) => (
                <span key={skill} style={{ background: "#6366f122", color: "#a5b4fc", padding: "4px 10px", borderRadius: 20, fontSize: 13 }}>
                  {skill}
                </span>
              ))}
            </div>
          </Card>

          <Card>
            <h3 style={{ color: "#e2e8f0", margin: "0 0 12px", fontSize: 15 }}>AI Suggestions</h3>
            {(result.parsed_profile?.suggestions ?? []).map((suggestion, index) => (
              <div key={index} style={{ color: "#94a3b8", fontSize: 14, marginBottom: 8 }}>
                {suggestion}
              </div>
            ))}
            <Link
              href="/jobs"
              style={{
                display: "inline-block",
                marginTop: 12,
                padding: "12px 22px",
                background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
                color: "#fff",
                borderRadius: 10,
                textDecoration: "none",
                fontWeight: 700,
              }}
            >
              View matched jobs
            </Link>
          </Card>
        </div>
      )}
    </div>
  );
}
