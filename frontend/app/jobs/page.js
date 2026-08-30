"use client";
import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";

const RESUME_STORAGE_KEY = "antigravity:lastResumeProfile";
const COUNTRY_FILTERS = [
  { label: "All", value: "all" },
  { label: "Egypt", value: "egypt" },
  { label: "Germany", value: "germany" },
  { label: "USA", value: "usa" },
  { label: "Europe", value: "europe" },
  { label: "Remote", value: "remote" },
];
const COUNTRY_KEYWORDS = {
  egypt: ["egypt", "cairo", "giza", "alexandria", "maadi", "new cairo", "remote in egypt"],
  germany: ["germany", "berlin", "munich", "hamburg", "frankfurt", "cologne"],
  usa: ["united states", "usa", "u.s.", "new york", "san francisco", "seattle", "austin", "boston", "chicago", "remote us", "remote - us"],
  europe: [
    "europe",
    "germany",
    "berlin",
    "munich",
    "hamburg",
    "frankfurt",
    "cologne",
    "united kingdom",
    "uk",
    "london",
    "manchester",
    "edinburgh",
    "france",
    "paris",
    "spain",
    "madrid",
    "barcelona",
    "italy",
    "milan",
    "rome",
    "netherlands",
    "amsterdam",
    "poland",
    "warsaw",
    "portugal",
    "lisbon",
    "ireland",
    "dublin",
    "sweden",
    "stockholm",
    "norway",
    "oslo",
    "denmark",
    "copenhagen",
    "finland",
    "helsinki",
    "belgium",
    "brussels",
  ],
  remote: ["remote", "work from home", "wfh", "distributed"],
};

function Card({ children, style = {}, onClick }) {
  return (
    <div
      onClick={onClick}
      style={{
        background: "#0f1117",
        border: "1px solid #1e2130",
        borderRadius: 16,
        padding: 24,
        ...style,
      }}
    >
      {children}
    </div>
  );
}

function ScoreBadge({ score }) {
  const color = score >= 90 ? "#10b981" : score >= 80 ? "#6366f1" : score >= 70 ? "#f59e0b" : "#ef4444";
  return (
    <div style={{ padding: "6px 14px", borderRadius: 20, background: color + "22", color, fontWeight: 700 }}>
      {score}%
    </div>
  );
}

function StatusBadge({ status }) {
  if (!status) return null;
  const normalized = String(status).toLowerCase();
  const colors = { saved: "#06b6d4", applied: "#10b981", rejected: "#ef4444" };
  const color = colors[normalized] || "#64748b";
  return (
    <span
      style={{
        marginLeft: 8,
        padding: "3px 8px",
        borderRadius: 999,
        background: color + "22",
        color,
        fontSize: 12,
        fontWeight: 700,
      }}
    >
      {normalized}
    </span>
  );
}

function localScore(job, profile) {
  const profileSkills = new Set((profile?.skills || []).map((s) => String(s).toLowerCase()));
  const jobSkills = (job.skills || []).map((s) => String(s).toLowerCase());
  const overlap = jobSkills.filter((skill) => profileSkills.has(skill)).length;
  const skillScore = jobSkills.length ? overlap / jobSkills.length : 0.35;
  const ats = Number(profile?.ats_score || 78);
  return Math.max(55, Math.min(98, Math.round(ats * 0.45 + skillScore * 45 + 10)));
}

function normalizeSkillList(values = []) {
  return Array.from(
    new Set(
      values
        .map((value) => String(value || "").trim())
        .filter(Boolean)
    )
  );
}

function normalizeText(value) {
  return String(value || "").toLowerCase();
}

function getCountryNeedles(country) {
  return COUNTRY_KEYWORDS[normalizeText(country)] || [];
}

function jobMatchesCountry(job, country) {
  const normalizedCountry = normalizeText(country);
  if (!normalizedCountry || normalizedCountry === "all") {
    return true;
  }

  const haystack = normalizeText([
    job?.country,
    job?.location,
    job?.source_location,
    job?.workplace_type,
    job?.title,
    job?.company,
    job?.description,
    job?.source_platform,
  ].join(" "));

  const needles = getCountryNeedles(normalizedCountry);
  if (!needles.length) {
    return true;
  }

  return needles.some((needle) => haystack.includes(needle));
}

