# 🚀 Antigravity AI --- Final Implementation Plan

## Overview

Antigravity AI is an AI-powered career intelligence platform built
around a **single LangGraph agent**. The agent understands a user's
resume, continuously discovers job opportunities through web scraping,
matches jobs intelligently, generates tailored application materials,
and provides an interactive chat interface.

------------------------------------------------------------------------

# Objectives

-   Upload and analyze a CV
-   Extract structured skills and experience
-   Scrape the latest jobs from company career pages
-   Match jobs using embeddings + LLM reasoning
-   Generate personalized cover letters
-   Chat with an AI career assistant
-   Visualize insights in a dashboard

------------------------------------------------------------------------

# Tech Stack

## Frontend

-   Next.js
-   Tailwind CSS
-   shadcn/ui
-   Recharts

## Backend

-   FastAPI

## AI Framework & Provider

- **LangGraph** (Single stateful agent orchestration)
- **LangChain** (Tool integration & memory)
- **OpenRouter API** (Unified API provider for routing all LLM model requests)

### Models (All routed via OpenRouter API)

| Task | Model | Provider via OpenRouter |
| :--- | :--- | :--- |
| **Chat Assistant** | Qwen3 30B Instruct | OpenRouter |
| **Resume Parsing** | Qwen3 30B | OpenRouter |
| **Job Matching** | DeepSeek V3 | OpenRouter |
| **Cover Letter Generation** | DeepSeek V3 | OpenRouter |
| **Mock Interview Coaching** | DeepSeek V3 / Qwen3 30B | OpenRouter |

------------------------------------------------------------------------

# Storage

## PostgreSQL

Tables:

-   Users
-   Resumes
-   Jobs
-   Companies
-   Applications
-   CoverLetters
-   ChatHistory

## Vector Database

-   Qdrant

Embedding Model:

-   BAAI/bge-small-en-v1.5

------------------------------------------------------------------------

# Scraping Architecture

## Primary Tool

**Playwright**

Playwright is the main scraping engine because it can:

-   Render JavaScript websites
-   Handle infinite scrolling
-   Wait for dynamic content
-   Interact with buttons and filters
-   Navigate modern career websites reliably

## Supporting Libraries

-   BeautifulSoup
-   lxml
-   Trafilatura
-   Pydantic

------------------------------------------------------------------------

# Websites to Scrape

## ATS Platforms (Highest Priority)

-   Greenhouse
-   Lever
-   Workable
-   Ashby
-   SmartRecruiters

## Startup Job Boards

-   Wellfound
-   RemoteOK
-   Y Combinator Jobs

## Company Career Pages

Examples:

-   OpenAI
-   Anthropic
-   Microsoft
-   NVIDIA
-   Google
-   Meta
-   Databricks
-   Snowflake
-   Hugging Face
-   Scale AI

> Avoid LinkedIn, Indeed, and Glassdoor in the first version because
> they have strong anti-bot protections and are difficult to maintain.

------------------------------------------------------------------------

# Scraper Design

``` text
BaseScraper
│
├── GreenhouseScraper
├── LeverScraper
├── WorkableScraper
├── AshbyScraper
├── RemoteOKScraper
└── CompanyScraper
```

Each scraper returns a normalized job object containing:

-   Job Title
-   Company
-   Location
-   Salary (if available)
-   Employment Type
-   Experience
-   Skills
-   Description
-   Requirements
-   Apply Link
-   Date Posted

------------------------------------------------------------------------

# LangGraph Workflow

``` text
START
 │
Upload Resume
 │
Parse Resume
 │
Extract Skills
 │
Generate Resume Embedding
 │
Scrape Jobs (Playwright)
 │
Normalize Job Data
 │
Generate Job Embeddings
 │
Semantic Search (Qdrant)
 │
Top 30 Jobs
 │
DeepSeek V3 Analysis
 │
Generate Match Score
 │
Generate Cover Letter
 │
Save Results
 │
Dashboard
 │
Chat
```

------------------------------------------------------------------------

# Agent Tools

-   parse_resume()
-   scrape_jobs()
-   search_jobs()
-   match_resume()
-   explain_match()
-   generate_cover_letter()
-   resume_feedback()
-   skill_gap_analysis()
-   company_summary()
-   dashboard()
-   application_tracker()

------------------------------------------------------------------------

# Matching Strategy

Hybrid scoring:

-   40% Semantic Similarity
-   30% Skills Match
-   15% Experience Match
-   10% Education Match
-   5% Preferred Qualifications

The LLM explains the score rather than generating an arbitrary
percentage.

------------------------------------------------------------------------

# Resume Processing

Extract:

-   Education
-   Experience
-   Projects
-   Skills
-   Certifications
-   Languages

Generate:

-   Structured JSON
-   Embeddings
-   ATS Score
-   Resume Improvement Suggestions

------------------------------------------------------------------------

# Cover Letter Generation

Generate:

-   Personalized Cover Letter
-   Recruiter Email
-   LinkedIn Message

Based only on verified resume information and the selected job
description.

------------------------------------------------------------------------

# Dashboard

## Statistics

-   Total Jobs Scraped
-   Best Matches
-   Average Match Score
-   Saved Jobs
-   Applied Jobs
-   Interviews
-   Rejections

## Analytics

-   Most Requested Skills
-   Top Hiring Companies
-   Jobs by Country
-   Jobs by Employment Type
-   Salary Distribution
-   Match Score Distribution
-   Remote vs On-site

------------------------------------------------------------------------

# Chat Examples

-   Find remote AI internships.
-   Show jobs above a 90% match.
-   Explain why this job scored 72%.
-   Generate another cover letter.
-   Which skills am I missing?
-   Show only jobs in Germany.
-   Summarize this company.
-   What should I learn next?

