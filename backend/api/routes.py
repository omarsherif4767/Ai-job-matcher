from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from backend.tools.parser import resume_parser
from backend.tools.matcher import job_matcher
from backend.tools.cover_letter import cover_letter_generator
from backend.tools.phase2_tools import mock_interview_coach, skill_gap_analyzer
from backend.graph.agent import get_agent_graph, assistant_chat_node
from backend.database.qdrant_client import qdrant_store
from backend.storage import build_dashboard_state, get_job_actions, get_resume_profile, save_job_action, save_recommended_jobs, save_resume_profile

router = APIRouter(prefix="/api")


# --------------------------------------------------------------------------- #
#  Request Schemas                                                              #
# --------------------------------------------------------------------------- #

class ScrapeRequest(BaseModel):
    platform: str   # greenhouse | lever | workable | ashby | remoteok
    board_token: str
    company_name: str

class MatchRequest(BaseModel):
    candidate_profile: Dict[str, Any]
    job_details: Dict[str, Any]

class RecommendJobsRequest(BaseModel):
    candidate_profile: Dict[str, Any]
    country: Optional[str] = "All"
    limit: int = 20

class ResumeProfileSaveRequest(BaseModel):
    profile: Dict[str, Any]
    file_name: Optional[str] = None

class JobActionRequest(BaseModel):
    job: Dict[str, Any]
    status: str

class CoverLetterRequest(BaseModel):
    candidate_profile: Dict[str, Any]
    job_details: Dict[str, Any]

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Dict[str, str]]] = []

class InterviewQuestionsRequest(BaseModel):
    job_title: str
    job_description: str

class EvaluateAnswerRequest(BaseModel):
    question: str
    candidate_answer: str

class SkillGapRequest(BaseModel):
    current_skills: List[str]
    target_role: str

class ApplicationUpdateRequest(BaseModel):
    status: str   # Saved | Applied | Screening | Interviewing | Offer | Rejected
    notes: Optional[str] = None


# --------------------------------------------------------------------------- #
#  Phase 1 Endpoints                                                            #
# --------------------------------------------------------------------------- #

@router.post("/resume/upload")
async def upload_resume(file: UploadFile = File(...)):
    """Upload and parse resume PDF/DOCX into structured JSON (Qwen3 30B via OpenRouter)."""
    contents = await file.read()
    raw_text = resume_parser.extract_text_from_bytes(contents, file.filename)
    if not raw_text:
        raise HTTPException(status_code=400, detail="Could not extract text from uploaded file.")

    parsed_json = await resume_parser.parse_resume_to_json(raw_text)
    embedding = resume_parser.generate_resume_embedding(raw_text)
    save_resume_profile(parsed_json, file.filename)

    return {
        "status": "success",
        "file_name": file.filename,
        "raw_text_length": len(raw_text),
        "parsed_profile": parsed_json,
        "embedding_dimensions": len(embedding)
    }


@router.post("/jobs/scrape")
async def scrape_jobs(request: ScrapeRequest):
    """Trigger Playwright scraper for a given ATS platform and index results into Qdrant."""
    from backend.embeddings.bge_embeddings import embedding_service
    jobs = []
    platform = request.platform.lower()

    if platform == "greenhouse":
        from scrapers.greenhouse import GreenhouseScraper
        scraper = GreenhouseScraper(headless=True)
        jobs = await scraper.scrape_board(request.board_token, request.company_name)
        await scraper.close()
    elif platform == "lever":
        from scrapers.lever import LeverScraper
        scraper = LeverScraper(headless=True)
        jobs = await scraper.scrape_board(request.board_token, request.company_name)
        await scraper.close()
    elif platform == "workable":
        from scrapers.workable import WorkableScraper
        scraper = WorkableScraper(headless=True)
        jobs = await scraper.scrape_board(request.board_token, request.company_name)
        await scraper.close()
    elif platform == "ashby":
        from scrapers.ashby import AshbyScraper
        scraper = AshbyScraper(headless=True)
        jobs = await scraper.scrape_board(request.board_token, request.company_name)
        await scraper.close()
    elif platform == "remoteok":
        from scrapers.remoteok import RemoteOKScraper
        scraper = RemoteOKScraper(headless=True)
        jobs = await scraper.scrape_jobs(tags=request.board_token.split(",") if request.board_token else None)
    elif platform == "smartrecruiters":
        from scrapers.smartrecruiters import SmartRecruitersScraper
        scraper = SmartRecruitersScraper(headless=True)
        jobs = await scraper.scrape_board(request.board_token, request.company_name)
        await scraper.close()
    elif platform == "wellfound":
        from scrapers.wellfound import WellfoundScraper
        scraper = WellfoundScraper(headless=True)
        jobs = await scraper.scrape_jobs(role=request.board_token)
        await scraper.close()
    elif platform == "ycombinator":
        from scrapers.ycombinator import YCombinatorScraper
        scraper = YCombinatorScraper(headless=True)
        jobs = await scraper.scrape_jobs()
        await scraper.close()
    elif platform == "company":
        from scrapers.company import CompanyScraper
        scraper = CompanyScraper(headless=True)
        jobs = await scraper.scrape_company(request.board_token, request.company_name)
        await scraper.close()
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported platform: {request.platform}")

    # Index scraped jobs into Qdrant
    for idx, job in enumerate(jobs):
        vec = embedding_service.embed_text(job.get("description", job.get("title", "")))
        qdrant_store.upsert_job_vector(
            job_id=f"{request.company_name}-{platform}-{idx}",
            vector=vec,
            payload=job
        )

    return {"status": "success", "scraped_count": len(jobs), "jobs": jobs}


