import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.database.session import Base

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")
    chat_histories = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")
    resume_versions = relationship("ResumeVersion", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("UserNotification", back_populates="user", cascade="all, delete-orphan")


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    raw_text = Column(Text, nullable=True)
    parsed_json = Column(JSON, nullable=True)
    ats_score = Column(Float, nullable=True)
    suggestions = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="resumes")


class Company(Base):
    __tablename__ = "companies"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), unique=True, nullable=False, index=True)
    website = Column(String(255), nullable=True)
    careers_page = Column(String(255), nullable=True)
    tech_stack = Column(JSON, nullable=True)
    summary = Column(Text, nullable=True)

    jobs = relationship("Job", back_populates="company")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=True)
    title = Column(String(255), nullable=False, index=True)
    location = Column(String(255), nullable=True)
    salary_range = Column(String(100), nullable=True)
    employment_type = Column(String(100), nullable=True)
    experience_level = Column(String(100), nullable=True)
    skills = Column(JSON, nullable=True)
    description = Column(Text, nullable=False)
    requirements = Column(Text, nullable=True)
    apply_url = Column(String(500), nullable=False, unique=True)
    source_platform = Column(String(100), nullable=True)
    date_posted = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="jobs")
    applications = relationship("Application", back_populates="job")


class Application(Base):
    __tablename__ = "applications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    job_id = Column(String(36), ForeignKey("jobs.id"), nullable=False)
    status = Column(String(50), default="Saved")  # Saved, Applied, Screening, Interviewing, Offer, Rejected
    match_score = Column(Float, nullable=True)
    match_explanation = Column(JSON, nullable=True)
    notes = Column(Text, nullable=True)
    applied_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="applications")
    job = relationship("Job", back_populates="applications")
    cover_letters = relationship("CoverLetter", back_populates="application", cascade="all, delete-orphan")


class CoverLetter(Base):
    __tablename__ = "cover_letters"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    application_id = Column(String(36), ForeignKey("applications.id"), nullable=False)
    content = Column(Text, nullable=False)
    recruiter_email_draft = Column(Text, nullable=True)
    linkedin_message_draft = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    application = relationship("Application", back_populates="cover_letters")


class ChatHistory(Base):
    __tablename__ = "chat_histories"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    role = Column(String(50), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    tool_calls = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="chat_histories")


# Phase 2 Models

class ResumeVersion(Base):
    __tablename__ = "resume_versions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    target_role = Column(String(255), nullable=True)
    content_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="resume_versions")


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    application_id = Column(String(36), ForeignKey("applications.id"), nullable=False)
    transcript_json = Column(JSON, nullable=False)
    overall_score = Column(Float, nullable=True)
    star_feedback = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class SkillGapRoadmap(Base):
    __tablename__ = "skill_gap_roadmaps"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    target_role = Column(String(255), nullable=False)
    missing_skills = Column(JSON, nullable=False)
    roadmap_steps = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class CompanyIntelligence(Base):
    __tablename__ = "company_intelligence"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    company_name = Column(String(255), unique=True, nullable=False)
    tech_stack = Column(JSON, nullable=True)
    recent_news = Column(JSON, nullable=True)
    culture_summary = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)


class ScheduledScrape(Base):
    __tablename__ = "scheduled_scrapes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    platform_name = Column(String(100), nullable=False)
    interval_minutes = Column(Integer, default=1440)
    last_run_at = Column(DateTime, nullable=True)
    status = Column(String(50), default="idle")


class UserNotification(Base):
    __tablename__ = "user_notifications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    type = Column(String(50), nullable=False)  # job_match, reminder, alert
    payload_json = Column(JSON, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")
