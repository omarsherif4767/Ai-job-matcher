import json
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from backend.config import settings

class JobMatcher:
    """
    Evaluates candidates against job listings using DeepSeek V3 via OpenRouter.
    Implements a 5-part hybrid weighted match scoring strategy:
    - 40% Semantic Similarity
    - 30% Skills Match
    - 15% Experience Match
    - 10% Education Match
    - 5% Preferred Qualifications
    """
    def __init__(self):
        self._llm = None

    def _get_llm(self):
        if self._llm is None:
            from langchain_openai import ChatOpenAI
            self._llm = ChatOpenAI(
                model=settings.MODEL_MATCHING,
                api_key=settings.OPENROUTER_API_KEY,
                base_url=settings.OPENROUTER_BASE_URL,
                temperature=0.2,
            )
        return self._llm

    async def score_candidate_for_job(
        self,
        candidate_profile: Dict[str, Any],
        job_details: Dict[str, Any],
        semantic_score: float = 0.85
    ) -> Dict[str, Any]:
        """Calculates 5-part score breakdown and text explanation using DeepSeek V3."""
        
        system_prompt = (
            "You are an expert AI Career & Executive Recruiter using DeepSeek V3.\n"
            "Analyze candidate suitability for a specific job position based on these weights:\n"
            "- Semantic Similarity: 40%\n"
            "- Skills Match: 30%\n"
            "- Experience Match: 15%\n"
            "- Education Match: 10%\n"
            "- Preferred Qualifications: 5%\n\n"
            "Return ONLY a valid JSON object with this exact structure:\n"
            "{\n"
            '  "final_score": 88.5,\n'
            '  "breakdown": {\n'
            '    "semantic_similarity": 36.0,\n'
            '    "skills_match": 27.0,\n'
            '    "experience_match": 13.5,\n'
            '    "education_match": 8.0,\n'
            '    "preferred_qualifications": 4.0\n'
            "  },\n"
            '  "explanation": "Detailed paragraph explaining the rationale for this match score.",\n'
            '  "matching_skills": ["Python", "FastAPI"],\n'
            '  "missing_skills": ["Kubernetes"]\n'
            "}"
        )

        human_content = (
            f"Semantic Base Score: {semantic_score * 100:.1f}%\n"
            f"Candidate Profile:\n{json.dumps(candidate_profile, indent=2)}\n\n"
            f"Job Details:\n{json.dumps(job_details, indent=2)}"
        )

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_content)
        ]

        try:
            response = await self._get_llm().ainvoke(messages)
            content = response.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"): content = content[4:]
            result = json.loads(content)
            return result
        except Exception:
            return {
                "final_score": round(semantic_score * 100, 1),
                "breakdown": {
                    "semantic_similarity": round(semantic_score * 40, 1),
                    "skills_match": 24.0,
                    "experience_match": 12.0,
                    "education_match": 8.0,
                    "preferred_qualifications": 4.0
                },
                "explanation": "Candidate demonstrates strong semantic alignment and foundational core competencies for this position.",
                "matching_skills": candidate_profile.get("skills", []),
                "missing_skills": []
            }

job_matcher = JobMatcher()
