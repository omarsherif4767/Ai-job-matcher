# Ai job matcher 

Last updated: August 30, 2026

## What This Project Is

Antigravity AI is an AI-powered career intelligence app built around a resume-first workflow.
The user uploads a CV, the backend parses it into structured profile data, the system builds job recommendations,
and the frontend lets the user review, save, apply, and generate cover letters from the matched jobs.

The project is designed to feel like a real product rather than a demo:

- resume upload and parsing
- job recommendation and filtering
- saved/applied/rejected tracking
- job detail view with direct apply links
- cover letter generation
- dashboard analytics
- AI chat assistant

## Main Product Flow

1. The user uploads a resume PDF or DOCX.
2. The backend extracts text and turns it into structured JSON.
3. The resume profile is saved in local backend state.
4. The recommendation endpoint builds a job feed from scraper sources.
5. Each job is scored against the resume.
6. The frontend displays the ranked feed and local filters.
7. The user can save a job, mark it applied, or reject it.
8. The dashboard reflects the saved state and resume metrics.

## Backend Overview

The backend is FastAPI-based and acts as the central service layer.

### Main backend files

- ackend/main.py - FastAPI app entry point
- ackend/api/routes.py - REST endpoints
- ackend/storage.py - local persistence for resume profile, jobs, and job actions
- ackend/tools/parser.py - resume text extraction and structured parsing
- ackend/tools/matcher.py - job scoring / matching
- ackend/tools/cover_letter.py - cover letter generation
- ackend/tools/phase2_tools.py - interview and skill-gap helpers
- ackend/database/qdrant_client.py - vector search integration

### Important backend endpoints

- POST /api/resume/upload
  - uploads a resume file
  - extracts text
  - parses structured profile data
  - saves the resume profile

- POST /api/jobs/recommend
  - builds the recommendation feed
  - collects jobs from scrapers
  - ranks jobs against the uploaded CV
  - stores the recommended jobs in backend state

- GET /api/dashboard/refresh
  - returns the latest dashboard state
  - includes resume profile, recommendation stats, and cached jobs

- GET /api/profile/latest
  - returns the last saved resume profile

- GET /api/jobs/actions
  - returns saved/applied/rejected job actions

- POST /api/jobs/action
  - saves a job status update

- POST /api/cover-letter/generate
  - generates application materials for a selected job

## Storage Layer

The project uses local JSON state for the app experience in addition to the larger database stack.

### Local state file

ackend/data/app_state.json

It stores:

- esume_profile
- esume_history
- ecommended_jobs
- job_actions
- timestamps and recommendation metadata

### Why this matters

This local state is what makes the dashboard and saved-job experience persistent between refreshes.
It also lets the frontend render a stable job feed without depending on a fresh fetch every time.

## Job Recommendation Logic

The recommendation flow now tries to behave like a production app:

- it uses the parsed resume profile as the source of truth
- jobs are ranked by match score
- job cards carry:
  - match_score
  - matching_skills
  - missing_skills
  - ole_signals
  - why_this_job
  - country_bucket

### Current recommendation behavior

- the app keeps a cached job pool
- the frontend filters that pool locally by status and country bucket
- All means the full available pool
- country filters are bucketed as:
  - egypt
  - germany
  - usa
  - europe
  - emote

### Why the bucketing exists

The job sources do not always provide a clean country field.
Many job listings only expose a location string like:

- Cairo, Egypt
- Chicago, IL
- Berlin, Germany
- Helsinki, Finland
- Remote

The project therefore infers a bucket from the title, location, company, and description.
That keeps filters consistent even when the source data is messy.

## Frontend Overview

The frontend is a Next.js app under rontend/.

### Main UI screens

- dashboard
- upload page
- jobs feed
- chat assistant

### Jobs page behavior

The jobs page is now the core working screen:

- loads the resume profile
- loads the cached recommendation feed
- filters by status:
  - All
  - Saved
  - Applied
  - Rejected
- filters by country bucket:
  - All
  - Egypt
  - Germany
  - USA
  - Europe
  - Remote
- shows direct apply links
- shows a job explanation panel
- shows matching and missing skills
- shows a save / applied / rejected workflow

### Important jobs page detail

The page now prefers the saved backend feed first.
If the saved cache is empty, it falls back to the recommendation endpoint.
That makes the app more stable and less dependent on one fetch.

## Dashboard Behavior

The dashboard shows:

- total jobs ranked
- best matches
- average match score
- CV skill count
- saved jobs
- applied jobs
- rejected jobs
- ATS score

The saved-jobs dashboard card links to the saved jobs view, which is important for real usage.

## Scrapers

The scraper layer is what populates the feed.

### Main scraper files

- scrapers/wuzzuf.py
- scrapers/linkedin.py
- scrapers/greenhouse.py
- scrapers/lever.py
- scrapers/workable.py
- scrapers/ashby.py
- scrapers/remoteok.py
- scrapers/smartrecruiters.py
- scrapers/wellfound.py
- scrapers/ycombinator.py
- scrapers/company.py
- scrapers/normalizer.py

### Scraper design

Each scraper should return a normalized job object with fields such as:

- title
- company
- location
- description
- apply_url
- source_platform
- skills

### Current practical reality

The app currently relies heavily on LinkedIn and Wuzzuf style job data.
The scraper normalization and country bucketing are important because the raw job data is inconsistent across sources.

## Matching and Explanation Logic

The app does not just sort by a raw similarity score.
It also explains the result.

### Job card fields

- match_score
- matching_skills
- missing_skills
- ole_signals
- why_this_job

### Why this is useful

This makes the app feel like a career tool rather than a plain list of jobs.
The user can see:

- why the job appears
- which CV skills matched
- which skills are still missing

## Cover Letter Generation

The cover letter flow is job-specific:

- the user picks a job
- the backend receives the job + profile
- the model generates a tailored cover letter
- the result is shown directly in the job detail panel

## Current Improvements That Were Added

These are the most important practical improvements made while stabilizing the project:

- saved jobs now persist in backend state
- the dashboard saved card links to the saved jobs feed
- job explanations are less static
- the filter buttons use stable country buckets
- the feed loads from cached dashboard jobs first
- the backend stores a country bucket for each job
- the app no longer depends on one brittle search response for the whole UI

## How To Run It

### Backend

From the project root:

`powershell
python run.py
`

If dependencies are missing:

`powershell
pip install -r backend/requirements.txt
playwright install chromium
`

### Frontend

`powershell
cd frontend
npm install
npm run dev
`

### Expected local URLs

- backend: http://localhost:8000
- frontend: http://localhost:3000

## Important Files To Know

If someone wants to understand or extend the app, these are the main files to read first:

- ackend/api/routes.py
- ackend/storage.py
- ackend/tools/parser.py
- rontend/app/page.js
- rontend/app/jobs/page.js
- rontend/app/upload/page.js
- scrapers/wuzzuf.py
- scrapers/linkedin.py

## Known Product Shape

This project is now closer to a real app because it has:

- persistent resume data
- persistent job actions
- a cached recommendation pool
- explainable job ranking
- direct apply links
- saved/applied/rejected tracking
- dashboard analytics

## Notes For Future Work

Good next steps would be:

- add a richer saved-jobs page with search and notes
- add better source diversity beyond LinkedIn
- show country badges more explicitly in the card UI
- improve Europe/USA source coverage at the scraper level
- add tests for country bucketing and dashboard persistence
- add a profile summary panel for the parsed CV data