@router.post("/jobs/match")
async def match_job(request: MatchRequest):
    """Evaluate candidate vs job using DeepSeek V3 hybrid 5-part scoring."""
    result = await job_matcher.score_candidate_for_job(
        candidate_profile=request.candidate_profile,
        job_details=request.job_details
    )
    return {"status": "success", "match_analysis": result}


@router.post("/cover-letter/generate")
async def generate_cover_letter_api(request: CoverLetterRequest):
    """Generate cover letter + recruiter email + LinkedIn note using DeepSeek V3."""
    materials = await cover_letter_generator.generate_materials(
        candidate_profile=request.candidate_profile,
        job_details=request.job_details
    )
    return {"status": "success", "materials": materials}


@router.post("/chat")
async def chat_api(request: ChatRequest):
    """Talk with Qwen3 30B Instruct AI Career Assistant."""
    messages = [HumanMessage(content=request.message)]
    state = {"messages": messages, "current_step": "init"}
    result_state = await assistant_chat_node(state)
    last_msg = result_state["messages"][-1].content
    return {"status": "success", "reply": last_msg}


@router.get("/agent/run")
async def run_full_agent(resume_text: str):
    """Run the complete LangGraph agent pipeline (parse â†’ search â†’ match â†’ cover letter)."""
    graph = get_agent_graph()
    initial_state = {
        "resume_text": resume_text,
        "messages": [],
        "current_step": "init",
        "parsed_resume": None,
        "resume_embedding": None,
        "scraped_jobs": [],
        "matched_jobs": [],
        "generated_cover_letter": None,
    }
    result = await graph.ainvoke(initial_state)
    return {"status": "success", "final_state": result}






