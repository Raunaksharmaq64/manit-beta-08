"""
RIGHT FIT Core — SQLAlchemy Database Models
Version: 1.0.0
Phase: 3 — Identity, Candidate Profile & Privacy Foundation
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def utc_now() -> datetime:
    """Returns current datetime in UTC timezone."""
    return datetime.now(timezone.utc)


def ensure_utc(dt: Optional[datetime]) -> Optional[datetime]:
    """Ensures datetime is timezone-aware in UTC (compatible with SQLite naive datetimes)."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def is_expired(expires_at: Optional[datetime]) -> bool:
    """Safely checks if an expiration timestamp has passed, handling naive SQLite datetimes."""
    if expires_at is None:
        return False
    target = ensure_utc(expires_at)
    return target < datetime.now(timezone.utc)


def generate_uuid() -> str:
    """Generates a UUID4 string."""
    return str(uuid.uuid4())


class User(Base):
    """Core platform user account entity."""
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="CANDIDATE", nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE", nullable=False)
    is_email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    profile: Mapped[Optional["CandidateProfile"]] = relationship("CandidateProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    refresh_tokens: Mapped[List["RefreshTokenRecord"]] = relationship("RefreshTokenRecord", back_populates="user", cascade="all, delete-orphan")
    verification_tokens: Mapped[List["EmailVerificationTokenRecord"]] = relationship("EmailVerificationTokenRecord", back_populates="user", cascade="all, delete-orphan")
    reset_tokens: Mapped[List["PasswordResetTokenRecord"]] = relationship("PasswordResetTokenRecord", back_populates="user", cascade="all, delete-orphan")
    privacy_settings: Mapped[Optional["PrivacySettingsRecord"]] = relationship("PrivacySettingsRecord", back_populates="user", uselist=False, cascade="all, delete-orphan")
    consents: Mapped[List["ConsentRecord"]] = relationship("ConsentRecord", back_populates="user", cascade="all, delete-orphan")
    export_requests: Mapped[List["DataExportRequestRecord"]] = relationship("DataExportRequestRecord", back_populates="user", cascade="all, delete-orphan")
    deletion_requests: Mapped[List["AccountDeletionRequestRecord"]] = relationship("AccountDeletionRequestRecord", back_populates="user", cascade="all, delete-orphan")
    resumes: Mapped[List["ResumeRecord"]] = relationship("ResumeRecord", back_populates="user", cascade="all, delete-orphan")
    saved_jobs: Mapped[List["SavedJobRecord"]] = relationship("SavedJobRecord", back_populates="user", cascade="all, delete-orphan")
    saved_searches: Mapped[List["SavedSearchRecord"]] = relationship("SavedSearchRecord", back_populates="user", cascade="all, delete-orphan")
    alert_logs: Mapped[List["AlertDeliveryLogRecord"]] = relationship("AlertDeliveryLogRecord", back_populates="user", cascade="all, delete-orphan")
    applications: Mapped[List["ApplicationRecord"]] = relationship("ApplicationRecord", back_populates="user", cascade="all, delete-orphan")
    reminders: Mapped[List["ReminderRecord"]] = relationship("ReminderRecord", back_populates="user", cascade="all, delete-orphan")
    interview_plans: Mapped[List["InterviewPlanRecord"]] = relationship("InterviewPlanRecord", back_populates="user", cascade="all, delete-orphan")
    star_answers: Mapped[List["STARAnswerRecord"]] = relationship("STARAnswerRecord", back_populates="user", cascade="all, delete-orphan")
    mock_sessions: Mapped[List["MockInterviewSessionRecord"]] = relationship("MockInterviewSessionRecord", back_populates="user", cascade="all, delete-orphan")
    debriefs: Mapped[List["InterviewDebriefRecord"]] = relationship("InterviewDebriefRecord", back_populates="user", cascade="all, delete-orphan")
    notifications: Mapped[List["NotificationRecord"]] = relationship("NotificationRecord", back_populates="user", cascade="all, delete-orphan")
    notification_preferences: Mapped[Optional["NotificationPreferencesRecord"]] = relationship("NotificationPreferencesRecord", back_populates="user", uselist=False, cascade="all, delete-orphan")
    saved_freelance_opportunities: Mapped[List["SavedFreelanceOpportunityRecord"]] = relationship("SavedFreelanceOpportunityRecord", back_populates="user", cascade="all, delete-orphan")
    freelance_search_history: Mapped[List["FreelanceSearchHistoryRecord"]] = relationship("FreelanceSearchHistoryRecord", back_populates="user", cascade="all, delete-orphan")
    freelance_settings: Mapped[Optional["FreelanceCandidateSettingsRecord"]] = relationship("FreelanceCandidateSettingsRecord", back_populates="user", uselist=False, cascade="all, delete-orphan")
    outreach_drafts: Mapped[List["OutreachDraftRecord"]] = relationship("OutreachDraftRecord", back_populates="user", cascade="all, delete-orphan")
    saved_startup_opportunities: Mapped[List["SavedStartupOpportunityRecord"]] = relationship("SavedStartupOpportunityRecord", back_populates="user", cascade="all, delete-orphan")
    startup_pitch_drafts: Mapped[List["StartupPitchDraftRecord"]] = relationship("StartupPitchDraftRecord", back_populates="user", cascade="all, delete-orphan")
    startup_workspaces: Mapped[List["StartupOpportunityWorkspaceRecord"]] = relationship("StartupOpportunityWorkspaceRecord", back_populates="user", cascade="all, delete-orphan")
    opportunity_feedbacks: Mapped[List["CandidateOpportunityFeedbackRecord"]] = relationship("CandidateOpportunityFeedbackRecord", back_populates="user", cascade="all, delete-orphan")
    skill_gap_recommendations: Mapped[List["CandidateSkillGapRecommendationRecord"]] = relationship("CandidateSkillGapRecommendationRecord", back_populates="user", cascade="all, delete-orphan")
    beta_feedbacks: Mapped[List["BetaFeedbackRecord"]] = relationship("BetaFeedbackRecord", back_populates="user")
    beta_consents: Mapped[List["BetaConsentRecord"]] = relationship("BetaConsentRecord", back_populates="user", cascade="all, delete-orphan")


class RefreshTokenRecord(Base):
    """Stored hash of rotating refresh tokens for session management and reuse detection."""
    __tablename__ = "refresh_tokens"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    family_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")


class EmailVerificationTokenRecord(Base):
    """Single-use email verification tokens."""
    __tablename__ = "email_verification_tokens"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="verification_tokens")


class PasswordResetTokenRecord(Base):
    """Single-use password recovery tokens."""
    __tablename__ = "password_reset_tokens"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="reset_tokens")


class CandidateProfile(Base):
    """Central candidate profile entity owned by Core."""
    __tablename__ = "candidate_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    headline: Mapped[Optional[str]] = mapped_column(String(140), nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    timezone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    portfolio_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    github_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    website_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    social_links_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="profile")
    education: Mapped[List["EducationRecord"]] = relationship("EducationRecord", back_populates="profile", cascade="all, delete-orphan", lazy="selectin")
    experience: Mapped[List["ExperienceRecord"]] = relationship("ExperienceRecord", back_populates="profile", cascade="all, delete-orphan", lazy="selectin")
    skills: Mapped[List["CandidateSkillRecord"]] = relationship("CandidateSkillRecord", back_populates="profile", cascade="all, delete-orphan", lazy="selectin")
    preferences: Mapped[Optional["CandidatePreferenceRecord"]] = relationship("CandidatePreferenceRecord", back_populates="profile", uselist=False, cascade="all, delete-orphan", lazy="selectin")


