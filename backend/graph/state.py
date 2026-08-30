from typing import List, Dict, Any, Optional, Annotated
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    """
    Unified state for the single LangGraph Agent.
    Tracks user resume, parsed profile, job recommendations, matched scores,
    generated cover letters, and chat conversation history.
    """
    messages: Annotated[List[BaseMessage], operator.add]
    user_id: Optional[str]
    resume_text: Optional[str]
    parsed_resume: Optional[Dict[str, Any]]
    resume_embedding: Optional[List[float]]
    scraped_jobs: Optional[List[Dict[str, Any]]]
    matched_jobs: Optional[List[Dict[str, Any]]]
    selected_job_id: Optional[str]
    generated_cover_letter: Optional[str]
    mock_interview_session: Optional[Dict[str, Any]]
    skill_gap_analysis: Optional[Dict[str, Any]]
    current_step: str
