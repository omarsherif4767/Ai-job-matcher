from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
STATE_PATH = DATA_DIR / "app_state.json"
STATE_LOCK = Lock()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _infer_country_bucket(job: Dict[str, Any], fallback: str = "all") -> str:
    job_text = " ".join([
        str(job.get("country") or ""),
        str(job.get("location") or ""),
        str(job.get("source_location") or ""),
        str(job.get("workplace_type") or ""),
        str(job.get("title") or ""),
        str(job.get("company") or ""),
        str(job.get("description") or ""),
        str(job.get("source_platform") or ""),
    ]).lower()
    buckets = {
        "egypt": ["egypt", "cairo", "giza", "alexandria", "maadi", "new cairo"],
        "germany": ["germany", "berlin", "munich", "hamburg", "frankfurt", "cologne"],
        "usa": ["united states", "usa", "u.s.", "new york", "san francisco", "seattle", "austin", "boston", "chicago"],
        "remote": ["remote", "work from home", "wfh", "distributed"],
        "europe": ["europe", "united kingdom", "uk", "london", "manchester", "edinburgh", "france", "paris", "spain", "madrid", "barcelona", "italy", "milan", "rome", "netherlands", "amsterdam", "poland", "warsaw", "portugal", "lisbon", "ireland", "dublin", "sweden", "stockholm", "norway", "oslo", "denmark", "copenhagen", "finland", "helsinki", "belgium", "brussels"],
    }
    for bucket, needles in buckets.items():
        if any(needle in job_text for needle in needles):
            return bucket
    return fallback


def _default_state() -> Dict[str, Any]:
    return {
        "resume_profile": None,
        "resume_history": [],
        "recommended_jobs": [],
        "job_actions": {},
        "updated_at": _utc_now(),
    }


def _ensure_state_file() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not STATE_PATH.exists():
        STATE_PATH.write_text(json.dumps(_default_state(), indent=2), encoding="utf-8")


def load_state() -> Dict[str, Any]:
    with STATE_LOCK:
        _ensure_state_file()
        try:
            return json.loads(STATE_PATH.read_text(encoding="utf-8"))
        except Exception:
            state = _default_state()
            STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")
            return state


def save_state(state: Dict[str, Any]) -> Dict[str, Any]:
    with STATE_LOCK:
        _ensure_state_file()
        state["updated_at"] = _utc_now()
        STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")
        return deepcopy(state)


def save_resume_profile(profile: Dict[str, Any], file_name: Optional[str] = None) -> Dict[str, Any]:
    state = load_state()
    profile_copy = deepcopy(profile or {})
    if file_name:
        profile_copy["file_name"] = file_name
    profile_copy["saved_at"] = _utc_now()
    state["resume_profile"] = profile_copy
    history = state.get("resume_history") or []
    history.insert(0, profile_copy)
    state["resume_history"] = history[:10]
    return save_state(state)


def get_resume_profile() -> Optional[Dict[str, Any]]:
    return load_state().get("resume_profile")


def save_recommended_jobs(jobs: List[Dict[str, Any]], query: str = "", country: str = "All") -> Dict[str, Any]:
    state = load_state()
    normalized_jobs = []
    for job in jobs or []:
        job_copy = deepcopy(job)
        job_copy["country_bucket"] = job_copy.get("country_bucket") or _infer_country_bucket(job_copy)
        normalized_jobs.append(job_copy)
    state["recommended_jobs"] = normalized_jobs
    state["recommendation_query"] = query
    state["recommendation_country"] = country
    return save_state(state)


def get_recommended_jobs() -> List[Dict[str, Any]]:
    return load_state().get("recommended_jobs") or []


def save_job_action(job: Dict[str, Any], status: str) -> Dict[str, Any]:
    state = load_state()
    job_copy = deepcopy(job or {})
    key = job_copy.get("apply_url") or job_copy.get("job_id") or job_copy.get("id") or f"job-{len(state.get('job_actions') or {}) + 1}"
    actions = state.get("job_actions") or {}
    actions[key] = {
        "status": status,
        "job": job_copy,
        "updated_at": _utc_now(),
    }
    state["job_actions"] = actions
    return save_state(state)


def get_job_actions() -> Dict[str, Any]:
    return load_state().get("job_actions") or {}


def build_dashboard_state() -> Dict[str, Any]:
    state = load_state()
    resume_profile = state.get("resume_profile") or {}
    recommended_jobs = state.get("recommended_jobs") or []
    job_actions = state.get("job_actions") or {}

    status_counts = {"saved": 0, "applied": 0, "rejected": 0}
    for action in job_actions.values():
        status = str(action.get("status") or "").lower()
        if status in status_counts:
            status_counts[status] += 1

    skills = resume_profile.get("skills") or []
    ats_score = resume_profile.get("ats_score")
    best_match = max((int(job.get("match_score", 0)) for job in recommended_jobs), default=0)
    enriched_jobs = []
    for job in recommended_jobs:
        job_copy = deepcopy(job)
        job_copy["country_bucket"] = job_copy.get("country_bucket") or _infer_country_bucket(job_copy)
        enriched_jobs.append(job_copy)

    return {
        "resume_profile": resume_profile or None,
        "counts": {
            "jobs_ranked": len(recommended_jobs),
            "best_matches": sum(1 for job in recommended_jobs if int(job.get("match_score", 0)) >= 80),
            "avg_match_score": round(sum(int(job.get("match_score", 0)) for job in recommended_jobs) / max(1, len(recommended_jobs))),
            "cv_skills_found": len(skills),
            "saved_jobs": status_counts["saved"],
            "applied_jobs": status_counts["applied"],
            "rejected_jobs": status_counts["rejected"],
            "ats_score": ats_score,
            "top_match": best_match,
        },
        "recommended_jobs": enriched_jobs,
        "job_actions": job_actions,
        "updated_at": state.get("updated_at"),
    }