------------------------------------------------------------------------

# Project Structure

``` text
backend/
├── api/
├── agents/
├── graph/
├── tools/
│   ├── scraper/
│   ├── matcher/
│   ├── parser/
│   ├── cover_letter/
│   └── dashboard/
├── database/
├── embeddings/
└── models/

frontend/
├── app/
├── components/
├── dashboard/
├── chat/
└── upload/

scrapers/
├── base_scraper.py
├── greenhouse.py
├── lever.py
├── workable.py
├── ashby.py
├── remoteok.py
└── company.py
```

------------------------------------------------------------------------

# Phase 2 Specifications

Phase 2 builds upon the core foundation by introducing automation, advanced AI coaching, cross-platform extensions, and deep analytical intelligence.

------------------------------------------------------------------------

## 1. Automated & Scheduled Job Scraping

- **Cron / Task Queue Infrastructure**: Integration with APScheduler / Celery / Redis to run recurring scrapers automatically (e.g., daily or hourly runs).
- **Delta Scraping & De-duplication**: Scrape only new or updated postings across target ATS platforms to reduce bandwidth and processing overhead.
- **Smart Push Notifications & Job Alerts**: Auto-match new job entries against active user profiles and send instant alerts (Email / Web push) for matches scoring above 85%.

------------------------------------------------------------------------

## 2. Interactive AI Interview Preparation

- **Job-Specific Question Generation**: Dynamic creation of technical, behavioral, and system design interview questions derived directly from target Job Descriptions and the candidate's resume.
- **Interactive Mock Interview Agent**: Roleplay conversational mode where the AI acts as an interviewer, evaluates candidate responses using the STAR method (Situation, Task, Action, Result), and provides real-time scoring and constructive feedback.
- **Answer Optimization & Rubric**: Instant suggestions to refine candidate answers for impact, clarity, and keyword alignment.

------------------------------------------------------------------------

## 3. Resume Versioning & Tailoring Engine

- **Multi-Version Resume Management**: Support for maintaining multiple resume variations tailored for distinct roles (e.g., *AI/ML Engineer*, *Full Stack Developer*, *Tech Lead*).
- **Targeted ATS Optimization**: Smart suggestions to reframe bullet points and highlight relevant skills specifically aligned with selected job descriptions (strictly avoiding fabrication).
- **Diff & Version Comparison**: Visual diff viewer to compare resume revisions and export tailored PDFs/Word documents.

------------------------------------------------------------------------

## 4. Deep Company Intelligence & Research Agent

- **Autonomous Web Research**: Specialized agent tool that harvests company news, funding rounds, engineering blog summaries, tech stack details, and interview culture insights.
- **Company Knowledge RAG**: Index company research into vector storage to allow targeted user inquiries during job preparation (e.g., *"What recent open-source projects has Anthropic released?"*).

------------------------------------------------------------------------

## 5. Skill-Gap Analysis & Personalized Learning Roadmaps

- **Competency Gap Identification**: Automated evaluation comparing candidate skills against industry standards for target job roles.
- **Custom Learning Roadmaps**: AI-curated step-by-step learning paths including recommended topics, courses, open-source projects, and key concepts required to bridge identified skill gaps.

------------------------------------------------------------------------

## 6. Browser Extension (Manifest V3)

- **One-Click Job Clipping**: Chrome / Firefox extension allowing users to save job postings from any web page directly into Antigravity AI with automatic page parsing.
- **On-Page Match Score Widget**: Floating overlay on job boards displaying live match scores, key requirements, and quick-apply helpers without leaving the target site.

------------------------------------------------------------------------

## 7. Application Tracker & Reminder Lifecycle

- **Kanban Board Workflow**: Interactive management of application stages (*Saved*, *Applied*, *Screening*, *Interviewing*, *Offer*, *Rejected*).
- **Automated Follow-Up Reminders**: Smart scheduled reminders for follow-up emails, interview prep milestones, and response deadline tracking.
- **Recruiter Outreach Templates**: Automated draft generation for recruiter follow-ups, LinkedIn connection requests, and post-interview thank-you notes.

------------------------------------------------------------------------

## 8. Phase 2 Database Schema Extensions

New PostgreSQL tables added to support Phase 2 features:

- `ResumeVersions` (id, user_id, title, content_json, created_at)
- `InterviewSessions` (id, application_id, user_id, transcript_json, score, feedback, created_at)
- `SkillGapRoadmaps` (id, user_id, target_role, missing_skills_json, roadmap_steps_json, progress)
- `CompanyIntelligence` (id, company_name, tech_stack_json, recent_news_json, culture_summary, updated_at)
- `ScheduledScrapes` (id, platform_name, interval_minutes, last_run_at, status)
- `UserNotifications` (id, user_id, type, payload_json, read_status, created_at)

------------------------------------------------------------------------

## 9. Phase 2 LangGraph Tools Addition

- `schedule_job_alerts()`
- `start_mock_interview()`
- `evaluate_interview_answer()`
- `generate_resume_variant()`
- `analyze_skill_gap()`
- `generate_learning_roadmap()`
- `research_company()`
- `clip_web_job()`

------------------------------------------------------------------------

------------------------------------------------------------------------

# Why Antigravity AI?

Antigravity AI combines:

-   LangGraph AI Agent
-   LangChain
-   OpenRouter
-   Playwright-based web scraping
-   Semantic search with Qdrant
-   Explainable AI matching
-   Resume intelligence
-   Personalized cover letters
-   Analytics dashboard

The project demonstrates modern AI engineering, browser automation,
information retrieval, full-stack development, and LLM orchestration in
one production-style application.