class EducationRecord(Base):
    __tablename__ = "educations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    profile_id: Mapped[str] = mapped_column(String(36), ForeignKey("candidate_profiles.id", ondelete="CASCADE"), index=True, nullable=False)
    institution: Mapped[str] = mapped_column(String(150), nullable=False)
    degree: Mapped[str] = mapped_column(String(100), nullable=False)
    field_of_study: Mapped[str] = mapped_column(String(100), nullable=False)
    start_date: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    end_date: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    achievements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    provenance: Mapped[str] = mapped_column(String(30), default="USER_PROVIDED", nullable=False)

    profile: Mapped["CandidateProfile"] = relationship("CandidateProfile", back_populates="education")


class ExperienceRecord(Base):
    __tablename__ = "experiences"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    profile_id: Mapped[str] = mapped_column(String(36), ForeignKey("candidate_profiles.id", ondelete="CASCADE"), index=True, nullable=False)
    company: Mapped[str] = mapped_column(String(150), nullable=False)
    role: Mapped[str] = mapped_column(String(100), nullable=False)
    employment_type: Mapped[str] = mapped_column(String(50), default="Full-time", nullable=False)
    start_date: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    end_date: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    skills_json: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    provenance: Mapped[str] = mapped_column(String(30), default="USER_PROVIDED", nullable=False)

    profile: Mapped["CandidateProfile"] = relationship("CandidateProfile", back_populates="experience")


class CandidateSkillRecord(Base):
    __tablename__ = "candidate_skills"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    profile_id: Mapped[str] = mapped_column(String(36), ForeignKey("candidate_profiles.id", ondelete="CASCADE"), index=True, nullable=False)
    skill_name: Mapped[str] = mapped_column(String(80), nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="Technical", nullable=False)
    proficiency: Mapped[str] = mapped_column(String(30), default="Intermediate", nullable=False)
    years_experience: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    provenance: Mapped[str] = mapped_column(String(30), default="USER_PROVIDED", nullable=False)
    canonical_skill_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    source_of_evidence: Mapped[str] = mapped_column(String(64), default="USER_ENTERED", nullable=False)
    resume_section: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    extraction_confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    confirmation_status: Mapped[str] = mapped_column(String(32), default="CONFIRMED", index=True, nullable=False)
    last_updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    profile: Mapped["CandidateProfile"] = relationship("CandidateProfile", back_populates="skills")


class CandidatePreferenceRecord(Base):
    __tablename__ = "candidate_preferences"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    profile_id: Mapped[str] = mapped_column(String(36), ForeignKey("candidate_profiles.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    preferred_roles_json: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    preferred_skills_json: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    preferred_industries_json: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    preferred_locations_json: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    remote_preference: Mapped[str] = mapped_column(String(20), default="ANY", nullable=False)
    min_salary: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_salary: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    employment_types_json: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    job_notification_frequency: Mapped[str] = mapped_column(String(20), default="DAILY", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    profile: Mapped["CandidateProfile"] = relationship("CandidateProfile", back_populates="preferences")


class PrivacySettingsRecord(Base):
    __tablename__ = "privacy_settings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    profile_visibility: Mapped[str] = mapped_column(String(20), default="PUBLIC", nullable=False)
    opportunity_alerts: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    email_notifications: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    ai_processing_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    data_usage_research: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="privacy_settings")


class ConsentRecord(Base):
    __tablename__ = "consent_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    purpose: Mapped[str] = mapped_column(String(50), nullable=False)
    granted: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    policy_version: Mapped[str] = mapped_column(String(20), default="1.0", nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    withdrawn_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="consents")


class DataExportRequestRecord(Base):
    __tablename__ = "data_export_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False)
    export_data_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="export_requests")


class AccountDeletionRequestRecord(Base):
    __tablename__ = "account_deletion_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False)
    reasons: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    service_status_json: Mapped[Dict[str, str]] = mapped_column(JSON, default=dict, nullable=False)
    scheduled_deletion_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="deletion_requests")


class SecurityAuditEventRecord(Base):
    __tablename__ = "security_audit_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    actor_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # SUCCESS, FAILURE
    details_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)


# =============================================================================
# Phase 4: Resume Intelligence & Reviewed Candidate Evidence Models
# =============================================================================

class ResumeRecord(Base):
    """Candidate resume container grouping multiple versions."""
    __tablename__ = "resumes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(150), default="My Resume", nullable=False)
    active_version_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="resumes")
    versions: Mapped[List["ResumeVersionRecord"]] = relationship(
        "ResumeVersionRecord",
        back_populates="resume",
        cascade="all, delete-orphan",
        order_by="desc(ResumeVersionRecord.version_number)"
    )


class ResumeVersionRecord(Base):
    """Specific uploaded file version and processing lifecycle state."""
    __tablename__ = "resume_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    resume_id: Mapped[str] = mapped_column(String(36), ForeignKey("resumes.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    version_label: Mapped[str] = mapped_column(String(100), default="v1", nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(10), nullable=False)  # pdf, docx
    mime_type: Mapped[str] = mapped_column(String(120), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_hash_sha256: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    parsing_status: Mapped[str] = mapped_column(String(30), default="UPLOADED", index=True, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    parsed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    resume: Mapped["ResumeRecord"] = relationship("ResumeRecord", back_populates="versions")
    extraction: Mapped[Optional["ResumeExtractionRecord"]] = relationship(
        "ResumeExtractionRecord",
        back_populates="resume_version",
        uselist=False,
        cascade="all, delete-orphan"
    )
    review: Mapped[Optional["ResumeReviewRecord"]] = relationship(
        "ResumeReviewRecord",
        back_populates="resume_version",
        uselist=False,
        cascade="all, delete-orphan"
    )
    ats_analyses: Mapped[List["ATSAnalysisRecord"]] = relationship(
        "ATSAnalysisRecord",
        back_populates="resume_version",
        cascade="all, delete-orphan"
    )
    job_matches: Mapped[List["ResumeJobMatchRecord"]] = relationship(
        "ResumeJobMatchRecord",
        back_populates="resume_version",
        cascade="all, delete-orphan"
    )
    suggestion_actions: Mapped[List["ResumeAISuggestionActionRecord"]] = relationship(
        "ResumeAISuggestionActionRecord",
        back_populates="resume_version",
        cascade="all, delete-orphan"
    )


class ResumeExtractionRecord(Base):
    """Structured information and evidence extracted from a resume version."""
    __tablename__ = "resume_extractions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    resume_version_id: Mapped[str] = mapped_column(String(36), ForeignKey("resume_versions.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    summary_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict, nullable=True)
    sections_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    personal_info_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    education_json: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    experience_json: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    skills_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    projects_json: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    certifications_json: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    languages_json: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, default=list, nullable=True)
    publications_json: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, default=list, nullable=True)
    awards_json: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, default=list, nullable=True)
    internships_json: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, default=list, nullable=True)
    inferred_skills_json: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, default=list, nullable=True)
    quality_score_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict, nullable=True)
    evidence_items_json: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    resume_version: Mapped["ResumeVersionRecord"] = relationship("ResumeVersionRecord", back_populates="extraction")