function inferCountryBucket(job) {
  const haystack = normalizeText([
    job?.country,
    job?.location,
    job?.source_location,
    job?.workplace_type,
    job?.title,
    job?.company,
    job?.description,
    job?.source_platform,
  ].join(" "));

  if (COUNTRY_KEYWORDS.egypt.some((needle) => haystack.includes(needle))) return "egypt";
  if (COUNTRY_KEYWORDS.germany.some((needle) => haystack.includes(needle))) return "germany";
  if (COUNTRY_KEYWORDS.usa.some((needle) => haystack.includes(needle))) return "usa";
  if (COUNTRY_KEYWORDS.remote.some((needle) => haystack.includes(needle))) return "remote";
  if (COUNTRY_KEYWORDS.europe.some((needle) => haystack.includes(needle))) return "europe";
  return "all";
}

function getMatchingSkills(job, profile) {
  const profileSkills = new Set(normalizeSkillList(profile?.skills).map((skill) => skill.toLowerCase()));
  return normalizeSkillList(job.skills || job.role_signals || extractJobSignals(job)).filter((skill) => profileSkills.has(skill.toLowerCase()));
}

function getMissingSkills(job, profile) {
  const profileSkills = new Set(normalizeSkillList(profile?.skills).map((skill) => skill.toLowerCase()));
  return normalizeSkillList(job.skills || job.role_signals || extractJobSignals(job)).filter((skill) => !profileSkills.has(skill.toLowerCase()));
}

function extractJobSignals(job) {
  const haystack = `${job?.title || ""} ${job?.company || ""} ${job?.location || ""} ${job?.description || ""}`;
  const keywords = [
    "Python",
    "SQL",
    "Azure",
    "AWS",
    "GCP",
    "Docker",
    "Kubernetes",
    "FastAPI",
    "Flask",
    "Django",
    "React",
    "Next.js",
    "TypeScript",
    "JavaScript",
    "Node.js",
    "PostgreSQL",
    "MongoDB",
    "PyTorch",
    "TensorFlow",
    "Machine Learning",
    "Deep Learning",
    "Data Engineering",
    "MLOps",
    "LangChain",
    "LLM",
    "RAG",
    "Spark",
    "Scala",
    "C++",
    "C#",
    "Java",
    "Cloud",
    "Backend",
    "APIs",
    "ETL",
    "Linux",
  ];
  const roleSignals = [];
  const lowerTitle = normalizeText(job?.title);

  const rolePatterns = [
    { pattern: /data engineer|analytics engineer/i, signals: ["Data Engineering", "SQL", "ETL", "Spark", "Python"] },
    { pattern: /machine learning|ml engineer|ai engineer/i, signals: ["Machine Learning", "Python", "PyTorch", "TensorFlow", "MLOps"] },
    { pattern: /backend/i, signals: ["Backend", "APIs", "Python", "Node.js", "SQL"] },
    { pattern: /frontend/i, signals: ["React", "Next.js", "TypeScript", "JavaScript", "APIs"] },
    { pattern: /full[- ]stack/i, signals: ["React", "Node.js", "TypeScript", "APIs", "SQL"] },
    { pattern: /devops|platform/i, signals: ["Docker", "Kubernetes", "Cloud", "Linux", "CI/CD"] },
    { pattern: /product manager|project manager/i, signals: ["Agile", "Roadmaps", "Stakeholder Management", "Communication"] },
    { pattern: /business analyst/i, signals: ["SQL", "Reporting", "Analytics", "Requirements Gathering"] },
    { pattern: /software engineer/i, signals: ["Backend", "APIs", "Python", "JavaScript", "SQL"] },
  ];

  rolePatterns.forEach(({ pattern, signals }) => {
    if (pattern.test(lowerTitle)) {
      roleSignals.push(...signals);
    }
  });

  return Array.from(
    new Set([
      ...keywords.filter((keyword) => new RegExp(`\\b${keyword.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\b`, "i").test(haystack)),
      ...roleSignals,
    ])
  );
}