@router.post("/jobs/recommend")
async def recommend_jobs(request: RecommendJobsRequest):
    """Fetch a broader mixed set of Wuzzuf and LinkedIn jobs and rank them against the uploaded CV."""
    profile = request.candidate_profile or {}
    skills = profile.get("skills") or []
    profile_skills = {str(skill).lower() for skill in skills}
    summary = profile.get("summary") or ""
    query_parts = skills[:4] if skills else summary.split()[:4]
    query = " ".join(query_parts).strip() or "software engineer"

    def normalize_country_bucket(job: Dict[str, Any], fallback: str = "all") -> str:
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

    target_countries = [request.country] if request.country and request.country.lower() != "all" else [
        "Egypt",
        "Germany",
        "United States",
        "United Kingdom",
        "France",
        "Netherlands",
        "Spain",
        "Italy",
        "Sweden",
        "Remote",
    ]
    per_source_limit = max(10, request.limit)

    jobs = []
    errors = []

    for target_country in target_countries:
        try:
            from scrapers.wuzzuf import WuzzufScraper
            fetched = await WuzzufScraper().search_jobs(query=query, country=target_country, limit=per_source_limit)
            for job in fetched:
                job["country_bucket"] = normalize_country_bucket(job, fallback="egypt" if target_country.lower() == "egypt" else normalize_country_bucket(job))
            jobs.extend(fetched)
        except Exception as exc:
            errors.append(f"Wuzzuf({target_country}): {exc}")

        try:
            from scrapers.linkedin import LinkedInScraper
            linkedin_country = target_country if target_country.lower() != "remote" else "Remote"
            fetched = await LinkedInScraper().search_jobs(query=query, country=linkedin_country, limit=per_source_limit)
            for job in fetched:
                fallback_bucket = target_country.lower() if target_country.lower() in {"egypt", "germany", "usa", "remote", "europe"} else normalize_country_bucket(job)
                job["country_bucket"] = normalize_country_bucket(job, fallback=fallback_bucket)
            jobs.extend(fetched)
        except Exception as exc:
            errors.append(f"LinkedIn({target_country}): {exc}")

    def score(job: Dict[str, Any]) -> int:
        job_skills = [str(skill).lower() for skill in (job.get("skills") or [])]
        overlap = len([skill for skill in job_skills if skill in profile_skills])
        skill_score = overlap / max(1, len(job_skills)) if job_skills else 0.35
        ats_score = float(profile.get("ats_score") or 78)
        return max(55, min(98, round(ats_score * 0.45 + skill_score * 45 + 10)))

    seen = set()
    ranked_jobs = []
    for job in jobs:
        apply_url = job.get("apply_url")
        if not apply_url or apply_url in seen:
            continue
        seen.add(apply_url)
        job["country_bucket"] = normalize_country_bucket(job, fallback=job.get("country_bucket") or "all")
        job["match_score"] = score(job)
        job_skills = [str(skill).strip() for skill in (job.get("skills") or []) if str(skill).strip()]
        matching_skills = [skill for skill in job_skills if skill.lower() in profile_skills]
        missing_skills = [skill for skill in job_skills if skill.lower() not in profile_skills]
        job["matching_skills"] = matching_skills
        job["missing_skills"] = missing_skills[:5]
        if matching_skills:
            job["why_this_job"] = f"Matches your CV skills: {', '.join(matching_skills[:3])}."
        else:
            job["why_this_job"] = "The title and stack are still close to your background and the role keywords."
        ranked_jobs.append(job)

    ranked_jobs.sort(key=lambda item: item.get("match_score", 0), reverse=True)
    save_recommended_jobs(ranked_jobs, query=query, country=request.country)
    return {
        "status": "success",
        "query": query,
        "country": request.country,
        "errors": errors,
        "jobs": ranked_jobs[: request.limit],
    }
@router.post("/profile/save")
async def save_profile(request: ResumeProfileSaveRequest):
    """Persist the parsed resume profile on the backend."""
    state = save_resume_profile(request.profile, request.file_name)
    return {"status": "success", "resume_profile": state.get("resume_profile")}


@router.get("/profile/latest")
async def latest_profile():
    """Return the most recently saved resume profile."""
    return {"status": "success", "resume_profile": get_resume_profile()}


@router.get("/jobs/actions")
async def list_job_actions():
    """Return saved job status actions."""
    return {"status": "success", "job_actions": get_job_actions()}


@router.post("/jobs/action")
async def update_job_action(request: JobActionRequest):
    """Save a job status such as saved, applied, or rejected."""
    state = save_job_action(request.job, request.status)
    return {"status": "success", "job_actions": state.get("job_actions")}


@router.get("/dashboard/refresh")
async def refresh_dashboard():
    """Return the latest dashboard state from backend persistence."""
    return {"status": "success", **build_dashboard_state()}
# --------------------------------------------------------------------------- #
#  Phase 2 Endpoints                                                            #
# --------------------------------------------------------------------------- #

@router.post("/interview/questions")
async def generate_interview_questions(request: InterviewQuestionsRequest):
    """Generate job-specific interview questions (technical, STAR, system design) via DeepSeek V3."""
    questions = await mock_interview_coach.generate_interview_questions(
        job_title=request.job_title,
        job_description=request.job_description
    )
    return {"status": "success", "questions": questions}


@router.post("/interview/evaluate")
async def evaluate_interview_answer(request: EvaluateAnswerRequest):
    """Evaluate a candidate's interview answer using STAR method (DeepSeek V3)."""
    evaluation = await mock_interview_coach.evaluate_answer(
        question=request.question,
        candidate_answer=request.candidate_answer
    )
    return {"status": "success", "evaluation": evaluation}


@router.post("/skills/gap")
async def analyze_skill_gap(request: SkillGapRequest):
    """Generate a personalized skill gap analysis and learning roadmap for a target role."""
    roadmap = await skill_gap_analyzer.generate_roadmap(
        current_skills=request.current_skills,
        target_role=request.target_role
    )
    return {"status": "success", "roadmap": roadmap}


@router.get("/jobs/search")
async def semantic_job_search(query: str, limit: int = 20):
    """Semantic job search in Qdrant using a natural language query."""
    from backend.embeddings.bge_embeddings import embedding_service
    query_vec = embedding_service.embed_text(query)
    results = qdrant_store.search_similar_jobs(query_vec, limit=limit)
    return {"status": "success", "results": results}

