class ResumeReviewRecord(Base):
    """Candidate review workbench state and synchronization tracking."""
    __tablename__ = "resume_reviews"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    resume_version_id: Mapped[str] = mapped_column(String(36), ForeignKey("resume_versions.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    review_status: Mapped[str] = mapped_column(String(30), default="PENDING", nullable=False)
    field_reviews_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    is_synced_to_profile: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    resume_version: Mapped["ResumeVersionRecord"] = relationship("ResumeVersionRecord", back_populates="review")


class ATSAnalysisRecord(Base):
    """Grounded ATS keyword match and bullet impact analysis."""
    __tablename__ = "ats_analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    resume_version_id: Mapped[str] = mapped_column(String(36), ForeignKey("resume_versions.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    target_job_title: Mapped[str] = mapped_column(String(150), nullable=False)
    target_job_description: Mapped[str] = mapped_column(Text, nullable=False)
    coverage_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    matched_keywords_json: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    missing_keywords_json: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    bullet_impact_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    bullet_impact_analysis_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    actionable_suggestions_json: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    formatting_observations_json: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    methodology_and_limitations: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    resume_version: Mapped["ResumeVersionRecord"] = relationship("ResumeVersionRecord", back_populates="ats_analyses")


class ResumeJobMatchRecord(Base):
    """Evidence-backed job-specific resume match result."""
    __tablename__ = "resume_job_matches"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    resume_version_id: Mapped[str] = mapped_column(String(36), ForeignKey("resume_versions.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    target_job_title: Mapped[str] = mapped_column(String(150), nullable=False)
    target_job_description: Mapped[str] = mapped_column(Text, nullable=False)
    overall_match_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    keyword_coverage_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    required_skills_match_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    preferred_skills_match_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    experience_level_match_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    project_theme_alignments_json: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    unverified_matches_json: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    job_specific_suggestions_json: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    resume_version: Mapped["ResumeVersionRecord"] = relationship("ResumeVersionRecord", back_populates="job_matches")


class ResumeAISuggestionActionRecord(Base):
    """Candidate approval action on an AI suggestion."""
    __tablename__ = "resume_ai_suggestion_actions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    resume_version_id: Mapped[str] = mapped_column(String(36), ForeignKey("resume_versions.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    suggestion_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    action: Mapped[str] = mapped_column(String(32), nullable=False)  # ACCEPT, REJECT, EDIT, REGENERATE
    original_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    suggested_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    edited_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="APPLIED", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    resume_version: Mapped["ResumeVersionRecord"] = relationship("ResumeVersionRecord", back_populates="suggestion_actions")


# ==============================================================================
# Phase 5: Job Source Framework Models
# ==============================================================================

class JobSourceRecord(Base):
    """Job source configuration, governance policy, and resilience state."""
    __tablename__ = "job_sources"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    source_key: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(150), nullable=False)
    source_type: Mapped[str] = mapped_column(String(30), default="ATS_JOB_BOARD", nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    base_url: Mapped[str] = mapped_column(String(500), nullable=False)
    integration_method: Mapped[str] = mapped_column(String(30), default="REST_API", nullable=False)
    auth_type: Mapped[str] = mapped_column(String(30), default="NONE_PUBLIC", nullable=False)
    credential_reference: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    policy_status: Mapped[str] = mapped_column(String(30), default="DRAFT", nullable=False)
    policy_decision_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    rate_limit_per_minute: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    timeout_seconds: Mapped[float] = mapped_column(Float, default=30.0, nullable=False)
    retry_max_attempts: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    circuit_breaker_state: Mapped[str] = mapped_column(String(20), default="CLOSED", nullable=False)
    consecutive_failures: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_failure_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_success_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    cooldown_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    observations: Mapped[List["SourceObservationRecord"]] = relationship(
        "SourceObservationRecord",
        back_populates="source",
        cascade="all, delete-orphan"
    )
    opportunities: Mapped[List["CanonicalOpportunityRecord"]] = relationship(
        "CanonicalOpportunityRecord",
        back_populates="source",
        cascade="all, delete-orphan"
    )
    run_logs: Mapped[List["SourceRunLogRecord"]] = relationship(
        "SourceRunLogRecord",
        back_populates="source",
        cascade="all, delete-orphan"
    )


class SourceObservationRecord(Base):
    """Raw payload observation and provenance record."""
    __tablename__ = "source_observations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    source_id: Mapped[str] = mapped_column(String(36), ForeignKey("job_sources.id", ondelete="CASCADE"), index=True, nullable=False)
    external_job_id: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    listing_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    source_published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    source_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    raw_payload_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    payload_hash_sha256: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    normalization_status: Mapped[str] = mapped_column(String(30), default="NORMALIZED", nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    source: Mapped["JobSourceRecord"] = relationship("JobSourceRecord", back_populates="observations")


class CanonicalOpportunityRecord(Base):
    """Canonical, normalized career opportunity stored in Core platform."""
    __tablename__ = "canonical_opportunities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    source_id: Mapped[str] = mapped_column(String(36), ForeignKey("job_sources.id", ondelete="CASCADE"), index=True, nullable=False)
    external_job_id: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    dedup_key_sha256: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    company_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    description_clean: Mapped[str] = mapped_column(Text, nullable=False)
    employment_type: Mapped[str] = mapped_column(String(30), default="FULL_TIME", nullable=False)
    workplace_type: Mapped[str] = mapped_column(String(30), default="UNKNOWN", nullable=False)
    department: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_remote: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    min_salary: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_salary: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    currency: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    salary_period: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    is_salary_estimated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    required_skills_json: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    application_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    source_published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    source_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    last_checked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_successful_check_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    status_changed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    expiry_derivation_notes: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    verification_status: Mapped[str] = mapped_column(String(30), default="UNVERIFIED", index=True, nullable=False)
    freshness_state: Mapped[str] = mapped_column(String(30), default="UNKNOWN", index=True, nullable=False)
    is_suppressed: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True, nullable=False)
    provenance_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    source: Mapped["JobSourceRecord"] = relationship("JobSourceRecord", back_populates="opportunities")
    verification_evidence: Mapped[List["VerificationEvidenceRecord"]] = relationship(
        "VerificationEvidenceRecord",
        back_populates="opportunity",
        cascade="all, delete-orphan"
    )
    source_mappings: Mapped[List["OpportunitySourceMappingRecord"]] = relationship(
        "OpportunitySourceMappingRecord",
        back_populates="opportunity",
        cascade="all, delete-orphan"
    )
    feedbacks: Mapped[List["UserListingFeedbackRecord"]] = relationship(
        "UserListingFeedbackRecord",
        back_populates="opportunity",
        cascade="all, delete-orphan"
    )
    saved_by: Mapped[List["SavedJobRecord"]] = relationship(
        "SavedJobRecord",
        back_populates="opportunity",
        cascade="all, delete-orphan"
    )
    applications: Mapped[List["ApplicationRecord"]] = relationship(
        "ApplicationRecord",
        back_populates="opportunity"
    )


class SourceRunLogRecord(Base):
    """Execution metrics and audit logs for source ingestion runs."""
    __tablename__ = "source_run_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    source_id: Mapped[str] = mapped_column(String(36), ForeignKey("job_sources.id", ondelete="CASCADE"), index=True, nullable=False)
    trigger_type: Mapped[str] = mapped_column(String(30), default="MANUAL", nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="RUNNING", nullable=False)
    records_fetched: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_normalized: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_inserted: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_updated: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    duplicates_skipped: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    safe_error_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    source: Mapped["JobSourceRecord"] = relationship("JobSourceRecord", back_populates="run_logs")


# ==============================================================================
# Phase 6: Verification, Deduplication, Freshness & Evidence Models
# ==============================================================================

class VerificationEvidenceRecord(Base):
    """Immutable audit trail of a verification check and its concrete evidentiary basis."""
    __tablename__ = "verification_evidence"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    opportunity_id: Mapped[str] = mapped_column(String(36), ForeignKey("canonical_opportunities.id", ondelete="CASCADE"), index=True, nullable=False)
    source_id: Mapped[str] = mapped_column(String(36), ForeignKey("job_sources.id", ondelete="CASCADE"), index=True, nullable=False)
    check_id: Mapped[str] = mapped_column(String(36), default=generate_uuid, index=True, nullable=False)
    check_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    check_method: Mapped[str] = mapped_column(String(50), nullable=False)
    check_outcome: Mapped[str] = mapped_column(String(30), nullable=False)
    http_status: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    provider_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    evidence_category: Mapped[str] = mapped_column(String(50), nullable=False)
    evidence_reference: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    safe_response_metadata_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    verification_rule_version: Mapped[str] = mapped_column(String(20), default="1.0.0", nullable=False)
    confidence_category: Mapped[str] = mapped_column(String(30), default="HIGH", nullable=False)
    error_category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    next_eligible_check_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    opportunity: Mapped["CanonicalOpportunityRecord"] = relationship("CanonicalOpportunityRecord", back_populates="verification_evidence")
    source: Mapped["JobSourceRecord"] = relationship("JobSourceRecord")


class OpportunitySourceMappingRecord(Base):
    """Preserves distinct source observations mapped to a canonical opportunity record."""
    __tablename__ = "opportunity_source_mappings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    canonical_opportunity_id: Mapped[str] = mapped_column(String(36), ForeignKey("canonical_opportunities.id", ondelete="CASCADE"), index=True, nullable=False)
    source_id: Mapped[str] = mapped_column(String(36), ForeignKey("job_sources.id", ondelete="CASCADE"), index=True, nullable=False)
    external_job_id: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    original_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    mapping_status: Mapped[str] = mapped_column(String(30), default="ACTIVE", nullable=False)
    match_tier: Mapped[str] = mapped_column(String(30), default="TIER_1_EXACT", nullable=False)
    match_method: Mapped[str] = mapped_column(String(50), default="EXACT_SOURCE_ID", nullable=False)
    match_evidence_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    merge_decision_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    opportunity: Mapped["CanonicalOpportunityRecord"] = relationship("CanonicalOpportunityRecord", back_populates="source_mappings")
    source: Mapped["JobSourceRecord"] = relationship("JobSourceRecord")


class MergeDecisionRecord(Base):
    """Auditable record of a merge or unmerge decision across duplicate opportunities."""
    __tablename__ = "merge_decisions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    canonical_opportunity_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    original_opportunity_ids_json: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    match_tier: Mapped[str] = mapped_column(String(30), nullable=False)
    match_method: Mapped[str] = mapped_column(String(50), nullable=False)
    evidence_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    actor_type: Mapped[str] = mapped_column(String(20), default="SYSTEM", nullable=False)
    actor_id: Mapped[str] = mapped_column(String(120), nullable=False)
    rule_version: Mapped[str] = mapped_column(String(20), default="1.0.0", nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="CONFIRMED", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    unmerged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    unmerged_by: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    unmerge_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class DuplicateCandidateRecord(Base):
    """Pairwise duplicate candidate awaiting automated or human administrative review."""
    __tablename__ = "duplicate_candidates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    primary_opportunity_id: Mapped[str] = mapped_column(String(36), ForeignKey("canonical_opportunities.id", ondelete="CASCADE"), index=True, nullable=False)
    duplicate_opportunity_id: Mapped[str] = mapped_column(String(36), ForeignKey("canonical_opportunities.id", ondelete="CASCADE"), index=True, nullable=False)
    match_tier: Mapped[str] = mapped_column(String(30), default="TIER_3_PROBABLE", nullable=False)
    match_method: Mapped[str] = mapped_column(String(50), nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    match_evidence_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="PROPOSED", nullable=False)
    decision_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_by: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)

    primary_opportunity: Mapped["CanonicalOpportunityRecord"] = relationship(
        "CanonicalOpportunityRecord",
        foreign_keys=[primary_opportunity_id]
    )
    duplicate_opportunity: Mapped["CanonicalOpportunityRecord"] = relationship(
        "CanonicalOpportunityRecord",
        foreign_keys=[duplicate_opportunity_id]
    )


class UserListingFeedbackRecord(Base):
    """User-reported feedback regarding listing inaccuracies, broken links, or closures."""
    __tablename__ = "user_listing_feedback"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    opportunity_id: Mapped[str] = mapped_column(String(36), ForeignKey("canonical_opportunities.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    feedback_type: Mapped[str] = mapped_column(String(30), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="RECEIVED", nullable=False)
    ip_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    opportunity: Mapped["CanonicalOpportunityRecord"] = relationship("CanonicalOpportunityRecord", back_populates="feedbacks")


# ==============================================================================
# Phase 7: Job Search, Candidate Matching, Saved Jobs & Alerts
# ==============================================================================

class SavedJobRecord(Base):
    """Candidate-saved job listing with optional private notes."""
    __tablename__ = "saved_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    opportunity_id: Mapped[str] = mapped_column(String(36), ForeignKey("canonical_opportunities.id", ondelete="CASCADE"), index=True, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="saved_jobs")
    opportunity: Mapped["CanonicalOpportunityRecord"] = relationship("CanonicalOpportunityRecord", back_populates="saved_by")


class SavedSearchRecord(Base):
    """Saved search query parameters and candidate alert notification subscription."""
    __tablename__ = "saved_searches"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    query_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    filters_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    alert_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    alert_frequency: Mapped[str] = mapped_column(String(20), default="DAILY", nullable=False)
    last_notified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="saved_searches")
    delivery_logs: Mapped[List["AlertDeliveryLogRecord"]] = relationship(
        "AlertDeliveryLogRecord",
        back_populates="saved_search",
        cascade="all, delete-orphan"
    )


class AlertDeliveryLogRecord(Base):
    """Audit log of delivered job match alert notifications."""
    __tablename__ = "alert_delivery_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    saved_search_id: Mapped[str] = mapped_column(String(36), ForeignKey("saved_searches.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    opportunity_ids_json: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    delivery_channel: Mapped[str] = mapped_column(String(30), default="IN_APP", nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="DELIVERED", nullable=False)
    delivered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="alert_logs")
    saved_search: Mapped["SavedSearchRecord"] = relationship("SavedSearchRecord", back_populates="delivery_logs")


# ==============================================================================
# Phase 8: CRM, Reminders, Interview Intelligence & Notifications Models
# ==============================================================================

class ApplicationRecord(Base):
    """Candidate job application tracking and CRM entity."""
    __tablename__ = "applications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    opportunity_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("canonical_opportunities.id", ondelete="SET NULL"), nullable=True, index=True)
    company_name: Mapped[str] = mapped_column(String(150), nullable=False)
    job_title: Mapped[str] = mapped_column(String(150), nullable=False)
    application_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="SAVED", index=True, nullable=False)
    applied_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    apply_link_opened_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_submission_confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    current_stage: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    salary_offered: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    salary_currency: Mapped[Optional[str]] = mapped_column(String(10), default="USD", nullable=True)
    contact_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    contact_email: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="applications")
    opportunity: Mapped[Optional["CanonicalOpportunityRecord"]] = relationship("CanonicalOpportunityRecord", back_populates="applications")
    status_history: Mapped[List["ApplicationStatusHistoryRecord"]] = relationship(
        "ApplicationStatusHistoryRecord",
        back_populates="application",
        cascade="all, delete-orphan",
        order_by="desc(ApplicationStatusHistoryRecord.changed_at)"
    )
    notes: Mapped[List["ApplicationNoteRecord"]] = relationship(
        "ApplicationNoteRecord",
        back_populates="application",
        cascade="all, delete-orphan",
        order_by="desc(ApplicationNoteRecord.created_at)"
    )
    reminders: Mapped[List["ReminderRecord"]] = relationship(
        "ReminderRecord",
        back_populates="application",
        cascade="all, delete-orphan"
    )
    interview_plans: Mapped[List["InterviewPlanRecord"]] = relationship(
        "InterviewPlanRecord",
        back_populates="application",
        cascade="all, delete-orphan"
    )
    debriefs: Mapped[List["InterviewDebriefRecord"]] = relationship(
        "InterviewDebriefRecord",
        back_populates="application",
        cascade="all, delete-orphan"
    )


class ApplicationStatusHistoryRecord(Base):
    """Immutable audit trail of application state transitions."""
    __tablename__ = "application_status_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    application_id: Mapped[str] = mapped_column(String(36), ForeignKey("applications.id", ondelete="CASCADE"), index=True, nullable=False)
    from_status: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    to_status: Mapped[str] = mapped_column(String(30), nullable=False)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    actor_type: Mapped[str] = mapped_column(String(30), default="CANDIDATE", nullable=False)
    actor_id: Mapped[str] = mapped_column(String(120), nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    application: Mapped["ApplicationRecord"] = relationship("ApplicationRecord", back_populates="status_history")


class ApplicationNoteRecord(Base):
    """Candidate private notes attached to an application."""
    __tablename__ = "application_notes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    application_id: Mapped[str] = mapped_column(String(36), ForeignKey("applications.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    note_type: Mapped[str] = mapped_column(String(30), default="GENERAL", nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    application: Mapped["ApplicationRecord"] = relationship("ApplicationRecord", back_populates="notes")


class ReminderRecord(Base):
    """Candidate scheduled follow-ups, interview reminders, and deadlines."""
    __tablename__ = "reminders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    application_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("applications.id", ondelete="CASCADE"), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    reminder_type: Mapped[str] = mapped_column(String(30), default="FOLLOW_UP", nullable=False)
    due_at_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    notification_sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="reminders")
    application: Mapped[Optional["ApplicationRecord"]] = relationship("ApplicationRecord", back_populates="reminders")


class InterviewPlanRecord(Base):
    """Interview preparation container linking a job role with rounds and study plans."""
    __tablename__ = "interview_plans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    application_id: Mapped[str] = mapped_column(String(36), ForeignKey("applications.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    role_title: Mapped[str] = mapped_column(String(150), nullable=False)
    company_name: Mapped[str] = mapped_column(String(150), nullable=False)
    job_description_excerpt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="interview_plans")
    application: Mapped["ApplicationRecord"] = relationship("ApplicationRecord", back_populates="interview_plans")
    rounds: Mapped[List["InterviewRoundRecord"]] = relationship(
        "InterviewRoundRecord",
        back_populates="plan",
        cascade="all, delete-orphan",
        order_by="InterviewRoundRecord.round_number"
    )
    star_answers: Mapped[List["STARAnswerRecord"]] = relationship(
        "STARAnswerRecord",
        back_populates="plan",
        cascade="all, delete-orphan"
    )
    mock_sessions: Mapped[List["MockInterviewSessionRecord"]] = relationship(
        "MockInterviewSessionRecord",
        back_populates="plan"
    )


class InterviewRoundRecord(Base):
    """Specific scheduled round within an interview plan."""
    __tablename__ = "interview_rounds"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    plan_id: Mapped[str] = mapped_column(String(36), ForeignKey("interview_plans.id", ondelete="CASCADE"), index=True, nullable=False)
    round_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    round_name: Mapped[str] = mapped_column(String(150), nullable=False)
    scheduled_at_utc: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    interview_format: Mapped[str] = mapped_column(String(30), default="VIDEO", nullable=False)
    interviewer_names: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    focus_areas_json: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="SCHEDULED", nullable=False)

    plan: Mapped["InterviewPlanRecord"] = relationship("InterviewPlanRecord", back_populates="rounds")


class STARAnswerRecord(Base):
    """Structured STAR answer grounded in candidate verified resume and experience."""
    __tablename__ = "star_answers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    plan_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("interview_plans.id", ondelete="SET NULL"), nullable=True, index=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    question: Mapped[str] = mapped_column(String(500), nullable=False)
    category: Mapped[str] = mapped_column(String(80), default="TECHNICAL_CHALLENGE", nullable=False)
    situation: Mapped[str] = mapped_column(Text, nullable=False)
    task: Mapped[str] = mapped_column(Text, nullable=False)
    action: Mapped[str] = mapped_column(Text, nullable=False)
    result: Mapped[str] = mapped_column(Text, nullable=False)
    supporting_evidence_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    missing_information_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_candidate_approved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="star_answers")
    plan: Mapped[Optional["InterviewPlanRecord"]] = relationship("InterviewPlanRecord", back_populates="star_answers")


