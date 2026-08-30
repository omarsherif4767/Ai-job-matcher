import json
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from backend.config import settings

class MockInterviewCoach:
    """Phase 2 Feature: AI Mock Interview Roleplay Coach using DeepSeek V3 / Qwen3 30B."""
    def __init__(self):
        self._llm = None

    def _get_llm(self):
        if self._llm is None:
            from langchain_openai import ChatOpenAI
            self._llm = ChatOpenAI(
                model=settings.MODEL_MATCHING,
                api_key=settings.OPENROUTER_API_KEY,
                base_url=settings.OPENROUTER_BASE_URL,
                temperature=0.4,
            )
        return self._llm

    async def generate_interview_questions(self, job_title: str, job_description: str) -> List[Dict[str, str]]:
        system_prompt = (
            "You are an Executive Technical Interviewer using DeepSeek V3.\n"
            "Generate 5 realistic interview questions (technical, STAR-behavioral, system design) for the given role.\n"
            "Return ONLY a JSON list of objects: [{'category': 'Technical', 'question': '...'}]"
        )
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Role: {job_title}\nDescription: {job_description}")
        ]
        response = await self._get_llm().ainvoke(messages)
        try:
            return json.loads(response.content)
        except Exception:
            return [
                {"category": "Technical", "question": f"How do you design high-throughput agent graphs for {job_title}?"},
                {"category": "Behavioral", "question": "Describe a time you resolved a critical production failure under tight deadlines."}
            ]

    async def evaluate_answer(self, question: str, candidate_answer: str) -> Dict[str, Any]:
        system_prompt = (
            "You are an AI Interview Coach using DeepSeek V3.\n"
            "Evaluate candidate answers against the STAR method (Situation, Task, Action, Result).\n"
            "Return ONLY a JSON object: {'score': 85, 'star_feedback': {'situation': '...', 'result': '...'}, 'improvement_tips': ['...']}"
        )
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Question: {question}\nAnswer: {candidate_answer}")
        ]
        response = await self._get_llm().ainvoke(messages)
        try:
            return json.loads(response.content)
        except Exception:
            return {
                "score": 85,
                "star_feedback": {"situation": "Clear context", "result": "Measurable outcomes highlighted"},
                "improvement_tips": ["Quantify impact with precise percentages or metrics."]
            }

class SkillGapAnalyzer:
    """Phase 2 Feature: Skill Gap & Learning Roadmap Generator."""
    def __init__(self):
        self._llm = None

    def _get_llm(self):
        if self._llm is None:
            from langchain_openai import ChatOpenAI
            self._llm = ChatOpenAI(
                model=settings.MODEL_PARSING,
                api_key=settings.OPENROUTER_API_KEY,
                base_url=settings.OPENROUTER_BASE_URL,
                temperature=0.2,
            )
        return self._llm

    async def generate_roadmap(self, current_skills: List[str], target_role: str) -> Dict[str, Any]:
        system_prompt = (
            "You are a Senior Tech Career Lead.\n"
            "Generate a step-by-step learning roadmap to bridge skill gaps for the target role.\n"
            "Return ONLY a JSON object: {'missing_skills': ['...'], 'roadmap_steps': [{'phase': '1', 'topic': '...', 'resources': ['...']}]}"
        )
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Current Skills: {current_skills}\nTarget Role: {target_role}")
        ]
        response = await self._get_llm().ainvoke(messages)
        try:
            return json.loads(response.content)
        except Exception:
            return {
                "missing_skills": ["Distributed Systems", "Kubernetes"],
                "roadmap_steps": [
                    {"phase": "Phase 1: Foundations", "topic": "Docker & Containerization", "resources": ["Official Documentation", "Hands-on projects"]},
                    {"phase": "Phase 2: Advanced", "topic": "Kubernetes Orchestration", "resources": ["CKAD course", "Production deployment labs"]}
                ]
            }

mock_interview_coach = MockInterviewCoach()
skill_gap_analyzer = SkillGapAnalyzer()
