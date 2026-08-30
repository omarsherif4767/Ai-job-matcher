from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class NormalizedJob(BaseModel):
    title: str
    company: str
    location: Optional[str] = "Remote / Unspecified"
    salary: Optional[str] = "Not Specified"
    employment_type: Optional[str] = "Full-time"
    experience: Optional[str] = "Not Specified"
    skills: List[str] = Field(default_factory=list)
    description: str
    requirements: Optional[str] = ""
    apply_url: str
    source_platform: str
    date_posted: Optional[str] = Field(default_factory=lambda: datetime.utcnow().isoformat())

def normalize_job_data(
    title: str,
    company: str,
    description: str,
    apply_url: str,
    source_platform: str,
    location: str = None,
    salary: str = None,
    employment_type: str = None,
    experience: str = None,
    skills: List[str] = None,
    requirements: str = None
) -> Dict[str, Any]:
    """Helper to return a standardized job dictionary across all scrapers."""
    job = NormalizedJob(
        title=title.strip() if title else "Untitled Position",
        company=company.strip() if company else "Unknown Company",
        location=location.strip() if location else "Remote / Unspecified",
        salary=salary.strip() if salary else "Not Specified",
        employment_type=employment_type.strip() if employment_type else "Full-time",
        experience=experience.strip() if experience else "Not Specified",
        skills=skills if skills else [],
        description=description.strip() if description else "No description provided.",
        requirements=requirements.strip() if requirements else "",
        apply_url=apply_url.strip() if apply_url else "",
        source_platform=source_platform
    )
    return job.model_dump()
