"use client";
import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const RESUME_STORAGE_KEY = "antigravity:lastResumeProfile";

const COLORS = ["#6366f1", "#06b6d4", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"];

const sampleSkillsData = [
  { skill: "Python", count: 342 },
  { skill: "React", count: 289 },
  { skill: "TypeScript", count: 251 },
  { skill: "Docker", count: 198 },
  { skill: "Kubernetes", count: 167 },
  { skill: "LangChain", count: 143 },
  { skill: "PostgreSQL", count: 128 },
  { skill: "AWS", count: 119 },
];

const sampleCompaniesData = [
  { company: "OpenAI", jobs: 48 },
  { company: "Anthropic", jobs: 35 },
  { company: "Google", jobs: 92 },
  { company: "Meta", jobs: 67 },
  { company: "Hugging Face", jobs: 29 },
  { company: "Databricks", jobs: 41 },
];

const sampleLocationData = [
  { name: "USA", value: 420 },
  { name: "UK", value: 145 },
  { name: "Germany", value: 98 },
  { name: "Remote", value: 312 },
  { name: "Canada", value: 87 },
  { name: "Other", value: 64 },
];

const sampleEmploymentData = [
  { name: "Full-time", value: 68 },
  { name: "Contract", value: 18 },
  { name: "Part-time", value: 7 },
  { name: "Internship", value: 7 },
];

const sampleSalaryData = [
  { range: "40-60k", count: 45 },
  { range: "60-80k", count: 89 },
  { range: "80-100k", count: 134 },
  { range: "100-130k", count: 178 },
  { range: "130-160k", count: 143 },
  { range: "160k+", count: 97 },
];

const sampleMatchScoreData = [
  { range: "50-60%", count: 23 },
  { range: "60-70%", count: 47 },
  { range: "70-80%", count: 82 },
  { range: "80-90%", count: 63 },
  { range: "90-100%", count: 31 },
];

const sampleRemoteData = [
  { name: "Remote", value: 45 },
  { name: "Hybrid", value: 32 },
  { name: "On-site", value: 23 },
];

function Card({ children, style = {} }) {
  return (
    <div
      style={{
        background: "#0f1117",
        border: "1px solid #1e2130",
        borderRadius: 16,
        padding: "24px",
        ...style,
      }}
    >
      {children}
    </div>
  );
}

function SectionTitle({ children }) {
  return <h2 style={{ color: "#e2e8f0", fontSize: 18, fontWeight: 600, marginBottom: 20, marginTop: 0 }}>{children}</h2>;
}

async function getJson(url, options) {
  const res = await fetch(url, options);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.detail || data.message || `Request failed: ${res.status}`);
  }
  return data;
}

function buildLiveStats(profile, counts) {
  if (!profile) {
    return [
      { label: "Total Jobs Ranked", value: "0", icon: "JR", color: "#6366f1" },
      { label: "Best Matches", value: "0", icon: "BM", color: "#10b981" },
      { label: "Avg Match Score", value: "0%", icon: "MS", color: "#8b5cf6" },
      { label: "CV Skills Found", value: "0", icon: "SK", color: "#f59e0b" },
      { label: "Applied", value: "0", icon: "AP", color: "#06b6d4" },
      { label: "Interviews", value: "0", icon: "IN", color: "#10b981" },
      { label: "Offers", value: "0", icon: "OF", color: "#f59e0b" },
      { label: "ATS Score", value: "N/A", icon: "AT", color: "#ef4444" },
    ];
  }

  const skillCount = Array.isArray(profile.skills) ? profile.skills.length : 0;
  const atsScore = Number(profile.ats_score || 0);
  const avgMatch = Number.isFinite(counts?.avg_match_score)
    ? counts.avg_match_score
    : Math.max(65, Math.min(96, Math.round((atsScore || 78) * 0.7 + skillCount * 2)));

  return [
    { label: "Total Jobs Ranked", value: String(counts?.jobs_ranked ?? 0), icon: "JR", color: "#6366f1" },
    { label: "Best Matches", value: String(counts?.best_matches ?? 0), icon: "BM", color: "#10b981" },
    { label: "Avg Match Score", value: `${avgMatch}%`, icon: "MS", color: "#8b5cf6" },
    { label: "CV Skills Found", value: String(counts?.cv_skills_found ?? skillCount), icon: "SK", color: "#f59e0b" },
    { label: "Applied", value: String(counts?.applied_jobs ?? 0), icon: "AP", color: "#06b6d4" },
    { label: "Saved", value: String(counts?.saved_jobs ?? 0), icon: "SV", color: "#10b981" },
    { label: "Rejected", value: String(counts?.rejected_jobs ?? 0), icon: "RJ", color: "#f59e0b" },
    { label: "ATS Score", value: atsScore ? String(atsScore) : "N/A", icon: "AT", color: "#ef4444" },
  ];
}

