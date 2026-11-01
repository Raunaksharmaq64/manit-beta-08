"""
RIGHT FIT Core — Resume Intelligence Endpoints
API routes for secure upload, extraction, evidence review, and ATS analysis.
Phase: 4 — Resume Intelligence & Reviewed Candidate Evidence
"""

from __future__ import annotations

import io
import urllib.parse
import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from contracts.resume.schemas import (
    ATSAnalysisRequest,
    ATSAnalysisResponse,
    ResumeConfirmSyncRequest,
    ResumeConfirmSyncResponse,
    ResumeExtractionResponse,
    ResumeReviewFieldUpdate,
    ResumeReviewResponse,
    ResumeSummaryResponse,
    ResumeUploadResponse,
    ResumeVersionResponse,
    ResumeQualityReportResponse,
    ResumeJobMatchRequest,
    ResumeJobMatchResponse,
    ResumeAISuggestionsResponse,
    AISuggestionDTO,
    SuggestionActionRequest,
    SuggestionActionResponse,
    ResumeVersionDiffResponse,
    SuggestedJobResponse,
)
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.db.models import (
    ATSAnalysisRecord,
    ResumeExtractionRecord,
    ResumeJobMatchRecord,
    ResumeAISuggestionActionRecord,
    ResumeRecord,
    ResumeVersionRecord,
    CanonicalOpportunityRecord,
    CandidateProfile,
    CandidateSkillRecord,
    User,
)
from app.services.ats_service import ats_service
from app.services.resume_service import resume_service
from app.services.review_service import review_service
from app.services.storage_service import StorageSecurityError, storage_service
from app.services.resume_quality_service import resume_quality_analyzer
from app.services.resume_job_matcher import resume_job_matcher
from app.services.resume_ai_service import resume_ai_service

router = APIRouter(prefix="/resumes", tags=["Resume Intelligence"])