function buildWhyThisJob(job, profile) {
  const matching = getMatchingSkills(job, profile);
  if (matching.length) {
    const topMatches = matching.slice(0, 3).join(", ");
    return `Matches your CV skills: ${topMatches}${matching.length > 3 ? ` and ${matching.length - 3} more` : ""}.`;
  }

  const signals = normalizeSkillList(job.role_signals || extractJobSignals(job));
  if (signals.length) {
    return `This role emphasizes ${signals.slice(0, 3).join(", ")}, which aligns with the job keywords in ${job.company || "this company"}.`;
  }

  const locationText = [job.company, job.location].filter(Boolean).join(" in ");
  return `This role at ${locationText || "this company"} is a keyword match for the title ${job.title || "shown here"}.`;
}

function isGenericWhyText(value) {
  const text = normalizeText(value);
  return (
    !text ||
    text.includes("the title and stack are still close") ||
    text.includes("role keywords") ||
    text.includes("no direct skill overlap detected")
  );
}

async function getJson(url, options) {
  const res = await fetch(url, options);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.detail || data.message || `Request failed: ${res.status}`);
  }
  return data;
}

export default function JobsPage() {
  const searchParams = useSearchParams();
  const [resumeProfile, setResumeProfile] = useState(null);
  const [country, setCountry] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");
  const [jobs, setJobs] = useState([]);
  const [selected, setSelected] = useState(null);
  const [loadingProfile, setLoadingProfile] = useState(true);
  const [loadingJobs, setLoadingJobs] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [generating, setGenerating] = useState(false);
  const [coverLetter, setCoverLetter] = useState(null);
  const [jobActions, setJobActions] = useState({});

  useEffect(() => {
    const status = searchParams.get("status") || "all";
    setStatusFilter(["saved", "applied", "rejected"].includes(status) ? status : "all");
  }, [searchParams]);

  const loadJobs = async (profile) => {
    if (!profile) {
      setJobs([]);
      setSelected(null);
      return;
    }

    setLoadingJobs(true);
    setError("");
    setCoverLetter(null);

    try {
      const dashboard = await getJson("http://localhost:8000/api/dashboard/refresh");
      const cachedJobs = dashboard.recommended_jobs || [];
      const actions = dashboard.job_actions || {};
      setJobActions(actions);

      const ranked = cachedJobs.map((job, index) => ({
        ...job,
        id: `${job.source_platform || "job"}-${index}-${job.apply_url}`,
        match: job.match_score || localScore(job, profile),
        status: actions[job.apply_url]?.status || "",
        matching_skills: normalizeSkillList(Array.isArray(job.matching_skills) && job.matching_skills.length ? job.matching_skills : getMatchingSkills(job, profile)),
        missing_skills: normalizeSkillList(Array.isArray(job.missing_skills) && job.missing_skills.length ? job.missing_skills : getMissingSkills(job, profile)),
        role_signals: normalizeSkillList(Array.isArray(job.role_signals) && job.role_signals.length ? job.role_signals : extractJobSignals(job)),
        why_this_job: isGenericWhyText(job.why_this_job) ? buildWhyThisJob(job, profile) : job.why_this_job,
        country_bucket: job.country_bucket || inferCountryBucket(job),
      }));

      if (!ranked.length) {
        const data = await getJson("http://localhost:8000/api/jobs/recommend", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ candidate_profile: profile, country: "All", limit: 100 }),
        });
        const apiJobs = (data.jobs || []).map((job, index) => ({
          ...job,
          id: `${job.source_platform || "job"}-${index}-${job.apply_url}`,
          match: job.match_score || localScore(job, profile),
          status: actions[job.apply_url]?.status || "",
          matching_skills: normalizeSkillList(Array.isArray(job.matching_skills) && job.matching_skills.length ? job.matching_skills : getMatchingSkills(job, profile)),
          missing_skills: normalizeSkillList(Array.isArray(job.missing_skills) && job.missing_skills.length ? job.missing_skills : getMissingSkills(job, profile)),
          role_signals: normalizeSkillList(Array.isArray(job.role_signals) && job.role_signals.length ? job.role_signals : extractJobSignals(job)),
          why_this_job: isGenericWhyText(job.why_this_job) ? buildWhyThisJob(job, profile) : job.why_this_job,
          country_bucket: job.country_bucket || inferCountryBucket(job),
        }));
        ranked.push(...apiJobs);
      }

      ranked.sort((a, b) => b.match - a.match);
      setJobs(ranked);
      setSelected((current) => ranked.find((job) => job.id === current?.id) || ranked[0] || null);
    } catch (e) {
      setError(e.message || "Could not load job recommendations.");
      setJobs([]);
      setSelected(null);
    } finally {
      setLoadingJobs(false);
    }
  };

  useEffect(() => {
    const loadProfile = async () => {
      setLoadingProfile(true);
      const raw = window.localStorage.getItem(RESUME_STORAGE_KEY);
      if (raw) {
        try {
          const profile = JSON.parse(raw);
          setResumeProfile(profile);
          setLoadingProfile(false);
          return;
        } catch {
          window.localStorage.removeItem(RESUME_STORAGE_KEY);
        }
      }

      try {
        const data = await getJson("http://localhost:8000/api/profile/latest");
        if (data.resume_profile) {
          setResumeProfile(data.resume_profile);
          window.localStorage.setItem(RESUME_STORAGE_KEY, JSON.stringify(data.resume_profile));
        } else {
          setResumeProfile(null);
        }
      } catch {
        setResumeProfile(null);
      } finally {
        setLoadingProfile(false);
      }
    };

    loadProfile();
  }, []);

  useEffect(() => {
    if (!resumeProfile) return;
    loadJobs(resumeProfile);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [resumeProfile]);

  const visibleJobs = useMemo(() => {
    return jobs.filter((job) => {
      const statusMatch = statusFilter === "all" || String(job.status || "").toLowerCase() === statusFilter;
      const countryMatch = country === "all" || (job.country_bucket || inferCountryBucket(job)) === country;
      return statusMatch && countryMatch;
    });
  }, [jobs, statusFilter, country]);

  useEffect(() => {
    if (!visibleJobs.length) {
      setSelected(null);
      return;
    }
    setSelected((current) => visibleJobs.find((job) => job.id === current?.id) || visibleJobs[0]);
  }, [visibleJobs]);

  const refreshJobs = async () => {
    setRefreshing(true);
    try {
      const profileData = await getJson("http://localhost:8000/api/profile/latest");
      const profile = profileData.resume_profile || resumeProfile;
      if (profileData.resume_profile) {
        setResumeProfile(profileData.resume_profile);
        window.localStorage.setItem(RESUME_STORAGE_KEY, JSON.stringify(profileData.resume_profile));
      }

      if (profile) {
        try {
          await getJson("http://localhost:8000/api/jobs/recommend", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ candidate_profile: profile, country: "All", limit: 100 }),
          });
        } catch {
          // Keep going with cached jobs from dashboard refresh.
        }
      }

      await loadJobs(profile);
    } catch (e) {
      setError(e.message || "Refresh failed.");
    } finally {
      setRefreshing(false);
    }
  };

  const generateCoverLetter = async (job) => {
    setGenerating(true);
    setCoverLetter(null);
    try {
      const data = await getJson("http://localhost:8000/api/cover-letter/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          candidate_profile: resumeProfile,
          job_details: job,
        }),
      });
      setCoverLetter(data.materials);
    } catch {
      setCoverLetter({ cover_letter: "Backend not connected. Start the server to generate cover letters." });
    } finally {
      setGenerating(false);
    }
  };

  const updateJobStatus = async (job, status) => {
    try {
      const data = await getJson("http://localhost:8000/api/jobs/action", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ job, status }),
      });
      const nextActions = data.job_actions || {};
      setJobActions(nextActions);
      setJobs((prev) => prev.map((item) => (item.apply_url === job.apply_url ? { ...item, status } : item)));
      setSelected((current) => (current?.apply_url === job.apply_url ? { ...current, status } : current));
    } catch (e) {
      setError(e.message || "Could not save job status.");
    }
  };

  if (loadingProfile) {
    return (
      <div style={{ maxWidth: 900 }}>
        <h1 style={{ color: "#fff", fontSize: 28, fontWeight: 700, margin: "0 0 8px" }}>Job Feed</h1>
        <Card style={{ color: "#94a3b8", marginTop: 32 }}>Loading your CV and recommendations...</Card>
      </div>
    );
  }

  if (!resumeProfile) {
    return (
      <div style={{ maxWidth: 900 }}>
        <h1 style={{ color: "#fff", fontSize: 28, fontWeight: 700, margin: "0 0 8px" }}>Job Feed</h1>
        <Card style={{ textAlign: "center", padding: 48, marginTop: 32 }}>
          <div style={{ color: "#e2e8f0", fontWeight: 700, fontSize: 20, marginBottom: 8 }}>Upload your CV first</div>
          <div style={{ color: "#64748b", marginBottom: 24 }}>Job recommendations stay empty until your resume is parsed.</div>
          <Link
            href="/upload"
            style={{
              display: "inline-block",
              padding: "12px 22px",
              background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
              color: "#fff",
              borderRadius: 10,
              textDecoration: "none",
              fontWeight: 700,
            }}
          >
            Upload Resume
          </Link>
        </Card>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 1200 }}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 16, alignItems: "flex-start", marginBottom: 24 }}>
        <div>
          <h1 style={{ color: "#fff", fontSize: 28, fontWeight: 700, margin: "0 0 8px" }}>Job Feed</h1>
          <p style={{ color: "#64748b", margin: 0 }}>
            Wuzzuf and LinkedIn recommendations ranked from {resumeProfile.candidate_name || resumeProfile.file_name || "your CV"}.
          </p>
        </div>
        <div style={{ display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap", justifyContent: "flex-end" }}>
          <div style={{ display: "flex", background: "#0f1117", border: "1px solid #1e2130", borderRadius: 10, padding: 4 }}>
            {[
              { label: "All", value: "all" },
              { label: "Saved", value: "saved" },
              { label: "Applied", value: "applied" },
              { label: "Rejected", value: "rejected" },
            ].map((item) => (
              <button
                key={item.value}
                onClick={() => setStatusFilter(item.value)}
                style={{
                  padding: "8px 12px",
                  borderRadius: 8,
                  border: "none",
                  cursor: "pointer",
                  background: statusFilter === item.value ? "#6366f1" : "transparent",
                  color: statusFilter === item.value ? "#fff" : "#94a3b8",
                  fontWeight: 700,
                  fontSize: 12,
                }}
              >
                {item.label}
              </button>
            ))}
          </div>
          <div style={{ display: "flex", background: "#0f1117", border: "1px solid #1e2130", borderRadius: 10, padding: 4, gap: 4, flexWrap: "wrap" }}>
            {COUNTRY_FILTERS.map((item) => (
              <button
                key={item.value}
                onClick={() => setCountry(item.value)}
                style={{
                  padding: "8px 12px",
                  borderRadius: 8,
                  border: "none",
                  cursor: "pointer",
                  background: country === item.value ? "#6366f1" : "transparent",
                  color: country === item.value ? "#fff" : "#94a3b8",
                  fontWeight: 700,
                  fontSize: 12,
                }}
              >
                {item.label}
              </button>
            ))}
          </div>
          <button
            onClick={refreshJobs}
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

      {loadingJobs && <Card style={{ color: "#94a3b8", marginBottom: 16 }}>Loading direct job links...</Card>}
      {error && <Card style={{ color: "#ef4444", borderColor: "#ef4444", marginBottom: 16 }}>{error}</Card>}

      <div style={{ display: "grid", gridTemplateColumns: "1fr 420px", gap: 24 }}>
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {!loadingJobs && visibleJobs.length === 0 && <Card style={{ color: "#94a3b8" }}>No jobs found for this filter yet.</Card>}

          {visibleJobs.map((job) => (
            <Card
              key={job.id}
              onClick={() => {
                setSelected(job);
                setCoverLetter(null);
              }}
              style={{
                cursor: "pointer",
                borderColor: selected?.id === job.id ? "#6366f1" : "#1e2130",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", gap: 16 }}>
                <div>
                  <div style={{ color: "#fff", fontWeight: 700, fontSize: 17, marginBottom: 4 }}>
                    {job.title}
                    <StatusBadge status={job.status} />
                  </div>
                  <div style={{ color: "#94a3b8", fontSize: 14 }}>
                    {job.company} · {job.location}
                  </div>
                  <div style={{ display: "flex", gap: 8, marginTop: 10, flexWrap: "wrap" }}>
                    {(job.skills || []).slice(0, 6).map((skill) => (
                      <span key={skill} style={{ background: "#1e2130", color: "#94a3b8", padding: "3px 8px", borderRadius: 8, fontSize: 12 }}>
                        {skill}
                      </span>
                    ))}
                    <span style={{ background: "#1e2130", color: "#64748b", padding: "3px 8px", borderRadius: 8, fontSize: 12 }}>
                      via {job.source_platform}
                    </span>
                  </div>
                </div>
                <ScoreBadge score={job.match} />
              </div>
            </Card>
          ))}
        </div>

        <div>
          {selected ? (
            <Card style={{ position: "sticky", top: 20 }}>
              <div style={{ display: "flex", justifyContent: "space-between", gap: 16, marginBottom: 16 }}>
                <div>
                  <div style={{ color: "#fff", fontWeight: 700, fontSize: 20 }}>{selected.title}</div>
                  <div style={{ color: "#94a3b8" }}>{selected.company}</div>
                  <div style={{ color: "#64748b", fontSize: 13, marginTop: 6 }}>{selected.location}</div>
                </div>
                <ScoreBadge score={selected.match} />
              </div>

              <div style={{ color: "#94a3b8", fontSize: 13, lineHeight: 1.7, marginBottom: 20, maxHeight: 150, overflow: "auto" }}>
                {selected.description}
              </div>

              <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
                <a
                  href={selected.apply_url}
                  target="_blank"
                  rel="noreferrer"
                  style={{
                    flex: 1,
                    textAlign: "center",
                    padding: "12px",
                    background: "linear-gradient(135deg, #10b981, #0ea5e9)",
                    color: "#fff",
                    borderRadius: 10,
                    textDecoration: "none",
                    fontWeight: 700,
                  }}
                >
                  Apply now
                </a>
                <button
                  onClick={() => generateCoverLetter(selected)}
                  style={{
                    flex: 1,
                    padding: "12px",
                    background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
                    color: "#fff",
                    border: "none",
                    borderRadius: 10,
                    cursor: "pointer",
                    fontWeight: 700,
                  }}
                >
                  {generating ? "Generating..." : "Cover Letter"}
                </button>
              </div>

              <div style={{ display: "flex", gap: 8, marginBottom: 16, flexWrap: "wrap" }}>
                <button
                  onClick={() => updateJobStatus(selected, "saved")}
                  style={{
                    padding: "10px 14px",
                    background: "#0f172a",
                    color: "#e2e8f0",
                    border: "1px solid #1e2130",
                    borderRadius: 10,
                    cursor: "pointer",
                    fontWeight: 700,
                    background: selected.status === "saved" ? "#0f766e" : "#0f172a",
                  }}
                >
                  {selected.status === "saved" ? "Saved" : "Save"}
                </button>
                <button
                  onClick={() => updateJobStatus(selected, "applied")}
                  style={{
                    padding: "10px 14px",
                    background: "#0f172a",
                    color: "#e2e8f0",
                    border: "1px solid #1e2130",
                    borderRadius: 10,
                    cursor: "pointer",
                    fontWeight: 700,
                  }}
                >
                  Applied
                </button>
                <button
                  onClick={() => updateJobStatus(selected, "rejected")}
                  style={{
                    padding: "10px 14px",
                    background: "#0f172a",
                    color: "#e2e8f0",
                    border: "1px solid #1e2130",
                    borderRadius: 10,
                    cursor: "pointer",
                    fontWeight: 700,
                  }}
                >
                  Rejected
                </button>
              </div>

              <div style={{ color: "#64748b", fontSize: 12, wordBreak: "break-all", marginBottom: 8 }}>
                Apply link: {selected.apply_url}
              </div>
              <div style={{ color: "#64748b", fontSize: 12, wordBreak: "break-all", marginBottom: 16 }}>
                Source: {selected.source_platform}
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 16 }}>
                <Card style={{ padding: 14, background: "#0b1220", borderRadius: 12 }}>
                  <div style={{ color: "#e2e8f0", fontSize: 13, fontWeight: 700, marginBottom: 8 }}>Why this job</div>
                  <div style={{ color: "#94a3b8", fontSize: 13, lineHeight: 1.6 }}>{selected.why_this_job}</div>
                  <div style={{ color: "#64748b", fontSize: 12, marginTop: 8, marginBottom: 6 }}>Role signals</div>
                  <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginTop: 10 }}>
                    {selected.role_signals?.length ? (
                      selected.role_signals.map((skill) => (
                        <span key={skill} style={{ background: "#6366f122", color: "#a5b4fc", padding: "4px 8px", borderRadius: 999, fontSize: 12, fontWeight: 700 }}>
                          {skill}
                        </span>
                      ))
                    ) : (
                      <span style={{ color: "#64748b", fontSize: 12 }}>No clear role signals detected from this posting.</span>
                    )}
                  </div>
                  <div style={{ color: "#64748b", fontSize: 12, marginTop: 14, marginBottom: 6 }}>Matching skills</div>
                  <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                    {selected.matching_skills?.length ? (
                      selected.matching_skills.map((skill) => (
                        <span key={skill} style={{ background: "#10b98122", color: "#6ee7b7", padding: "4px 8px", borderRadius: 999, fontSize: 12, fontWeight: 700 }}>
                          {skill}
                        </span>
                      ))
                    ) : (
                      <span style={{ color: "#64748b", fontSize: 12 }}>No direct skill overlap detected.</span>
                    )}
                  </div>
                </Card>

                <Card style={{ padding: 14, background: "#0b1220", borderRadius: 12 }}>
                  <div style={{ color: "#e2e8f0", fontSize: 13, fontWeight: 700, marginBottom: 8 }}>Missing skills</div>
                  <div style={{ color: "#94a3b8", fontSize: 13, lineHeight: 1.6 }}>
                    These are the job skills that do not appear in your CV yet.
                  </div>
                  <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginTop: 10 }}>
                    {selected.missing_skills?.length ? (
                      selected.missing_skills.map((skill) => (
                        <span key={skill} style={{ background: "#ef444422", color: "#fca5a5", padding: "4px 8px", borderRadius: 999, fontSize: 12, fontWeight: 700 }}>
                          {skill}
                        </span>
                      ))
                    ) : (
                      <span style={{ color: "#64748b", fontSize: 12 }}>No major gaps detected from the listed skills.</span>
                    )}
                  </div>
                </Card>
              </div>

              {coverLetter && (
                <div
                  style={{
                    background: "#060810",
                    padding: 16,
                    borderRadius: 10,
                    color: "#94a3b8",
                    fontSize: 13,
                    lineHeight: 1.7,
                    maxHeight: 300,
                    overflowY: "auto",
                  }}
                >
                  {coverLetter.cover_letter}
                </div>
              )}
            </Card>
          ) : (
            <Card style={{ color: "#64748b", textAlign: "center", padding: 48 }}>Select a job to see details and apply.</Card>
          )}
        </div>
      </div>
    </div>
  );
}