class MockInterviewSessionRecord(Base):
    """Interactive practice interview session."""
    __tablename__ = "mock_interview_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    plan_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("interview_plans.id", ondelete="SET NULL"), nullable=True, index=True)
    role_title: Mapped[str] = mapped_column(String(150), nullable=False)
    session_type: Mapped[str] = mapped_column(String(30), default="BEHAVIORAL", nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="IN_PROGRESS", nullable=False)
    average_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    overall_feedback_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="mock_sessions")
    plan: Mapped[Optional["InterviewPlanRecord"]] = relationship("InterviewPlanRecord", back_populates="mock_sessions")
    questions: Mapped[List["MockInterviewQuestionRecord"]] = relationship(
        "MockInterviewQuestionRecord",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="MockInterviewQuestionRecord.order_index"
    )


class MockInterviewQuestionRecord(Base):
    """Individual question and rubric evaluation within a mock interview session."""
    __tablename__ = "mock_interview_questions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("mock_interview_sessions.id", ondelete="CASCADE"), index=True, nullable=False)
    question_text: Mapped[str] = mapped_column(String(1000), nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    candidate_answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    feedback_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    follow_up_question: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    answered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    session: Mapped["MockInterviewSessionRecord"] = relationship("MockInterviewSessionRecord", back_populates="questions")


class InterviewDebriefRecord(Base):
    """Post-interview candidate reflections, questions asked, and follow-up tracking."""
    __tablename__ = "interview_debriefs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    application_id: Mapped[str] = mapped_column(String(36), ForeignKey("applications.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    round_name: Mapped[str] = mapped_column(String(150), nullable=False)
    interview_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    questions_asked_json: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    topics_discussed: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    candidate_reflections: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    strengths: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    areas_to_improve: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recruiter_commitments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    expected_response_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    next_step: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="debriefs")
    application: Mapped["ApplicationRecord"] = relationship("ApplicationRecord", back_populates="debriefs")


