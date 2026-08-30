import json
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from backend.config import settings

class CoverLetterGenerator:
    """
    Generates personalized cover letters, recruiter outreach emails,
    and LinkedIn connection notes using DeepSeek V3 via OpenRouter.
    """
    def __init__(self):
        self._llm = None

    def _get_llm(self):
        if self._llm is None:
            from langchain_openai import ChatOpenAI
            self._llm = ChatOpenAI(
                model=settings.MODEL_COVER_LETTER,
                api_key=settings.OPENROUTER_API_KEY,
                base_url=settings.OPENROUTER_BASE_URL,
                temperature=0.3,
            )
        return self._llm

    async def generate_materials(
        self,
        candidate_profile: Dict[str, Any],
        job_details: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generates tailored cover letter, cold recruiter email, and LinkedIn message."""
        
        system_prompt = (
            "You are a professional Executive Career Strategist using DeepSeek V3.\n"
            "Generate customized application materials based ONLY on verified candidate accomplishments and target job details.\n"
            "Return ONLY a JSON object with this structure:\n"
            "{\n"
            '  "cover_letter": "Formal, high-impact cover letter text...",\n'
            '  "recruiter_email": "Subject: ... \\n\\nDear Hiring Team...",\n'
            '  "linkedin_message": "Concise 300-character LinkedIn connection note..."\n'
            "}"
        )

        human_content = (
            f"Candidate Info:\n{json.dumps(candidate_profile, indent=2)}\n\n"
            f"Target Job:\n{json.dumps(job_details, indent=2)}"
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
                "cover_letter": f"Dear Hiring Manager,\n\nI am writing to express my enthusiastic interest in the {job_details.get('title', 'Position')} role at {job_details.get('company', 'your company')}. With my background in technology and software development, I am confident in my ability to contribute effectively to your team.\n\nSincerely,\nCandidate",
                "recruiter_email": f"Subject: Application for {job_details.get('title', 'Position')} - Candidate\n\nHi Hiring Team,\n\nI recently submitted my application for the {job_details.get('title', 'Position')} role at {job_details.get('company', 'your company')}. I would love to connect and share more about my qualifications.\n\nBest regards,\nCandidate",
                "linkedin_message": f"Hi! I noticed the {job_details.get('title', 'Position')} opening at {job_details.get('company', 'your company')} and would love to connect and introduce myself."
            }

cover_letter_generator = CoverLetterGenerator()
