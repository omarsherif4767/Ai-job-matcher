from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from backend.graph.state import AgentState
from backend.config import settings


def _make_chat_llm():
    return ChatOpenAI(
        model=settings.MODEL_CHAT,
        api_key=settings.OPENROUTER_API_KEY,
        base_url=settings.OPENROUTER_BASE_URL,
        temperature=0.4,
    )


async def parse_resume_node(state: AgentState) -> AgentState:
    """Node: Extract structured JSON and embeddings from uploaded resume."""
    if state.get("resume_text"):
        from backend.tools.parser import resume_parser
        parsed = await resume_parser.parse_resume_to_json(state["resume_text"])
        embedding = resume_parser.generate_resume_embedding(state["resume_text"])
        state["parsed_resume"] = parsed
        state["resume_embedding"] = embedding
        state["current_step"] = "resume_parsed"
    return state


async def search_jobs_node(state: AgentState) -> AgentState:
    """Node: Semantic search in Qdrant for top 30 job candidates."""
    if state.get("resume_embedding"):
        from backend.database.qdrant_client import qdrant_store
        results = qdrant_store.search_similar_jobs(state["resume_embedding"], limit=30)
        state["scraped_jobs"] = [r["payload"] for r in results]
        state["current_step"] = "jobs_searched"
    return state


async def match_jobs_node(state: AgentState) -> AgentState:
    """Node: Evaluate jobs using DeepSeek V3 5-part match scoring."""
    if state.get("parsed_resume") and state.get("scraped_jobs"):
        from backend.tools.matcher import job_matcher
        matched = []
        for job in state["scraped_jobs"][:5]:
            score_data = await job_matcher.score_candidate_for_job(
                candidate_profile=state["parsed_resume"],
                job_details=job
            )
            job_copy = dict(job)
            job_copy["match_analysis"] = score_data
            matched.append(job_copy)
        state["matched_jobs"] = matched
        state["current_step"] = "jobs_matched"
    return state


async def generate_cover_letter_node(state: AgentState) -> AgentState:
    """Node: Generate tailored cover letter & recruiter outreach templates."""
    if state.get("parsed_resume") and state.get("matched_jobs"):
        from backend.tools.cover_letter import cover_letter_generator
        top_job = state["matched_jobs"][0]
        materials = await cover_letter_generator.generate_materials(
            candidate_profile=state["parsed_resume"],
            job_details=top_job
        )
        state["generated_cover_letter"] = materials["cover_letter"]
        state["current_step"] = "cover_letter_generated"
    return state


async def assistant_chat_node(state: AgentState) -> AgentState:
    """Node: Interactive career assistant conversing with candidate."""
    system_prompt = (
        "You are A Job in AI Era — an intelligent, friendly AI Career Assistant powered by a single LangGraph agent.\n"
        "You assist users with resume optimization, job discovery, application tracking, interview prep, and career strategy.\n"
        "Provide helpful, concise, and highly relevant guidance."
    )
    messages = [SystemMessage(content=system_prompt)] + state.get("messages", [])

    try:
        chat_llm = _make_chat_llm()
        response = await chat_llm.ainvoke(messages)
        state["messages"].append(response)
    except Exception as e:
        print(f"[assistant_chat_node] LLM call failed ({e}). Using intelligent fallback response.")
        user_msg = state.get("messages", [])[-1].content if state.get("messages") else ""
        
        # Rule-based intelligent career assistant responses
        user_msg_lower = user_msg.lower()
        if "intern" in user_msg_lower:
            reply_text = "I recommend targeting AI/ML software engineering internships at companies like OpenAI, Anthropic, Hugging Face, or YC startups. Highlight hands-on projects using PyTorch, FastAPI, and LangChain on your resume."
        elif "match" in user_msg_lower or "score" in user_msg_lower:
            reply_text = "Your job match score is calculated using a 5-part hybrid formula: 40% Semantic Vector Similarity, 30% Skills Match, 15% Experience Match, 10% Education, and 5% Preferred Qualifications."
        elif "skill" in user_msg_lower or "learn" in user_msg_lower:
            reply_text = "Top in-demand skills in the AI Era include: Python, PyTorch, Docker, Kubernetes, Vector Databases (Qdrant), RAG architecture, and Agentic frameworks like LangGraph."
        else:
            reply_text = f"Great question about '{user_msg}'! To maximize your opportunities in the AI Era, ensure your resume highlights quantifiable project achievements, modern AI toolstacks (Python, LangChain, PyTorch), and active portfolio links."

        state["messages"].append(AIMessage(content=reply_text))

    state["current_step"] = "chat_response_ready"
    return state


def build_agent_graph():
    """Build and compile the single LangGraph Agent workflow."""
    builder = StateGraph(AgentState)
    builder.add_node("parse_resume", parse_resume_node)
    builder.add_node("search_jobs", search_jobs_node)
    builder.add_node("match_jobs", match_jobs_node)
    builder.add_node("generate_cover_letter", generate_cover_letter_node)
    builder.add_node("assistant_chat", assistant_chat_node)

    builder.set_entry_point("parse_resume")
    builder.add_edge("parse_resume", "search_jobs")
    builder.add_edge("search_jobs", "match_jobs")
    builder.add_edge("match_jobs", "generate_cover_letter")
    builder.add_edge("generate_cover_letter", END)

    return builder.compile()


# Lazy-compiled graph — use get_agent_graph() to access it
_agent_graph = None


def get_agent_graph():
    global _agent_graph
    if _agent_graph is None:
        _agent_graph = build_agent_graph()
    return _agent_graph
