"""
RIGHT FIT Core — Unified Opportunities & Candidate Dashboard REST API Router
Version: 1.0.0
Phase: 11 — Unified Opportunities Engine and Dashboard

Exposes multi-source aggregation, unified metrics, polymorphic bookmarking,
and isolated candidate relevance feedback.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_optional_current_user
from app.db.models import User
from app.services.unified_opportunity_service import UnifiedOpportunityService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Unified Opportunities & Dashboard"])


# -----------------------------------------------------------------------------
# Request Schemas
# -----------------------------------------------------------------------------

class SaveOpportunityRequest(BaseModel):
    notes: Optional[str] = Field(default=None, description="Candidate's private bookmark notes")
    category: Optional[str] = Field(default=None, description="Folder/Tag category: HIGH_FIT, APPLY_SOON, OUTREACH_LEAD, STARTUP_SOLVE, RESEARCHING")


class OpportunityFeedbackRequest(BaseModel):
    feedback_category: str = Field(
        ...,
        description="Category: IRRELEVANT, ALREADY_APPLIED, INCORRECT_SKILLS, WRONG_LOCATION, OTHER",
    )
    explanation: Optional[str] = Field(default=None, description="Optional candidate explanation")


# -----------------------------------------------------------------------------
# Endpoints
# -----------------------------------------------------------------------------

@router.post("/opportunities/refresh", summary="Dynamically refresh real-time market signals and opportunities")
async def refresh_opportunities(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """
    Dynamically scans and injects fresh real-time opportunities and startup pain points
    across multiple disciplines (Engineering, Marketing, Sales, Product, Finance, Ops).
    """
    refreshed_count = await UnifiedOpportunityService.refresh_market_signals(db)
    return {
        "success": True,
        "message": f"Successfully synced and refreshed {refreshed_count} market signals.",
        "refreshed_count": refreshed_count,
    }


@router.get("/dashboard", summary="Unified candidate dashboard metrics and recent opportunities")
async def get_dashboard(
    refresh: bool = Query(default=False, description="Whether to bypass cache and fetch live real-time metrics"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """
    Returns reconciled summary metrics and recent cross-module opportunities.
    Reconciles: total_opportunities == total_jobs + total_freelance + total_startups.
    """
    user_id = current_user.id if current_user else None
    if refresh:
        UnifiedOpportunityService.clear_caches()
    data = await UnifiedOpportunityService.get_unified_dashboard_metrics(db, user_id=user_id, force_fresh=refresh)
    return {
        "success": True,
        "data": data,
    }


@router.get("/opportunities/all", summary="Unified multi-source opportunity aggregation feed")
async def list_unified_opportunities(
    type: str = Query(default="ALL", description="Opportunity type: ALL, JOB, FREELANCE, STARTUP_PAIN_POINT"),
    resume_id: Optional[str] = Query(default=None, description="Resume ID to dynamically calculate candidate fit against"),
    search: Optional[str] = Query(default=None, description="Search term for title or organization"),
    category: Optional[str] = Query(default=None, description="Category filter"),
    discipline: Optional[str] = Query(default=None, description="Discipline: MARKETING_GROWTH, SALES_BD, PRODUCT_DESIGN, FINANCE_ACCOUNTING, OPERATIONS_LOGISTICS, HR_TALENT, CUSTOMER_SUCCESS, DATA_ANALYTICS, HEALTHCARE_MEDICAL, LEGAL_COMPLIANCE, SOFTWARE_ENGINEERING"),
    sort_by: str = Query(default="BEST_FIT", description="Sort by: BEST_FIT, NEWEST, URGENCY"),
    refresh: bool = Query(default=False, description="Whether to trigger fresh signal refresh"),
    source: Optional[str] = Query(default=None, description="Source platform filter"),
    min_score: Optional[int] = Query(default=None, ge=1, le=10, description="Minimum urgency/rating score"),
    employment_type: Optional[str] = Query(default=None, description="Employment type filter: FULL_TIME, INTERNSHIP, CONTRACT"),
    page: int = Query(default=1, ge=1, description="Page number"),
    per_page: int = Query(default=20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """
    Aggregates opportunities across Core Canonical Jobs, LeadHunter Freelance Leads,
    and Startup Intelligence Pain Points into standard OpportunityEnvelopes.
    Adapts dynamically to the candidate's resume/domain and calculates why the candidate fits.
    """
    user_id = current_user.id if current_user else None
    result = await UnifiedOpportunityService.aggregate_opportunities(
        session=db,
        opportunity_type=type.upper(),
        resume_id=resume_id,
        search=search,
        category=category,
        source=source,
        min_score=min_score,
        page=page,
        per_page=per_page,
        user_id=user_id,
        discipline=discipline,
        sort_by=sort_by,
        refresh=refresh,
        employment_type=employment_type,
    )
    return result


@router.get("/opportunities/saved/all", summary="List all saved opportunities across types")
async def list_saved_opportunities(
    category: Optional[str] = Query(default=None, description="Filter by bookmark folder category"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns candidate's saved items across Jobs, Freelance, and Startups with category categorization."""
    saved_items = await UnifiedOpportunityService.list_all_saved_opportunities(
        user_id=current_user.id,
        session=db,
        category_filter=category,
    )
    return {
        "success": True,
        "data": saved_items,
        "total": len(saved_items),
    }