class NotificationRecord(Base):
    """In-app alerts and notifications delivered to candidate."""
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="SYSTEM", nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    reference_link: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    delivery_channel: Mapped[str] = mapped_column(String(30), default="IN_APP", nullable=False)
    delivery_status: Mapped[str] = mapped_column(String(30), default="DELIVERED", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="notifications")


class NotificationPreferencesRecord(Base):
    """Candidate notification settings and delivery channel controls."""
    __tablename__ = "notification_preferences"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    in_app_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    email_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    interview_reminders: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    application_follow_ups: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    assessment_deadlines: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    prep_milestones: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    frequency: Mapped[str] = mapped_column(String(30), default="DAILY_DIGEST", nullable=False)
    quiet_hours_start: Mapped[Optional[str]] = mapped_column(String(10), default="22:00", nullable=True)
    quiet_hours_end: Mapped[Optional[str]] = mapped_column(String(10), default="08:00", nullable=True)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)
    job_alerts_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    digest_email_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    market_intelligence_alerts: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="notification_preferences")


# ==============================================================================
# PHASE 9: FREELANCE OPPORTUNITIES, CONTACT EVIDENCE & OUTREACH
# ==============================================================================

class FreelanceOpportunityRecord(Base):
    """Canonical freelance and local business development opportunity imported from LeadHunter."""
    __tablename__ = "freelance_opportunities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    leadhunter_lead_id: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    place_id: Mapped[Optional[str]] = mapped_column(String(255), index=True, nullable=True)
    business_name: Mapped[str] = mapped_column(String(255), nullable=False)
    opportunity_title: Mapped[str] = mapped_column(String(255), nullable=False)
    service_category: Mapped[str] = mapped_column(String(120), default="Web Development", nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    city: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_remote: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    website: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    is_broken_website: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    rating: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    reviews_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    instagram: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    facebook: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    linkedin: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    twitter: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    required_skills: Mapped[List[Any]] = mapped_column(JSON, default=list, nullable=False)
    suggested_service: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    suggested_pitch: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    classification_state: Mapped[str] = mapped_column(
        String(50), default="POTENTIAL_FREELANCE_OPPORTUNITY", index=True, nullable=False
    )
    classification_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    priority: Mapped[str] = mapped_column(String(20), default="MEDIUM", index=True, nullable=False)
    relevance_score: Mapped[float] = mapped_column(Float, default=85.0, nullable=False)
    source: Mapped[str] = mapped_column(String(60), default="leadhunter_google_maps", nullable=False)
    original_source_url: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    discovered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    last_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    contact_evidence: Mapped[List["ContactEvidenceRecord"]] = relationship(
        "ContactEvidenceRecord", back_populates="opportunity", cascade="all, delete-orphan"
    )
    drafts: Mapped[List["OutreachDraftRecord"]] = relationship(
        "OutreachDraftRecord", back_populates="opportunity", cascade="all, delete-orphan"
    )
    saved_by: Mapped[List["SavedFreelanceOpportunityRecord"]] = relationship(
        "SavedFreelanceOpportunityRecord", back_populates="opportunity", cascade="all, delete-orphan"
    )


class ContactEvidenceRecord(Base):
    """Audit evidence ledger for contact points discovered for a freelance opportunity."""
    __tablename__ = "contact_evidence"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    opportunity_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("freelance_opportunities.id", ondelete="CASCADE"), index=True, nullable=False
    )
    contact_type: Mapped[str] = mapped_column(String(30), nullable=False)  # EMAIL, PHONE, WEBSITE, etc.
    contact_value: Mapped[str] = mapped_column(String(255), nullable=False)
    source: Mapped[str] = mapped_column(String(60), default="leadhunter", nullable=False)
    source_evidence_url: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    evidence_status: Mapped[str] = mapped_column(String(30), default="OBSERVED", nullable=False)
    verification_method: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    verification_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    discovered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    opportunity: Mapped["FreelanceOpportunityRecord"] = relationship(
        "FreelanceOpportunityRecord", back_populates="contact_evidence"
    )