export default function Dashboard() {
  const [isDemoMode, setIsDemoMode] = useState(false);
  const [resumeProfile, setResumeProfile] = useState(null);
  const [dashboardState, setDashboardState] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  const refreshDashboard = async ({ preferCache = false } = {}) => {
    if (preferCache) {
      const raw = window.localStorage.getItem(RESUME_STORAGE_KEY);
      if (raw) {
        try {
          setResumeProfile(JSON.parse(raw));
        } catch {
          window.localStorage.removeItem(RESUME_STORAGE_KEY);
        }
      }
    }

    setRefreshing(true);
    try {
      const data = await getJson("http://localhost:8000/api/dashboard/refresh");
      setDashboardState(data);
      if (data.resume_profile) {
        setResumeProfile(data.resume_profile);
        window.localStorage.setItem(RESUME_STORAGE_KEY, JSON.stringify(data.resume_profile));
      } else {
        const raw = window.localStorage.getItem(RESUME_STORAGE_KEY);
        if (raw) {
          try {
            setResumeProfile(JSON.parse(raw));
          } catch {
            setResumeProfile(null);
          }
        } else {
          setResumeProfile(null);
        }
      }
    } catch {
      const raw = window.localStorage.getItem(RESUME_STORAGE_KEY);
      if (raw) {
        try {
          setResumeProfile(JSON.parse(raw));
        } catch {
          setResumeProfile(null);
        }
      }
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    refreshDashboard({ preferCache: true });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const profile = dashboardState?.resume_profile || resumeProfile;
  const liveStats = useMemo(() => buildLiveStats(profile, dashboardState?.counts), [profile, dashboardState]);
  const activeStatCards = isDemoMode
    ? [
        { label: "Total Jobs Scraped", value: "1,126", icon: "JS", color: "#6366f1" },
        { label: "Best Matches", value: "31", icon: "BM", color: "#10b981" },
        { label: "Avg Match Score", value: "78%", icon: "MS", color: "#8b5cf6" },
        { label: "Saved Jobs", value: "47", icon: "SV", color: "#f59e0b" },
        { label: "Applied", value: "12", icon: "AP", color: "#06b6d4" },
        { label: "Interviews", value: "3", icon: "IN", color: "#10b981" },
        { label: "Offers", value: "1", icon: "OF", color: "#f59e0b" },
        { label: "Rejections", value: "4", icon: "RJ", color: "#ef4444" },
      ]
    : liveStats;

  const profileSkillsData = (profile?.skills || []).slice(0, 8).map((skill, index) => ({
    skill,
    count: Math.max(25, 100 - index * 8),
  }));

  const chartSkillsData = isDemoMode ? sampleSkillsData : profileSkillsData;

  return (
    <div style={{ maxWidth: 1400 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 24 }}>
        <div>
          <h1 style={{ color: "#fff", fontSize: 28, fontWeight: 700, margin: 0 }}>Dashboard</h1>
          <p style={{ color: "#64748b", marginTop: 6 }}>Career intelligence overview powered by A Job in AI Era</p>
          {dashboardState?.updated_at && (
            <p style={{ color: "#64748b", marginTop: 4, fontSize: 12 }}>Last sync: {new Date(dashboardState.updated_at).toLocaleString()}</p>
          )}
        </div>

        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <div style={{ display: "flex", background: "#0f1117", border: "1px solid #1e2130", borderRadius: 10, padding: 4 }}>
            <button
              onClick={() => setIsDemoMode(false)}
              style={{
                padding: "8px 16px",
                borderRadius: 8,
                border: "none",
                cursor: "pointer",
                background: !isDemoMode ? "#6366f1" : "transparent",
                color: !isDemoMode ? "#fff" : "#94a3b8",
                fontWeight: 600,
                fontSize: 13,
              }}
            >
              My Account
            </button>
            <button
              onClick={() => setIsDemoMode(true)}
              style={{
                padding: "8px 16px",
                borderRadius: 8,
                border: "none",
                cursor: "pointer",
                background: isDemoMode ? "#6366f1" : "transparent",
                color: isDemoMode ? "#fff" : "#94a3b8",
                fontWeight: 600,
                fontSize: 13,
              }}
            >
              Sample Market Demo
            </button>
          </div>

          <button
            onClick={() => refreshDashboard()}
            style={{
              padding: "10px 16px",
              borderRadius: 10,
              border: "1px solid #1e2130",
              background: refreshing ? "#1e2130" : "#0f1117",
              color: "#e2e8f0",
              cursor: "pointer",
              fontWeight: 700,
            }}
          >
            {refreshing ? "Refreshing..." : "Refresh"}
          </button>
        </div>
      </div>

      {!isDemoMode && (
        <Card
          style={{
            marginBottom: 24,
            background: profile ? "linear-gradient(135deg, #052e2b, #0f1117)" : "linear-gradient(135deg, #1e1b4b, #0f1117)",
            borderColor: profile ? "#10b98166" : "#6366f155",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 16 }}>
            <div>
              <div style={{ color: "#fff", fontWeight: 700, fontSize: 16, marginBottom: 4 }}>
                {profile
                  ? `Resume loaded: ${profile.candidate_name || profile.file_name || "Candidate profile"}`
                  : "Welcome! Upload your resume to unlock personalized job matches and analytics"}
              </div>
              <div style={{ color: "#94a3b8", fontSize: 13 }}>
                {profile
                  ? `Using ${profile.skills?.length || 0} extracted skills to rank jobs and generate application materials.`
                  : 'Your account is currently empty. Upload your resume or click "Sample Market Demo" above to preview analytics.'}
              </div>
            </div>
            <Link
              href={profile ? "/jobs" : "/upload"}
              style={{
                padding: "10px 20px",
                background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
                color: "#fff",
                borderRadius: 10,
                textDecoration: "none",
                fontWeight: 600,
                fontSize: 14,
                flexShrink: 0,
              }}
            >
              {profile ? "View Jobs" : "Upload Resume"}
            </Link>
          </div>
          </Card>
        )}

      {!isDemoMode && profile && !(dashboardState?.counts?.jobs_ranked > 0) && (
        <Card style={{ marginBottom: 24, borderColor: "#1e2130" }}>
          <div style={{ color: "#e2e8f0", fontWeight: 700, marginBottom: 4 }}>Jobs are not ranked yet</div>
          <div style={{ color: "#94a3b8", fontSize: 13 }}>
            Open the Jobs page once to generate recommendations and populate the dashboard stats.
          </div>
        </Card>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 32 }}>
        {activeStatCards.map((card) => (
          card.label === "Saved" ? (
            <Link key={card.label} href="/jobs?status=saved" style={{ textDecoration: "none" }}>
              <Card style={{ padding: 20, cursor: "pointer" }}>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                  <div>
                    <div style={{ color: "#64748b", fontSize: 12, marginBottom: 6 }}>{card.label}</div>
                    <div style={{ color: "#fff", fontSize: 28, fontWeight: 700 }}>{card.value}</div>
                  </div>
                  <div
                    style={{
                      width: 48,
                      height: 48,
                      background: card.color + "22",
                      color: card.color,
                      borderRadius: 12,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontSize: 13,
                      fontWeight: 800,
                    }}
                  >
                    {card.icon}
                  </div>
                </div>
              </Card>
            </Link>
          ) : (
            <Card key={card.label} style={{ padding: 20 }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <div>
                  <div style={{ color: "#64748b", fontSize: 12, marginBottom: 6 }}>{card.label}</div>
                  <div style={{ color: "#fff", fontSize: 28, fontWeight: 700 }}>{card.value}</div>
                </div>
                <div
                  style={{
                    width: 48,
                    height: 48,
                    background: card.color + "22",
                    color: card.color,
                    borderRadius: 12,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: 13,
                    fontWeight: 800,
                  }}
                >
                  {card.icon}
                </div>
              </div>
            </Card>
          )
        ))}
      </div>

      {isDemoMode || profile ? (
        <>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20, marginBottom: 20 }}>
            <Card>
              <SectionTitle>{isDemoMode ? "Most Requested Skills" : "Skills From Your CV"}</SectionTitle>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={chartSkillsData} layout="vertical" margin={{ left: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e2130" />
                  <XAxis type="number" stroke="#475569" tick={{ fill: "#94a3b8", fontSize: 12 }} />
                  <YAxis dataKey="skill" type="category" stroke="#475569" tick={{ fill: "#94a3b8", fontSize: 12 }} width={90} />
                  <Tooltip contentStyle={{ background: "#0f1117", border: "1px solid #1e2130", borderRadius: 8 }} labelStyle={{ color: "#e2e8f0" }} />
                  <Bar dataKey="count" fill="#6366f1" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </Card>

            <Card>
              <SectionTitle>Top Hiring Companies</SectionTitle>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={sampleCompaniesData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e2130" />
                  <XAxis dataKey="company" stroke="#475569" tick={{ fill: "#94a3b8", fontSize: 11 }} />
                  <YAxis stroke="#475569" tick={{ fill: "#94a3b8", fontSize: 12 }} />
                  <Tooltip contentStyle={{ background: "#0f1117", border: "1px solid #1e2130", borderRadius: 8 }} labelStyle={{ color: "#e2e8f0" }} />
                  <Bar dataKey="jobs" fill="#06b6d4" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </Card>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 20 }}>
            <Card>
              <SectionTitle>Jobs by Country</SectionTitle>
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie data={sampleLocationData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={75}>
                    {sampleLocationData.map((_, i) => (
                      <Cell key={i} fill={COLORS[i % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ background: "#0f1117", border: "1px solid #1e2130", borderRadius: 8 }} />
                </PieChart>
              </ResponsiveContainer>
            </Card>

            <Card>
              <SectionTitle>Match Score Distribution</SectionTitle>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={sampleMatchScoreData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e2130" />
                  <XAxis dataKey="range" stroke="#475569" tick={{ fill: "#94a3b8", fontSize: 11 }} />
                  <YAxis stroke="#475569" tick={{ fill: "#94a3b8", fontSize: 12 }} />
                  <Tooltip contentStyle={{ background: "#0f1117", border: "1px solid #1e2130", borderRadius: 8 }} />
                  <Bar dataKey="count" fill="#10b981" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </Card>

            <Card>
              <SectionTitle>Remote vs On-site</SectionTitle>
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie data={sampleRemoteData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={75}>
                    {sampleRemoteData.map((_, i) => (
                      <Cell key={i} fill={COLORS[i % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ background: "#0f1117", border: "1px solid #1e2130", borderRadius: 8 }} />
                </PieChart>
              </ResponsiveContainer>
            </Card>
          </div>
        </>
      ) : (
        <Card style={{ textAlign: "center", padding: "60px 24px" }}>
          <div style={{ color: "#e2e8f0", fontSize: 18, fontWeight: 600, marginBottom: 8 }}>No Activity Recorded Yet</div>
          <div style={{ color: "#64748b", fontSize: 14, maxWidth: 500, margin: "0 auto 24px" }}>
            Upload your resume to populate account stats, extracted skills, and personalized job matches.
          </div>
          <div style={{ display: "flex", gap: 12, justifyContent: "center" }}>
            <Link
              href="/upload"
              style={{
                padding: "12px 24px",
                background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
                color: "#fff",
                borderRadius: 10,
                textDecoration: "none",
                fontWeight: 600,
              }}
            >
              Upload Resume
            </Link>
            <button
              onClick={() => setIsDemoMode(true)}
              style={{
                padding: "12px 24px",
                background: "#1e2130",
                color: "#94a3b8",
                border: "none",
                borderRadius: 10,
                cursor: "pointer",
                fontWeight: 600,
              }}
            >
              View Sample Demo Analytics
            </button>
          </div>
        </Card>
      )}
    </div>
  );
}