@router.post("/opportunities/{opportunity_type}/{opportunity_id}/save", summary="Save an opportunity polymorphically")
async def save_opportunity(
    opportunity_type: str,
    opportunity_id: str,
    body: Optional[SaveOpportunityRequest] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Bookmarks a Job, Freelance, or Startup opportunity for the candidate with optional category."""
    notes = body.notes if body else None
    category = body.category if body else None
    try:
        saved = await UnifiedOpportunityService.save_unified_opportunity(
            user_id=current_user.id,
            opportunity_type=opportunity_type,
            opportunity_id=opportunity_id,
            notes=notes,
            category=category,
            session=db,
        )
        return {
            "success": True,
            "message": f"Successfully saved {opportunity_type.lower()} opportunity",
            "data": saved,
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/opportunities/{opportunity_type}/{opportunity_id}/save", summary="Unsave an opportunity polymorphically")
async def unsave_opportunity(
    opportunity_type: str,
    opportunity_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Removes a bookmark for a Job, Freelance, or Startup opportunity."""
    removed = await UnifiedOpportunityService.unsave_unified_opportunity(
        user_id=current_user.id,
        opportunity_type=opportunity_type,
        opportunity_id=opportunity_id,
        session=db,
    )
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Saved {opportunity_type.lower()} opportunity not found or already removed",
        )
    return {
        "success": True,
        "message": f"Successfully removed {opportunity_type.lower()} bookmark",
    }


@router.post("/opportunities/{opportunity_type}/{opportunity_id}/feedback", summary="Submit candidate relevance feedback")
async def submit_opportunity_feedback(
    opportunity_type: str,
    opportunity_id: str,
    body: OpportunityFeedbackRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Records candidate relevance feedback (e.g., IRRELEVANT, ALREADY_APPLIED).
    Strictly candidate-isolated; does NOT alter source verification, evidence, or universal scores.
    """
    valid_categories = {
        "RELEVANT",
        "NOT_RELEVANT",
        "IRRELEVANT",
        "WRONG_SKILLS",
        "INCORRECT_SKILLS",
        "EXPERIENCE_TOO_HIGH",
        "EXPERIENCE_TOO_LOW",
        "LOCATION_UNSUITABLE",
        "WRONG_LOCATION",
        "WORK_MODE_UNSUITABLE",
        "ALREADY_APPLIED",
        "DUPLICATE",
        "JOB_CLOSED",
        "NOT_INTERESTED",
        "OTHER",
    }
    cat_upper = body.feedback_category.upper()
    if cat_upper not in valid_categories:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid feedback category. Must be one of: {', '.join(sorted(valid_categories))}",
        )

    feedback = await UnifiedOpportunityService.record_candidate_feedback(
        user_id=current_user.id,
        opportunity_type=opportunity_type,
        opportunity_id=opportunity_id,
        feedback_category=body.feedback_category,
        explanation=body.explanation,
        session=db,
    )
    return {
        "success": True,
        "message": "Feedback submitted successfully. Your preference has been recorded.",
        "data": {
            "id": feedback.id,
            "opportunity_id": feedback.opportunity_id,
            "opportunity_type": feedback.opportunity_type,
            "feedback_category": feedback.feedback_category,
            "recorded_at": feedback.created_at.isoformat() if feedback.created_at else None,
        },
    }