class SavedFreelanceOpportunityRecord(Base):
    """Candidate-saved freelance opportunity bookmarks."""
    __tablename__ = "saved_freelance_opportunities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    opportunity_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("freelance_opportunities.id", ondelete="CASCADE"), index=True, nullable=False
    )
    status: Mapped[str] = mapped_column(String(30), default="SAVED", nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="saved_freelance_opportunities")
    opportunity: Mapped["FreelanceOpportunityRecord"] = relationship(
        "FreelanceOpportunityRecord", back_populates="saved_by"
    )


class OutreachDraftRecord(Base):
    """Outreach message draft requiring explicit candidate review and approval."""
    __tablename__ = "outreach_drafts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    opportunity_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("freelance_opportunities.id", ondelete="CASCADE"), index=True, nullable=False
    )
    channel: Mapped[str] = mapped_column(String(30), default="EMAIL", nullable=False)
    recipient_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    recipient_contact: Mapped[str] = mapped_column(String(255), nullable=False)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    message_body: Mapped[str] = mapped_column(Text, nullable=False)
    proposed_service: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="DRAFT", index=True, nullable=False)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_recipient: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    approved_subject: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    approved_body_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    candidate_edits_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="outreach_drafts")
    opportunity: Mapped["FreelanceOpportunityRecord"] = relationship(
        "FreelanceOpportunityRecord", back_populates="drafts"
    )
    delivery_logs: Mapped[List["OutreachDeliveryLogRecord"]] = relationship(
        "OutreachDeliveryLogRecord", back_populates="draft", cascade="all, delete-orphan"
    )


class OutreachDeliveryLogRecord(Base):
    """Audit delivery ledger for sent outreach messages."""
    __tablename__ = "outreach_delivery_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    draft_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("outreach_drafts.id", ondelete="CASCADE"), index=True, nullable=False
    )
    provider: Mapped[str] = mapped_column(String(50), default="SMTP", nullable=False)
    provider_message_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    provider_response_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    provider_raw_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    delivery_status: Mapped[str] = mapped_column(String(30), default="SENT", nullable=False)
    webhook_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    event_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    draft: Mapped["OutreachDraftRecord"] = relationship(
        "OutreachDraftRecord", back_populates="delivery_logs"
    )


class OutreachSuppressionRecord(Base):
    """Do-not-contact and unsubscribed recipients suppression list."""
    __tablename__ = "outreach_suppression_list"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    recipient_value: Mapped[str] = mapped_column(String(255), index=True, unique=True, nullable=False)
    reason: Mapped[str] = mapped_column(String(50), default="UNSUBSCRIBED", nullable=False)
    created_by_user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class FreelanceSearchHistoryRecord(Base):
    """Candidate historical freelance discovery search queries."""
    __tablename__ = "freelance_search_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    query: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(150), nullable=False)
    results_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    leads_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    deep_scan: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    zones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    include_with_website: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    searched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="freelance_search_history")


class FreelanceCandidateSettingsRecord(Base):
    """Candidate BYOK API credentials and custom email inbox configurations."""
    __tablename__ = "freelance_candidate_settings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False
    )
    encrypted_serpapi_key: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    encrypted_apify_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    encrypted_gemini_key: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    maps_provider: Mapped[str] = mapped_column(String(50), default="serpapi", nullable=False)
    sender_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    sender_brand: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    smtp_host: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    smtp_port: Mapped[int] = mapped_column(Integer, default=465, nullable=False)
    smtp_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    encrypted_smtp_password: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    smtp_use_ssl: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="freelance_settings")


# ==============================================================================
# PHASE 10: STARTUP INTELLIGENCE & OPPORTUNITY AGENT MODELS
# ==============================================================================

class StartupOpportunityRecord(Base):
    """Canonical startup problem / pain point opportunity owned by Core Career Engine."""
    __tablename__ = "startup_opportunities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    service_record_id: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    startup_name: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    domain: Mapped[Optional[str]] = mapped_column(String(150), index=True, nullable=True)
    website_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    category: Mapped[str] = mapped_column(String(50), index=True, default="Development", nullable=False)
    detected_signal: Mapped[str] = mapped_column(Text, nullable=False)
    pain_point_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    urgency_score: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    score_explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    primary_source: Mapped[str] = mapped_column(String(100), default="Direct Search", nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="DISCOVERED", index=True, nullable=False)
    
    # Separated AI Outputs
    ai_insight: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_opportunity: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_pitch_idea: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_model: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    ai_generated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    problem_explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    how_to_solve_strategy: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Social & Direct Founder Contact Channels
    contact_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    twitter_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    github_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    contact_page_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Corroboration & Conflict Metrics
    corroboration_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    has_conflicting_evidence: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    validation_state: Mapped[str] = mapped_column(String(50), default="OBSERVED_PROBLEM", index=True, nullable=False)
    
    # Timestamps (Independent UTC)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    retrieved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    last_checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    evidence_records: Mapped[List["StartupEvidenceRecord"]] = relationship(
        "StartupEvidenceRecord", back_populates="opportunity", cascade="all, delete-orphan"
    )
    tech_findings: Mapped[List["StartupTechFindingRecord"]] = relationship(
        "StartupTechFindingRecord", back_populates="opportunity", cascade="all, delete-orphan"
    )
    corroboration_records: Mapped[List["StartupCorroborationRecord"]] = relationship(
        "StartupCorroborationRecord", back_populates="opportunity", cascade="all, delete-orphan"
    )
    pitch_drafts: Mapped[List["StartupPitchDraftRecord"]] = relationship(
        "StartupPitchDraftRecord", back_populates="opportunity", cascade="all, delete-orphan"
    )
    saved_by: Mapped[List["SavedStartupOpportunityRecord"]] = relationship(
        "SavedStartupOpportunityRecord", back_populates="opportunity", cascade="all, delete-orphan"
    )
    workspaces: Mapped[List["StartupOpportunityWorkspaceRecord"]] = relationship(
        "StartupOpportunityWorkspaceRecord", back_populates="opportunity", cascade="all, delete-orphan"
    )