@router.post("", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    title: str = Form("My Resume"),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Securely uploads an initial resume document (PDF or DOCX)."""
    try:
        file_bytes = await file.read()
        res = await resume_service.upload_initial_resume(
            db=db,
            user_id=current_user.id,
            title=title,
            file_bytes=file_bytes,
            filename=file.filename or "resume.pdf"
        )
        return res
    except StorageSecurityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("", response_model=List[ResumeSummaryResponse])
async def list_resumes(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Lists all resume containers owned by the candidate."""
    return await resume_service.list_resumes(db, current_user.id)


@router.get("/{resume_id}", response_model=ResumeSummaryResponse)
async def get_resume(
    resume_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves resume summary and active version details."""
    try:
        return await resume_service.get_resume_summary(db, current_user.id, resume_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{resume_id}", status_code=status.HTTP_200_OK)
async def delete_resume(
    resume_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Permanently deletes a resume, all versions, extraction data, and stored files."""
    try:
        await resume_service.delete_resume(db, current_user.id, resume_id)
        return {"success": True, "message": "Resume and all associated records deleted."}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{resume_id}/versions", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_new_version(
    resume_id: str,
    version_label: Optional[str] = Form(None),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Uploads an additional version to an existing candidate resume."""
    try:
        file_bytes = await file.read()
        return await resume_service.upload_new_version(
            db=db,
            user_id=current_user.id,
            resume_id=resume_id,
            file_bytes=file_bytes,
            filename=file.filename or "resume.pdf",
            version_label=version_label
        )
    except StorageSecurityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{resume_id}/versions", response_model=List[ResumeVersionResponse])
async def list_versions(
    resume_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Lists all versions of a specific resume."""
    try:
        return await resume_service.list_versions(db, current_user.id, resume_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch("/{resume_id}/active-version", response_model=ResumeSummaryResponse)
async def set_active_version(
    resume_id: str,
    version_id: str = Query(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Designates a specific version as the active resume."""
    try:
        return await resume_service.set_active_version(db, current_user.id, resume_id, version_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{resume_id}/parse", response_model=ResumeExtractionResponse)
async def parse_resume(
    resume_id: str,
    version_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Triggers the document text extraction and structured parsing pipeline."""
    try:
        return await resume_service.execute_parse_pipeline(
            db=db,
            user_id=current_user.id,
            resume_id=resume_id,
            version_id=version_id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{resume_id}/extraction", response_model=ResumeExtractionResponse)
async def get_extraction(
    resume_id: str,
    version_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves structured extractions and evidence for a parsed resume."""
    try:
        return await resume_service.get_extraction(db, current_user.id, resume_id, version_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{resume_id}/review", response_model=ResumeReviewResponse)
async def get_review_workbench(
    resume_id: str,
    version_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves review workbench state with profile conflict detection."""
    try:
        # Resolve target version
        if not version_id:
            summary = await resume_service.get_resume_summary(db, current_user.id, resume_id)
            if not summary.active_version_id:
                raise ValueError("Active version not found.")
            target_version_id = summary.active_version_id
        else:
            target_version_id = version_id

        return await review_service.get_or_create_review(db, target_version_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch("/{resume_id}/review", response_model=ResumeReviewResponse)
async def update_field_review(
    resume_id: str,
    update: ResumeReviewFieldUpdate,
    version_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Confirms, corrects, or rejects an extracted field."""
    try:
        if not version_id:
            summary = await resume_service.get_resume_summary(db, current_user.id, resume_id)
            target_version_id = summary.active_version_id
        else:
            target_version_id = version_id

        if not target_version_id:
            raise ValueError("Target version not found.")

        return await review_service.update_field_review(db, target_version_id, current_user.id, update)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{resume_id}/confirm", response_model=ResumeConfirmSyncResponse)
async def confirm_and_sync_profile(
    resume_id: str,
    sync_req: ResumeConfirmSyncRequest,
    version_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Synchronizes candidate-confirmed fields into canonical candidate profile tables."""
    try:
        if not version_id:
            summary = await resume_service.get_resume_summary(db, current_user.id, resume_id)
            target_version_id = summary.active_version_id
        else:
            target_version_id = version_id

        if not target_version_id:
            raise ValueError("Target version not found.")

        return await review_service.sync_approved_to_profile(
            db=db,
            version_id=target_version_id,
            user_id=current_user.id,
            sync_req=sync_req
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{resume_id}/ats-analysis", response_model=ATSAnalysisResponse)
async def analyze_ats_compatibility(
    resume_id: str,
    req: ATSAnalysisRequest,
    version_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Evaluates ATS keyword coverage, bullet impact, and non-fabricating advice."""
    try:
        ext = await resume_service.get_extraction(db, current_user.id, resume_id, version_id)

        # Collect bullets from experience and projects
        bullets: List[str] = []
        for exp in ext.experience:
            bullets.extend(exp.get("responsibilities", []))
        for proj in ext.projects:
            if proj.get("description"):
                bullets.append(proj["description"])

        # Fetch raw text
        stmt_ext = select(ResumeExtractionRecord).where(
            ResumeExtractionRecord.resume_version_id == ext.version_id
        )
        res_ext = await db.execute(stmt_ext)
        ext_record = res_ext.scalar_one()

        analysis_data = ats_service.analyze_resume_for_ats(
            resume_text=ext_record.raw_text,
            job_title=req.target_job_title,
            job_description=req.target_job_description,
            bullets=bullets,
            extractions={
                "personal_info": ext.personal_info,
                "sections": ext_record.sections_json
            }
        )

        analysis_record = ATSAnalysisRecord(
            resume_version_id=ext.version_id,
            user_id=current_user.id,
            target_job_title=req.target_job_title,
            target_job_description=req.target_job_description,
            coverage_score=analysis_data["coverage_score"],
            matched_keywords_json=analysis_data["matched_keywords"],
            missing_keywords_json=analysis_data["missing_keywords"],
            bullet_impact_score=analysis_data["bullet_impact_score"],
            bullet_impact_analysis_json=analysis_data["bullet_impact_analysis"],
            actionable_suggestions_json=analysis_data["actionable_suggestions"],
            formatting_observations_json=analysis_data["formatting_observations"],
            methodology_and_limitations=analysis_data["methodology_and_limitations"]
        )
        db.add(analysis_record)
        await db.commit()
        await db.refresh(analysis_record)

        return ATSAnalysisResponse(
            analysis_id=analysis_record.id,
            resume_id=resume_id,
            version_id=ext.version_id,
            target_job_title=req.target_job_title,
            coverage_score=analysis_record.coverage_score,
            matched_keywords=analysis_record.matched_keywords_json,
            missing_keywords=analysis_record.missing_keywords_json,
            bullet_impact_score=analysis_record.bullet_impact_score,
            bullet_impact_analysis=analysis_record.bullet_impact_analysis_json,
            actionable_suggestions=analysis_record.actionable_suggestions_json,
            formatting_observations=analysis_record.formatting_observations_json,
            methodology_and_limitations=analysis_record.methodology_and_limitations,
            created_at=analysis_record.created_at,
            total_relevant_keywords=analysis_data.get("total_relevant_keywords", 0),
            keyword_coverage_percentage=analysis_data.get("keyword_coverage_percentage", 0.0),
            required_keywords=analysis_data.get("required_keywords", []),
            required_matched=analysis_data.get("required_matched", []),
            required_missing=analysis_data.get("required_missing", []),
            preferred_keywords=analysis_data.get("preferred_keywords", []),
            preferred_matched=analysis_data.get("preferred_matched", []),
            preferred_missing=analysis_data.get("preferred_missing", []),
            keyword_details=analysis_data.get("keyword_details"),
            keyword_rankings=analysis_data.get("keyword_rankings", [])
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{resume_id}/ats-analysis/{analysis_id}", response_model=ATSAnalysisResponse)
async def get_ats_analysis(
    resume_id: str,
    analysis_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves an existing ATS analysis result."""
    stmt = select(ATSAnalysisRecord).where(
        ATSAnalysisRecord.id == analysis_id,
        ATSAnalysisRecord.user_id == current_user.id
    )
    res = await db.execute(stmt)
    analysis = res.scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found.")

    return ATSAnalysisResponse(
        analysis_id=analysis.id,
        resume_id=resume_id,
        version_id=analysis.resume_version_id,
        target_job_title=analysis.target_job_title,
        coverage_score=analysis.coverage_score,
        matched_keywords=analysis.matched_keywords_json,
        missing_keywords=analysis.missing_keywords_json,
        bullet_impact_score=analysis.bullet_impact_score,
        bullet_impact_analysis=analysis.bullet_impact_analysis_json,
        actionable_suggestions=analysis.actionable_suggestions_json,
        formatting_observations=analysis.formatting_observations_json,
        methodology_and_limitations=analysis.methodology_and_limitations,
        created_at=analysis.created_at
    )


@router.get("/{resume_id}/quality", response_model=ResumeQualityReportResponse)
@router.get("/{resume_id}/quality-report", response_model=ResumeQualityReportResponse)
async def get_resume_quality_report(
    resume_id: str,
    version_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Evaluates comprehensive resume quality, section scores, readability, and structural hygiene."""
    try:
        ext = await resume_service.get_extraction(db, current_user.id, resume_id, version_id)
        stmt_ext = select(ResumeExtractionRecord).where(
            ResumeExtractionRecord.resume_version_id == ext.version_id
        )
        res_ext = await db.execute(stmt_ext)
        ext_rec = res_ext.scalar_one()

        extractions_dict = {
            "personal_info": ext.personal_info,
            "summary": ext.summary,
            "education": ext.education,
            "experience": ext.experience,
            "skills": ext.skills,
            "projects": ext.projects,
            "certifications": ext.certifications,
            "sections": ext_rec.sections_json,
        }

        return resume_quality_analyzer.analyze_quality(
            resume_id=resume_id,
            version_id=ext.version_id,
            raw_text=ext_rec.raw_text,
            extractions=extractions_dict
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{resume_id}/job-match", response_model=ResumeJobMatchResponse)
async def match_resume_to_job(
    resume_id: str,
    req: ResumeJobMatchRequest,
    version_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Evaluates multi-attribute fit against target job description without hallucinating qualifications."""
    try:
        ext = await resume_service.get_extraction(db, current_user.id, resume_id, version_id)
        stmt_ext = select(ResumeExtractionRecord).where(
            ResumeExtractionRecord.resume_version_id == ext.version_id
        )
        res_ext = await db.execute(stmt_ext)
        ext_rec = res_ext.scalar_one()

        extractions_dict = {
            "personal_info": ext.personal_info,
            "summary": ext.summary,
            "education": ext.education,
            "experience": ext.experience,
            "skills": ext.skills,
            "inferred_skills": ext.inferred_skills,
            "projects": ext.projects,
            "certifications": ext.certifications,
        }

        match_result = resume_job_matcher.match_resume_to_job(
            resume_id=resume_id,
            version_id=ext.version_id,
            target_job_title=req.target_job_title,
            target_job_description=req.target_job_description,
            raw_resume_text=ext_rec.raw_text,
            extractions=extractions_dict
        )

        # Persist the evaluation into resume_job_matches
        match_record = ResumeJobMatchRecord(
            resume_version_id=ext.version_id,
            user_id=current_user.id,
            target_job_title=req.target_job_title,
            target_job_description=req.target_job_description,
            overall_match_score=match_result.overall_match_score,
            keyword_coverage_score=match_result.keyword_coverage_score,
            required_skills_match_json=match_result.required_skills_match,
            preferred_skills_match_json=match_result.preferred_skills_match,
            experience_level_match_json=match_result.experience_level_match,
            project_theme_alignments_json=match_result.project_theme_alignments,
            unverified_matches_json=match_result.unverified_matches,
            job_specific_suggestions_json=match_result.job_specific_suggestions
        )
        db.add(match_record)
        await db.commit()
        await db.refresh(match_record)

        match_result.match_id = match_record.id
        return match_result

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{resume_id}/job-matches", response_model=List[ResumeJobMatchResponse])
async def list_resume_job_matches(
    resume_id: str,
    version_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Lists saved job matching analyses for a resume."""
    stmt = select(ResumeJobMatchRecord).where(ResumeJobMatchRecord.user_id == current_user.id)
    if version_id:
        stmt = stmt.where(ResumeJobMatchRecord.resume_version_id == version_id)
    stmt = stmt.order_by(ResumeJobMatchRecord.created_at.desc())
    res = await db.execute(stmt)
    records = res.scalars().all()
    return [
        ResumeJobMatchResponse(
            match_id=r.id,
            resume_id=resume_id,
            version_id=r.resume_version_id,
            target_job_title=r.target_job_title,
            overall_match_score=r.overall_match_score,
            match_band="STRONG" if (r.overall_match_score or 0) >= 80.0 else ("MODERATE" if (r.overall_match_score or 0) >= 60.0 else "NEEDS_IMPROVEMENT"),
            keyword_coverage_score=r.keyword_coverage_score,
            required_skills_match=r.required_skills_match_json,
            preferred_skills_match=r.preferred_skills_match_json,
            experience_level_match=r.experience_level_match_json,
            hard_skills_match=r.required_skills_match_json,
            experience_fit=r.experience_level_match_json,
            project_theme_alignments=r.project_theme_alignments_json,
            unverified_matches=r.unverified_matches_json,
            job_specific_suggestions=r.job_specific_suggestions_json,
            created_at=r.created_at
        )
        for r in records
    ]


@router.get("/{resume_id}/suggested-jobs", response_model=List[SuggestedJobResponse])
async def get_suggested_jobs_for_resume(
    resume_id: str,
    version_id: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Ranks real active career opportunities dynamically against the candidate's specific
    resume extractions, explicit skills, inferred skills, headline, roles, and project evidence.
    Completely dynamic: switching or uploading a resume recalculates suggestions specifically for that document.
    """
    try:
        # 1. Fetch extraction for this specific resume
        ext = await resume_service.get_extraction(db, current_user.id, resume_id, version_id)

        # 2. Collect candidate skills strictly from this resume's extraction
        candidate_skills_set = set()
        for cat, skill_list in (ext.skills or {}).items():
            if isinstance(skill_list, list):
                for s in skill_list:
                    if isinstance(s, dict):
                        name = s.get("name") or s.get("skill_name")
                        if name:
                            candidate_skills_set.add(str(name).strip())
                    elif isinstance(s, str) and s.strip():
                        candidate_skills_set.add(s.strip())

        # Also incorporate explicit and inferred skills from this resume
        if ext.explicit_skills and isinstance(ext.explicit_skills, dict):
            for cat, skill_list in ext.explicit_skills.items():
                if isinstance(skill_list, list):
                    for s in skill_list:
                        if isinstance(s, dict):
                            name = s.get("name") or s.get("skill_name")
                            if name:
                                candidate_skills_set.add(str(name).strip())
                        elif isinstance(s, str) and s.strip():
                            candidate_skills_set.add(s.strip())

        if ext.inferred_skills and isinstance(ext.inferred_skills, list):
            for s in ext.inferred_skills:
                if isinstance(s, dict):
                    name = s.get("name") or s.get("skill_name")
                    if name:
                        candidate_skills_set.add(str(name).strip())
                elif isinstance(s, str) and s.strip():
                    candidate_skills_set.add(s.strip())

        # Only if this specific resume has zero extracted skills, fallback to profile skills
        if not candidate_skills_set:
            prof_res = await db.execute(
                select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
            )
            profile = prof_res.scalar_one_or_none()
            if profile and profile.skills:
                for cs in profile.skills:
                    candidate_skills_set.add(cs.skill_name.strip())

        candidate_skills_list = sorted(list(candidate_skills_set))
        normalized_candidate_tokens = {s.lower() for s in candidate_skills_list}

        # Extract headline and roles from this resume
        candidate_headline = ""
        if ext.personal_info and isinstance(ext.personal_info, dict):
            candidate_headline = ext.personal_info.get("headline", "") or ""

        candidate_roles: List[str] = []
        for exp in (ext.experience or []):
            if isinstance(exp, dict) and exp.get("role"):
                candidate_roles.append(str(exp["role"]).strip())
        for intern in (ext.internships or []):
            if isinstance(intern, dict) and intern.get("role"):
                candidate_roles.append(str(intern["role"]).strip())

        # Project bullets
        project_bullets: List[str] = []
        for p in (ext.projects or []):
            if isinstance(p, dict):
                parts = []
                if p.get("name"):
                    parts.append(p["name"])
                if p.get("technologies"):
                    parts.append(" ".join(p["technologies"]))
                if p.get("description"):
                    parts.append(p["description"])
                for b in p.get("bullets", []):
                    if b and str(b).strip():
                        parts.append(str(b).strip())
                if parts:
                    project_bullets.append(" — ".join(parts))

        for exp in (ext.experience or []):
            if isinstance(exp, dict):
                for r in exp.get("responsibilities", []):
                    if isinstance(r, str) and r.strip():
                        project_bullets.append(r.strip())
                if exp.get("role"):
                    project_bullets.append(f"{exp['role']} at {exp.get('company', '')}")

        # 3. Query active non-suppressed canonical opportunities (real authentic jobs only)
        stmt_opps = select(CanonicalOpportunityRecord).where(
            CanonicalOpportunityRecord.is_active == True,
            CanonicalOpportunityRecord.is_suppressed == False,
            CanonicalOpportunityRecord.application_url.notlike("%example.com%")
        )
        res_opps = await db.execute(stmt_opps)
        opportunities = res_opps.scalars().all()

        if not opportunities:
            return []

        scored_suggestions: List[SuggestedJobResponse] = []

        for opp in opportunities:
            req_skills = opp.required_skills_json or []
            combined_jd_text = f"{opp.title}\n{opp.description_clean}"

            # Skills fit calculation
            matched_skills: List[str] = []
            missing_skills: List[str] = []

            for req in req_skills:
                clean_req = req.strip()
                req_lower = clean_req.lower()
                # Check direct or token containment
                if any(cand in req_lower or req_lower in cand for cand in normalized_candidate_tokens):
                    matched_skills.append(clean_req)
                else:
                    missing_skills.append(clean_req)

            # Check if any candidate skills appear in the full JD description
            jd_tokens = resume_job_matcher.tokenize(combined_jd_text)
            jd_token_set = set(jd_tokens)
            for c_skill in candidate_skills_list:
                c_clean = c_skill.strip()
                if c_clean.lower() in jd_token_set and c_clean not in matched_skills:
                    matched_skills.append(c_clean)

            # Portfolio theme overlap
            portfolio_alignment_score = 0.0
            if project_bullets and req_skills:
                try:
                    portfolio_res = resume_job_matcher.align_portfolio_themes(
                        portfolio_bullets=project_bullets,
                        jd_themes=req_skills[:5]
                    )
                    if portfolio_res:
                        portfolio_alignment_score = min(1.0, len(portfolio_res) / max(1, len(req_skills[:5])))
                except Exception:
                    portfolio_alignment_score = 0.0

            # Title & Domain overlap
            t_tokens = set(resume_job_matcher.tokenize(opp.title.lower()))
            h_tokens = set(resume_job_matcher.tokenize(f"{candidate_headline} {' '.join(candidate_roles)}".lower()))
            title_overlap = len(t_tokens.intersection(h_tokens)) / max(1, len(t_tokens)) if t_tokens else 0.0

            # Compute weighted fit score dynamically
            if req_skills:
                req_match_ratio = len([s for s in matched_skills if s in req_skills]) / max(1, len(req_skills))
            else:
                req_match_ratio = 0.45

            raw_fit = (req_match_ratio * 0.45) + (title_overlap * 0.35) + (portfolio_alignment_score * 0.20)
            overall_score = round(45.0 + (raw_fit * 50.0), 1)
            overall_score = max(38.0, min(97.5, overall_score))

            loc_str = "Remote"
            if opp.city and opp.country:
                loc_str = f"{opp.city}, {opp.country}"
            elif opp.country:
                loc_str = opp.country
            if opp.is_remote and "Remote" not in loc_str:
                loc_str = f"{loc_str} (Remote)"

            salary_str = None
            if opp.min_salary and opp.max_salary:
                salary_str = f"${int(opp.min_salary):,} - ${int(opp.max_salary):,} {opp.currency or 'USD'}"
            elif opp.min_salary:
                salary_str = f"${int(opp.min_salary):,}+ {opp.currency or 'USD'}"

            desc_snippet = opp.description_clean[:220].strip() + ("..." if len(opp.description_clean) > 220 else "")

            # Vacancy verification and age calculation
            from datetime import datetime, timezone
            now_dt = datetime.now(timezone.utc)
            first_seen = opp.first_seen_at or now_dt
            first_seen_utc = first_seen if first_seen.tzinfo else first_seen.replace(tzinfo=timezone.utc)
            age_days = max(0.1, round((now_dt - first_seen_utc).total_seconds() / 86400.0, 1))

            v_status = opp.verification_status or "OPEN_CONFIRMED"
            fresh_state = opp.freshness_state or ("FRESH" if age_days <= 7 else "AGING" if age_days <= 21 else "STALE")

            if v_status == "OPEN_CONFIRMED":
                last_ver_display = "🟢 Verified active today" if age_days < 1 else f"🟢 Verified active ({int(age_days)}d ago)"
            elif v_status == "CLOSED_CONFIRMED":
                last_ver_display = "🔴 Position closed"
            else:
                last_ver_display = f"🟡 Status observed ({int(age_days)}d ago)"

            scored_suggestions.append(
                SuggestedJobResponse(
                    job_id=opp.id,
                    title=opp.title,
                    company_name=opp.company_name,
                    location=loc_str,
                    is_remote=opp.is_remote,
                    employment_type=opp.employment_type,
                    salary_display=salary_str,
                    application_url=opp.application_url or "",
                    match_score=overall_score,
                    matched_skills=matched_skills[:8],
                    missing_skills=missing_skills[:5],
                    description_snippet=desc_snippet,
                    full_description=opp.description_clean,
                    verification_status=v_status,
                    freshness_state=fresh_state,
                    listing_age_days=age_days,
                    last_verified_display=last_ver_display
                )
            )

        # Sort by match score descending
        scored_suggestions.sort(key=lambda x: x.match_score, reverse=True)
        return scored_suggestions[:limit]

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))



@router.get("/{resume_id}/job-matches/{match_id}", response_model=ResumeJobMatchResponse)
async def get_resume_job_match(
    resume_id: str,
    match_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves a specific past job match evaluation."""
    stmt = select(ResumeJobMatchRecord).where(
        ResumeJobMatchRecord.id == match_id,
        ResumeJobMatchRecord.user_id == current_user.id
    )
    res = await db.execute(stmt)
    r = res.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job match not found.")
    return ResumeJobMatchResponse(
        match_id=r.id,
        resume_id=resume_id,
        version_id=r.resume_version_id,
        target_job_title=r.target_job_title,
        overall_match_score=r.overall_match_score,
        match_band="STRONG" if (r.overall_match_score or 0) >= 80.0 else ("MODERATE" if (r.overall_match_score or 0) >= 60.0 else "NEEDS_IMPROVEMENT"),
        keyword_coverage_score=r.keyword_coverage_score,
        required_skills_match=r.required_skills_match_json,
        preferred_skills_match=r.preferred_skills_match_json,
        experience_level_match=r.experience_level_match_json,
        hard_skills_match=r.required_skills_match_json,
        experience_fit=r.experience_level_match_json,
        project_theme_alignments=r.project_theme_alignments_json,
        unverified_matches=r.unverified_matches_json,
        job_specific_suggestions=r.job_specific_suggestions_json,
        created_at=r.created_at
    )


@router.get("/{resume_id}/diff", response_model=ResumeVersionDiffResponse)
async def compare_resume_versions(
    resume_id: str,
    v1: str = Query(..., description="First version ID (baseline)"),
    v2: str = Query(..., description="Second version ID (comparison)"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Compares two resume versions for textual, skill, and quality differences."""
    stmt = select(ResumeVersionRecord).where(
        ResumeVersionRecord.resume_id == resume_id,
        ResumeVersionRecord.user_id == current_user.id,
        ResumeVersionRecord.id.in_([v1, v2])
    )
    res = await db.execute(stmt)
    versions_map = {ver.id: ver for ver in res.scalars().all()}
    if v1 not in versions_map or v2 not in versions_map:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="One or both versions not found.")

    ver1 = versions_map[v1]
    ver2 = versions_map[v2]

    stmt_e = select(ResumeExtractionRecord).where(
        ResumeExtractionRecord.resume_version_id.in_([v1, v2]),
        ResumeExtractionRecord.user_id == current_user.id
    )
    res_e = await db.execute(stmt_e)
    ext_map = {e.resume_version_id: e for e in res_e.scalars().all()}

    ext1 = ext_map.get(v1)
    ext2 = ext_map.get(v2)

    text1 = ext1.raw_text if ext1 else ""
    text2 = ext2.raw_text if ext2 else ""

    char_diff = len(text2) - len(text1)
    words1 = text1.split()
    words2 = text2.split()
    word_diff = len(words2) - len(words1)

    def collect_skills(ext_record):
        if not ext_record or not ext_record.skills_json:
            return set()
        s_set = set()
        for cat, items in ext_record.skills_json.items():
            if isinstance(items, list):
                for item in items:
                    name = item.get("name") if isinstance(item, dict) else str(item)
                    if name:
                        s_set.add(name.strip())
        return s_set

    s1 = collect_skills(ext1)
    s2 = collect_skills(ext2)
    added = sorted(list(s2 - s1))
    removed = sorted(list(s1 - s2))
    shared = sorted(list(s1 & s2))

    sec1 = set((ext1.sections_json or {}).keys()) if ext1 else set()
    sec2 = set((ext2.sections_json or {}).keys()) if ext2 else set()
    sec_changes = {}
    for s in (sec2 - sec1):
        if not s.startswith("_"):
            sec_changes[s] = "ADDED"
    for s in (sec1 - sec2):
        if not s.startswith("_"):
            sec_changes[s] = "REMOVED"
    for s in (sec1 & sec2):
        if not s.startswith("_"):
            sec_changes[s] = "RETAINED"

    quality_diff = None
    try:
        if ext1 and ext2:
            q1 = resume_quality_analyzer.analyze_quality(
                resume_id, v1, text1, {
                    "personal_info": ext1.personal_info_json,
                    "summary": ext1.summary_json,
                    "education": ext1.education_json,
                    "experience": ext1.experience_json,
                    "skills": ext1.skills_json,
                    "projects": ext1.projects_json,
                    "sections": ext1.sections_json
                }
            )
            q2 = resume_quality_analyzer.analyze_quality(
                resume_id, v2, text2, {
                    "personal_info": ext2.personal_info_json,
                    "summary": ext2.summary_json,
                    "education": ext2.education_json,
                    "experience": ext2.experience_json,
                    "skills": ext2.skills_json,
                    "projects": ext2.projects_json,
                    "sections": ext2.sections_json
                }
            )
            quality_diff = {
                "v1_score": q1.overall_quality_score,
                "v2_score": q2.overall_quality_score,
                "score_delta": round(q2.overall_quality_score - q1.overall_quality_score, 1),
                "v1_band": q1.quality_band,
                "v2_band": q2.quality_band,
            }
    except Exception:
        pass

    return ResumeVersionDiffResponse(
        resume_id=resume_id,
        version_id_1=v1,
        version_id_2=v2,
        version_label_1=ver1.version_label,
        version_label_2=ver2.version_label,
        character_count_diff=char_diff,
        word_count_diff=word_diff,
        added_skills=added,
        removed_skills=removed,
        shared_skills=shared,
        section_changes=sec_changes,
        quality_score_diff=quality_diff
    )


@router.get("/{resume_id}/ai-suggestions", response_model=ResumeAISuggestionsResponse)
async def get_ai_suggestions(
    resume_id: str,
    version_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Generates grounded 'Before vs After' rewrite proposals requiring candidate verification."""
    try:
        ext = await resume_service.get_extraction(db, current_user.id, resume_id, version_id)
        extractions_dict = {
            "personal_info": ext.personal_info,
            "summary": ext.summary,
            "education": ext.education,
            "experience": ext.experience,
            "skills": ext.skills,
            "projects": ext.projects,
        }

        return await resume_ai_service.generate_suggestions(
            resume_id=resume_id,
            version_id=ext.version_id,
            extractions=extractions_dict
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{resume_id}/ai-suggestions/{suggestion_id}/action", response_model=SuggestionActionResponse)
async def handle_ai_suggestion_action(
    resume_id: str,
    suggestion_id: str,
    req: SuggestionActionRequest,
    version_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Applies candidate approval actions (ACCEPT, REJECT, EDIT, REGENERATE).
    Never overwrites original resume content without explicit candidate confirmation.
    """
    try:
        ext = await resume_service.get_extraction(db, current_user.id, resume_id, version_id)
        extractions_dict = {
            "personal_info": ext.personal_info,
            "summary": ext.summary,
            "education": ext.education,
            "experience": ext.experience,
            "skills": ext.skills,
            "projects": ext.projects,
        }

        # Generate current suggestions to locate target suggestion
        sug_resp = await resume_ai_service.generate_suggestions(
            resume_id=resume_id,
            version_id=ext.version_id,
            extractions=extractions_dict
        )
        target_sug = next((s for s in sug_resp.suggestions if s.id == suggestion_id), None)
        if not target_sug:
            # Create a shell suggestion to apply action
            target_sug = AISuggestionDTO(
                id=suggestion_id,
                category="BULLET_REWRITE",
                target_section="EXPERIENCE",
                current_issue="Target suggestion",
                why_it_matters="Candidate review",
                recommended_text=req.edited_text or "Suggested rewrite",
                evidence_required_from_candidate="Proof required"
            )

        success, updated_sug, msg = resume_ai_service.apply_candidate_action(
            target_sug, req.action, req.edited_text
        )
        if not success:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

        # Persist candidate action record
        action_rec = ResumeAISuggestionActionRecord(
            resume_version_id=ext.version_id,
            user_id=current_user.id,
            suggestion_id=suggestion_id,
            action=req.action,
            original_text=target_sug.current_text or target_sug.original_content,
            suggested_text=target_sug.recommended_text or target_sug.suggested_rewrite,
            edited_text=req.edited_text,
            status="APPLIED"
        )
        db.add(action_rec)
        await db.commit()

        return SuggestionActionResponse(
            success=True,
            suggestion=updated_sug,
            message=msg
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{resume_id}/download")
async def download_resume_file(
    resume_id: str,
    version_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Authenticated streaming download of the candidate's original resume file."""
    try:
        if version_id:
            stmt = select(ResumeVersionRecord).where(
                ResumeVersionRecord.id == version_id,
                ResumeVersionRecord.resume_id == resume_id,
                ResumeVersionRecord.user_id == current_user.id
            )
        else:
            stmt_r = select(ResumeRecord).where(ResumeRecord.id == resume_id, ResumeRecord.user_id == current_user.id)
            res_r = await db.execute(stmt_r)
            resume = res_r.scalar_one_or_none()
            if not resume or not resume.active_version_id:
                raise ValueError("Active version not found.")
            stmt = select(ResumeVersionRecord).where(
                ResumeVersionRecord.id == resume.active_version_id,
                ResumeVersionRecord.user_id == current_user.id
            )

        res = await db.execute(stmt)
        ver = res.scalar_one_or_none()
        if not ver:
            raise ValueError("Resume file not found.")

        file_bytes = storage_service.read_resume_file(ver.storage_path, current_user.id)
        return StreamingResponse(
            io.BytesIO(file_bytes),
            media_type=ver.mime_type,
            headers={"Content-Disposition": f'attachment; filename="{ver.original_filename}"'}
        )
    except StorageSecurityError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except (ValueError, FileNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
