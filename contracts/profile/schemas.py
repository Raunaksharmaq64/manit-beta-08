"""
RIGHT FIT — Candidate Profile & Preferences Schemas
Version: 1.0.0
Phase: 3 — Identity, Candidate Profile & Privacy Foundation
"""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class FieldProvenance(StrEnum):
    """Source provenance tracking for profile data attributes."""
    USER_PROVIDED = "USER_PROVIDED"
    RESUME_EXTRACTED = "RESUME_EXTRACTED"
    AI_SUGGESTED = "AI_SUGGESTED"
    IMPORTED = "IMPORTED"
    VERIFIED = "VERIFIED"


class RemotePreference(StrEnum):
    """Work arrangement preference."""
    REMOTE = "REMOTE"
    HYBRID = "HYBRID"
    ON_SITE = "ON_SITE"
    ANY = "ANY"


# ------------------------------------------------------------------------------
# Education
# ------------------------------------------------------------------------------

class EducationCreate(BaseModel):
    institution: str = Field(..., min_length=2, max_length=255)
    degree: str = Field(..., min_length=2, max_length=255)
    field_of_study: str = Field(..., min_length=2, max_length=255)
    start_date: Optional[str] = Field(default=None, description="YYYY-MM or YYYY format")
    end_date: Optional[str] = Field(default=None, description="YYYY-MM or YYYY format")
    is_current: bool = Field(default=False)
    achievements: Optional[str] = Field(default=None, max_length=1000)
    provenance: FieldProvenance = Field(default=FieldProvenance.USER_PROVIDED)


class EducationResponse(EducationCreate):
    id: str = Field(..., description="Unique education entry UUID.")


# ------------------------------------------------------------------------------
# Experience
# ------------------------------------------------------------------------------

class ExperienceCreate(BaseModel):
    company: str = Field(..., min_length=2, max_length=255)
    role: str = Field(..., min_length=2, max_length=255)
    employment_type: str = Field(default="Full-time", max_length=100)
    start_date: Optional[str] = Field(default=None, description="YYYY-MM or YYYY")
    end_date: Optional[str] = Field(default=None, description="YYYY-MM or YYYY")
    is_current: bool = Field(default=False)
    description: Optional[str] = Field(default=None, max_length=4000)
    skills: List[str] = Field(default_factory=list)
    provenance: FieldProvenance = Field(default=FieldProvenance.USER_PROVIDED)


class ExperienceResponse(ExperienceCreate):
    id: str = Field(..., description="Unique experience entry UUID.")


# ------------------------------------------------------------------------------
# Skills
# ------------------------------------------------------------------------------

class SkillCreate(BaseModel):
    skill_name: str = Field(..., min_length=1, max_length=80)
    category: str = Field(default="Technical", max_length=50)
    proficiency: str = Field(default="Intermediate", max_length=30)  # Beginner, Intermediate, Expert
    years_experience: Optional[float] = Field(default=None, ge=0)
    provenance: FieldProvenance = Field(default=FieldProvenance.USER_PROVIDED)


class SkillResponse(SkillCreate):
    id: str = Field(..., description="Unique skill entry UUID.")


# ------------------------------------------------------------------------------
# Profile
# ------------------------------------------------------------------------------

class CandidateProfileUpdate(BaseModel):
    headline: Optional[str] = Field(default=None, max_length=140)
    summary: Optional[str] = Field(default=None, max_length=2000)
    phone: Optional[str] = Field(default=None, max_length=30)
    city: Optional[str] = Field(default=None, max_length=80)
    state: Optional[str] = Field(default=None, max_length=80)
    country: Optional[str] = Field(default=None, max_length=80)
    timezone: Optional[str] = Field(default=None, max_length=50)


class CandidateProfileResponse(BaseModel):
    id: str = Field(..., description="Profile UUID.")
    user_id: str = Field(..., description="Owner User UUID.")
    headline: Optional[str] = None
    summary: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    timezone: Optional[str] = None
    education: List[EducationResponse] = Field(default_factory=list)
    experience: List[ExperienceResponse] = Field(default_factory=list)
    skills: List[SkillResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class CompletenessSectionImpact(BaseModel):
    """Explains why each profile section matters and what matching capabilities it unlocks."""
    section_key: str
    section_name: str
    is_completed: bool
    weight_percentage: int
    why_it_matters: str
    unlocks: str
    is_required: bool = False


class ProfileCompletenessResponse(BaseModel):
    """Calculated profile completeness score and explainable section impact metrics."""
    score_percentage: int = Field(..., ge=0, le=100)
    has_basic_info: bool = Field(...)
    has_education: bool = Field(...)
    has_experience: bool = Field(...)
    has_skills: bool = Field(...)
    has_preferences: bool = Field(...)
    missing_sections: List[str] = Field(default_factory=list)
    section_breakdown: List[CompletenessSectionImpact] = Field(default_factory=list)


# ------------------------------------------------------------------------------
# Preferences
# ------------------------------------------------------------------------------

class CandidatePreferencesUpdate(BaseModel):
    preferred_roles: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    preferred_industries: List[str] = Field(default_factory=list)
    preferred_locations: List[str] = Field(default_factory=list)
    remote_preference: RemotePreference = Field(default=RemotePreference.ANY)
    min_salary: Optional[float] = Field(default=None, ge=0)
    max_salary: Optional[float] = Field(default=None, ge=0)
    currency: str = Field(default="USD", max_length=3)
    employment_types: List[str] = Field(default_factory=lambda: ["Full-time"])
    job_notification_frequency: str = Field(default="DAILY")  # IMMEDIATE, DAILY, WEEKLY, NEVER


class CandidatePreferencesResponse(CandidatePreferencesUpdate):
    id: str = Field(..., description="Preference record UUID.")
    user_id: str = Field(..., description="Owner User UUID.")
    updated_at: datetime