class StartupEvidenceRecord(Base):
    """Immutable evidence audit record preserving original observations and provenance."""
    __tablename__ = "startup_evidence"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    opportunity_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("startup_opportunities.id", ondelete="CASCADE"), index=True, nullable=False
    )
    source_title: Mapped[str] = mapped_column(String(300), nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    publisher: Mapped[str] = mapped_column(String(100), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), default="PERMITTED_PUBLIC_SOURCE", nullable=False)
    observation_excerpt: Mapped[str] = mapped_column(Text, nullable=False)
    collection_method: Mapped[str] = mapped_column(String(50), default="RSS_FEED", nullable=False)
    source_limitations: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    last_checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    is_corroborating: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    opportunity: Mapped["StartupOpportunityRecord"] = relationship(
        "StartupOpportunityRecord", back_populates="evidence_records"
    )


class StartupTechFindingRecord(Base):
    """Observed technographic stack findings with exact traceability to evidence."""
    __tablename__ = "startup_tech_findings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    opportunity_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("startup_opportunities.id", ondelete="CASCADE"), index=True, nullable=False
    )
    evidence_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("startup_evidence.id", ondelete="SET NULL"), nullable=True
    )
    technology_name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="Framework", nullable=False)
    finding_type: Mapped[str] = mapped_column(String(50), default="AUDIT_DETECTED", nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    traceable_evidence: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    opportunity: Mapped["StartupOpportunityRecord"] = relationship(
        "StartupOpportunityRecord", back_populates="tech_findings"
    )


class StartupCorroborationRecord(Base):
    """Independent source corroboration or contradictory signal record."""
    __tablename__ = "startup_corroborations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    opportunity_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("startup_opportunities.id", ondelete="CASCADE"), index=True, nullable=False
    )
    source_identifier: Mapped[str] = mapped_column(String(200), nullable=False)
    source_name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_independent: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    conflicts_with_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    opportunity: Mapped["StartupOpportunityRecord"] = relationship(
        "StartupOpportunityRecord", back_populates="corroboration_records"
    )


class StartupPitchDraftRecord(Base):
    """Candidate-tailored pitch drafts with explicit assumptions checklist (Draft only, no send)."""
    __tablename__ = "startup_pitch_drafts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    opportunity_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("startup_opportunities.id", ondelete="CASCADE"), index=True, nullable=False
    )
    candidate_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    tone: Mapped[str] = mapped_column(String(30), default="casual", nullable=False)
    candidate_grounded_skills: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    explicit_assumptions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    candidate_edits_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="startup_pitch_drafts")
    opportunity: Mapped["StartupOpportunityRecord"] = relationship(
        "StartupOpportunityRecord", back_populates="pitch_drafts"
    )


class SavedStartupOpportunityRecord(Base):
    """Bookmarks for candidate startup opportunities."""
    __tablename__ = "saved_startup_opportunities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    opportunity_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("startup_opportunities.id", ondelete="CASCADE"), index=True, nullable=False
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="saved_startup_opportunities")
    opportunity: Mapped["StartupOpportunityRecord"] = relationship(
        "StartupOpportunityRecord", back_populates="saved_by"
    )


class StartupOpportunityWorkspaceRecord(Base):
    """Candidate's working canvas for turning an observed startup problem into an actionable venture / solution."""
    __tablename__ = "startup_opportunity_workspaces"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    opportunity_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("startup_opportunities.id", ondelete="CASCADE"), index=True, nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    target_persona: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    hypotheses_json: Mapped[Optional[list]] = mapped_column(JSON, default=list, nullable=True)
    competitor_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    interview_questions_json: Mapped[Optional[list]] = mapped_column(JSON, default=list, nullable=True)
    validation_checklist_json: Mapped[Optional[list]] = mapped_column(JSON, default=list, nullable=True)
    solution_architecture: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    candidate_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    opportunity: Mapped["StartupOpportunityRecord"] = relationship(
        "StartupOpportunityRecord", back_populates="workspaces"
    )
    user: Mapped["User"] = relationship("User", back_populates="startup_workspaces")


# ==============================================================================
# PHASE 11: UNIFIED OPPORTUNITY ENGINE & CANDIDATE FEEDBACK
# ==============================================================================

class CandidateOpportunityFeedbackRecord(Base):
    """Candidate relevance feedback on unified opportunities (isolated per candidate)."""
    __tablename__ = "candidate_opportunity_feedback"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    opportunity_type: Mapped[str] = mapped_column(String(30), index=True, nullable=False)
    opportunity_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    feedback_category: Mapped[str] = mapped_column(String(50), nullable=False)
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="opportunity_feedbacks")


# ==============================================================================
# PHASE 12: MARKET & COMPENSATION INTELLIGENCE
# ==============================================================================

class MarketDataSourceRecord(Base):
    """Documented registry of market data sources, permissions, licenses and limitations."""
    __tablename__ = "market_data_sources"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    source_code: Mapped[str] = mapped_column(String(60), unique=True, index=True, nullable=False)
    source_name: Mapped[str] = mapped_column(String(150), nullable=False)
    provider: Mapped[str] = mapped_column(String(150), nullable=False)
    source_category: Mapped[str] = mapped_column(String(60), default="OBSERVED_POSTINGS", nullable=False)
    documentation_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    access_method: Mapped[str] = mapped_column(String(60), default="LOCAL_CANONICAL_INDEX", nullable=False)
    license_type: Mapped[str] = mapped_column(String(100), default="PROPRIETARY_OBSERVATION", nullable=False)
    commercial_use_permitted: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    attribution_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    attribution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    permitted_storage_days: Mapped[int] = mapped_column(Integer, default=365, nullable=False)
    geographic_coverage: Mapped[str] = mapped_column(String(100), default="GLOBAL", nullable=False)
    update_frequency: Mapped[str] = mapped_column(String(50), default="DAILY", nullable=False)
    known_limitations: Mapped[str] = mapped_column(Text, nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)


class SkillTaxonomyRecord(Base):
    """Canonical technology and professional skills in the RIGHT FIT taxonomy."""
    __tablename__ = "market_skills"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    canonical_name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(80), index=True, default="General", nullable=False)
    parent_category: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    technology_family: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    taxonomy_version: Mapped[str] = mapped_column(String(20), default="1.0.0", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    aliases: Mapped[List["SkillAliasRecord"]] = relationship(
        "SkillAliasRecord", back_populates="skill", cascade="all, delete-orphan", lazy="selectin"
    )
    demand_snapshots: Mapped[List["SkillDemandSnapshotRecord"]] = relationship(
        "SkillDemandSnapshotRecord", back_populates="skill", cascade="all, delete-orphan"
    )


class SkillAliasRecord(Base):
    """Curated and reviewed aliases mapping raw skill strings to canonical skills."""
    __tablename__ = "market_skill_aliases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    skill_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("market_skills.id", ondelete="CASCADE"), index=True, nullable=False
    )
    alias_normalized: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    alias_display: Mapped[str] = mapped_column(String(100), nullable=False)
    source: Mapped[str] = mapped_column(String(50), default="CANONICAL_CURATED", nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    skill: Mapped["SkillTaxonomyRecord"] = relationship("SkillTaxonomyRecord", back_populates="aliases")


class SkillRelationshipRecord(Base):
    """Structured relationships between canonical skills (Parent-Child, Synonyms, Related, Transferable)."""
    __tablename__ = "market_skill_relationships"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    source_skill_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("market_skills.id", ondelete="CASCADE"), index=True, nullable=False
    )
    target_skill_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("market_skills.id", ondelete="CASCADE"), index=True, nullable=False
    )
    relationship_type: Mapped[str] = mapped_column(
        String(32), default="RELATED", index=True, nullable=False
    )  # PARENT_CHILD, SYNONYM, RELATED, TRANSFERABLE
    strength: Mapped[float] = mapped_column(Float, default=0.7, nullable=False)  # 0.0 to 1.0
    notes: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    source_skill: Mapped["SkillTaxonomyRecord"] = relationship(
        "SkillTaxonomyRecord", foreign_keys=[source_skill_id], lazy="selectin"
    )
    target_skill: Mapped["SkillTaxonomyRecord"] = relationship(
        "SkillTaxonomyRecord", foreign_keys=[target_skill_id], lazy="selectin"
    )


class SkillDemandSnapshotRecord(Base):
    """Historical or scheduled demand snapshots across time windows and roles."""
    __tablename__ = "market_skill_demand_snapshots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    skill_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("market_skills.id", ondelete="CASCADE"), index=True, nullable=False
    )
    role_category: Mapped[str] = mapped_column(String(100), default="ALL", index=True, nullable=False)
    geography: Mapped[str] = mapped_column(String(100), default="GLOBAL", index=True, nullable=False)
    time_window: Mapped[str] = mapped_column(String(20), default="30d", index=True, nullable=False)
    distinct_opportunity_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    distinct_employer_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    distinct_source_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    first_observed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_observed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    trend_direction: Mapped[str] = mapped_column(String(40), default="STABLE_IN_SAMPLE", nullable=False)
    period_over_period_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    confidence_level: Mapped[str] = mapped_column(
        String(50), default="MODERATE_CONFIDENCE_LIMITED_SOURCES", nullable=False
    )
    limitations_disclosure: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    snapshot_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, index=True, nullable=False
    )

    skill: Mapped["SkillTaxonomyRecord"] = relationship("SkillTaxonomyRecord", back_populates="demand_snapshots")


class CompensationObservationRecord(Base):
    """Granular, audited compensation observations strictly separating base, total, and currency."""
    __tablename__ = "market_compensation_observations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    opportunity_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("canonical_opportunities.id", ondelete="CASCADE"), index=True, nullable=True
    )
    role_title: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    skill_slug: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    geography: Mapped[str] = mapped_column(String(100), default="Remote", index=True, nullable=False)
    country: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    compensation_type: Mapped[str] = mapped_column(
        String(30), default="BASE_SALARY", index=True, nullable=False
    )
    period: Mapped[str] = mapped_column(String(20), default="ANNUAL", nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    min_amount: Mapped[float] = mapped_column(Float, nullable=False)
    max_amount: Mapped[float] = mapped_column(Float, nullable=False)
    median_amount: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_estimated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    source_provider: Mapped[str] = mapped_column(String(100), default="CORE_ATS_CONNECTOR", nullable=False)
    sample_size: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    methodology_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class CandidateSkillGapRecommendationRecord(Base):
    """Evidence-based skill gap recommendations comparing candidate profile with market demand."""
    __tablename__ = "candidate_skill_gap_recommendations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    target_role: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    canonical_skill_name: Mapped[str] = mapped_column(String(100), nullable=False)
    skill_slug: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(80), default="Technical", nullable=False)
    importance_level: Mapped[str] = mapped_column(String(40), default="HIGH_FREQUENCY", nullable=False)
    frequency_in_role_sample_pct: Mapped[float] = mapped_column(Float, nullable=False)
    candidate_evidence_status: Mapped[str] = mapped_column(String(40), default="MISSING", nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="UNREVIEWED", index=True, nullable=False)
    reason_narrative: Mapped[str] = mapped_column(Text, nullable=False)
    supporting_job_sample: Mapped[List[Any]] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="skill_gap_recommendations")


# ==============================================================================
# PHASE 14: BETA TESTING, PRODUCT VALIDATION & DATA QUALITY MODELS
# ==============================================================================

class BetaFeedbackRecord(Base):
    """Structured user feedback covering search relevance, job details, broken links, usability, and data quality."""
    __tablename__ = "beta_feedback"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True
    )
    category: Mapped[str] = mapped_column(String(60), index=True, nullable=False)
    related_feature: Mapped[str] = mapped_column(String(60), default="GENERAL", nullable=False)
    related_record_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="MEDIUM", nullable=False)
    review_status: Mapped[str] = mapped_column(String(30), default="NEW", index=True, nullable=False)
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    responsible_owner: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    user: Mapped[Optional["User"]] = relationship("User", back_populates="beta_feedbacks")


class BetaConsentRecord(Base):
    """Explicit, auditable user consent records for beta participation with data retention controls."""
    __tablename__ = "beta_consent_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    consent_version: Mapped[str] = mapped_column(String(30), default="v1.0-beta", nullable=False)
    has_consented_data_collection: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    has_consented_ai_processing: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    has_consented_anonymized_analytics: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    consented_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    withdrawn_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    data_retention_expiry: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="beta_consents")


class ConnectorHealthSnapshotRecord(Base):
    """Granular execution log and reliability metrics for every job source connector."""
    __tablename__ = "connector_health_snapshots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    source_key: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    run_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, index=True, nullable=False
    )
    status: Mapped[str] = mapped_column(String(30), default="SUCCESS", nullable=False)
    duration_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    records_discovered: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_updated: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_rejected_dedup: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_rejected_quality: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class DataQualityAuditRecord(Base):
    """Aggregate metrics tracking deduplication rates, broken application links, and stale postings."""
    __tablename__ = "data_quality_audits"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    audit_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, index=True, nullable=False
    )
    total_active_listings: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    duplicate_detection_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    false_positive_merge_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    broken_link_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    broken_link_rate_pct: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    closed_listing_detection_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class DiscoveryTaskExecutionRecord(Base):
    """Tracks continuous background discovery runs, schedules, and incremental checkpoints."""
    __tablename__ = "discovery_task_executions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    task_name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    task_type: Mapped[str] = mapped_column(String(50), index=True, nullable=False)  # JOB_DISCOVERY, JOB_VERIFICATION, STARTUP_DISCOVERY, RE_RANKING, HEALTH_CHECK
    source_id: Mapped[Optional[str]] = mapped_column(String(50), index=True, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="PENDING", index=True, nullable=False)  # PENDING, RUNNING, SUCCESS, FAILED, RETRIED, PAUSED
    records_fetched: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_inserted: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_updated: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_rejected: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    checkpoint_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    execution_duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class DiscoveryScheduleConfigRecord(Base):
    """Configurable refresh intervals, rate limits, and pause states per source."""
    __tablename__ = "discovery_schedule_configs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    source_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    source_name: Mapped[str] = mapped_column(String(100), nullable=False)
    interval_seconds: Mapped[int] = mapped_column(Integer, default=1800, nullable=False)  # e.g., 30 mins
    is_paused: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    max_records_per_run: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    rate_limit_per_minute: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    last_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    next_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)










