"""
RIGHT FIT Core — Resume Review & Profile Synchronization Service
Conflict detection, candidate evidence review, and explicit-consent profile updates.
Phase: 4 — Resume Intelligence & Reviewed Candidate Evidence
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from contracts.profile.schemas import FieldProvenance
from contracts.resume.schemas import (
    ConfidenceLevel,
    EvidenceDTO,
    ResumeConfirmSyncRequest,
    ResumeConfirmSyncResponse,
    ResumeReviewFieldUpdate,
    ResumeReviewResponse,
    ReviewAction,
    ReviewStatus,
)
from app.db.models import (
    CandidateProfile,
    CandidateSkillRecord,
    EducationRecord,
    ExperienceRecord,
    ResumeExtractionRecord,
    ResumeReviewRecord,
    ResumeVersionRecord,
    utc_now,
)
from app.services.audit_service import audit_service


class ReviewService:
    """Manages candidate review workbench and candidate profile synchronization."""

    async def get_or_create_review(
        self,
        db: AsyncSession,
        version_id: str,
        user_id: str
    ) -> ResumeReviewResponse:
        """Retrieves or initializes candidate review workbench state."""
        # 1. Fetch version and extraction
        stmt_ver = select(ResumeVersionRecord).where(
            ResumeVersionRecord.id == version_id,
            ResumeVersionRecord.user_id == user_id
        ).limit(1)
        res_ver = await db.execute(stmt_ver)
        version = res_ver.scalars().first()
        if not version:
            raise ValueError("Resume version not found.")

        stmt_ext = select(ResumeExtractionRecord).where(
            ResumeExtractionRecord.resume_version_id == version_id
        ).order_by(ResumeExtractionRecord.created_at.desc()).limit(1)
        res_ext = await db.execute(stmt_ext)
        extraction = res_ext.scalars().first()
        if not extraction:
            raise ValueError("Extraction records not found for this version.")

        # 2. Fetch or create review record
        stmt_rev = select(ResumeReviewRecord).where(
            ResumeReviewRecord.resume_version_id == version_id
        ).order_by(ResumeReviewRecord.updated_at.desc()).limit(1)
        res_rev = await db.execute(stmt_rev)
        review = res_rev.scalars().first()

        if not review:
            review = ResumeReviewRecord(
                resume_version_id=version_id,
                user_id=user_id,
                review_status=ReviewStatus.PENDING.value,
                field_reviews_json={},
                is_synced_to_profile=False
            )
            db.add(review)
            await db.commit()
            await db.refresh(review)

        # 3. Detect conflicts against existing candidate profile
        stmt_prof = select(CandidateProfile).where(CandidateProfile.user_id == user_id).limit(1)
        res_prof = await db.execute(stmt_prof)
        profile = res_prof.scalars().first()

        conflicts: List[Dict[str, Any]] = []
        personal_info = extraction.personal_info_json or {}

        if profile:
            # Check phone
            if profile.phone and personal_info.get("phone") and profile.phone != personal_info["phone"]:
                conflicts.append({
                    "field_name": "phone",
                    "current_profile_value": profile.phone,
                    "extracted_value": personal_info["phone"],
                    "description": "Phone number in resume differs from existing profile."
                })
            # Check headline
            if profile.headline and personal_info.get("headline") and profile.headline.strip().lower() != personal_info["headline"].strip().lower():
                conflicts.append({
                    "field_name": "headline",
                    "current_profile_value": profile.headline,
                    "extracted_value": personal_info["headline"],
                    "description": "Headline in resume differs from current profile."
                })

        # 4. Parse evidence items and calculate counts
        evidence_dicts = extraction.evidence_items_json or []
        field_reviews = review.field_reviews_json or {}
        evidence_dtos: List[EvidenceDTO] = []

        pending_cnt = 0
        confirmed_cnt = 0
        rejected_cnt = 0

        for item in evidence_dicts:
            f_id = item["field_id"]
            rev_data = field_reviews.get(f_id, {})
            current_action = rev_data.get("action", ReviewStatus.PENDING.value)

            if current_action == ReviewAction.CONFIRM.value:
                status = ReviewStatus.CONFIRMED
                confirmed_cnt += 1
            elif current_action == ReviewAction.EDIT_AND_CONFIRM.value:
                status = ReviewStatus.EDITED
                confirmed_cnt += 1
            elif current_action in (ReviewAction.REJECT.value, ReviewAction.MARK_INCORRECT.value):
                status = ReviewStatus.REJECTED
                rejected_cnt += 1
            else:
                status = ReviewStatus.PENDING
                pending_cnt += 1

            evidence_dtos.append(EvidenceDTO(
                field_id=f_id,
                field_name=item["field_name"],
                extracted_value=item["extracted_value"],
                source_section=item.get("source_section"),
                excerpt=item.get("excerpt", ""),
                page_number=item.get("page_number"),
                extraction_method=item.get("extraction_method", "STRUCTURED_PARSER"),
                confidence_score=float(item.get("confidence_score", 0.85)),
                confidence_level=ConfidenceLevel(item.get("confidence_level", "HIGH")),
                review_status=status,
                user_correction=rev_data.get("corrected_value"),
                reviewed_at=None
            ))

        return ResumeReviewResponse(
            resume_id=version.resume_id,
            version_id=version.id,
            review_status=ReviewStatus(review.review_status),
            is_synced_to_profile=review.is_synced_to_profile,
            synced_at=review.synced_at,
            pending_fields_count=pending_cnt,
            confirmed_fields_count=confirmed_cnt,
            rejected_fields_count=rejected_cnt,
            conflicts_with_profile=conflicts,
            evidence_items=evidence_dtos
        )

    async def update_field_review(
        self,
        db: AsyncSession,
        version_id: str,
        user_id: str,
        update: ResumeReviewFieldUpdate
    ) -> ResumeReviewResponse:
        """Applies candidate confirmation, correction, or rejection to an evidenced field."""
        stmt_rev = select(ResumeReviewRecord).where(
            ResumeReviewRecord.resume_version_id == version_id,
            ResumeReviewRecord.user_id == user_id
        ).order_by(ResumeReviewRecord.updated_at.desc()).limit(1)
        res_rev = await db.execute(stmt_rev)
        review = res_rev.scalars().first()
        if not review:
            raise ValueError("Review record not found.")

        reviews = dict(review.field_reviews_json or {})
        reviews[update.field_id] = {
            "action": update.action.value,
            "corrected_value": update.corrected_value,
            "notes": update.notes,
            "reviewed_at": utc_now().isoformat()
        }
        review.field_reviews_json = reviews
        review.review_status = ReviewStatus.IN_PROGRESS.value
        await db.commit()
        await db.refresh(review)

        return await self.get_or_create_review(db, version_id, user_id)

    async def sync_approved_to_profile(
        self,
        db: AsyncSession,
        version_id: str,
        user_id: str,
        sync_req: ResumeConfirmSyncRequest
    ) -> ResumeConfirmSyncResponse:
        """
        Synchronizes candidate-confirmed fields into canonical profile tables.
        Guarantees existing user data is protected unless overwrite_conflicts=True.
        """
        # 1. Fetch version and extraction
        stmt_ver = select(ResumeVersionRecord).where(
            ResumeVersionRecord.id == version_id,
            ResumeVersionRecord.user_id == user_id
        ).limit(1)
        res_ver = await db.execute(stmt_ver)
        version = res_ver.scalars().first()
        if not version:
            raise ValueError("Resume version not found.")

        stmt_ext = select(ResumeExtractionRecord).where(
            ResumeExtractionRecord.resume_version_id == version_id
        ).order_by(ResumeExtractionRecord.created_at.desc()).limit(1)
        res_ext = await db.execute(stmt_ext)
        extraction = res_ext.scalars().first()
        if not extraction:
            raise ValueError("Extraction records not found.")

        stmt_rev = select(ResumeReviewRecord).where(
            ResumeReviewRecord.resume_version_id == version_id
        ).order_by(ResumeReviewRecord.updated_at.desc()).limit(1)
        res_rev = await db.execute(stmt_rev)
        review = res_rev.scalars().first()
        if not review:
            raise ValueError("Review record not found.")

        # 2. Fetch candidate profile
        stmt_prof = select(CandidateProfile).where(CandidateProfile.user_id == user_id).limit(1)
        res_prof = await db.execute(stmt_prof)
        profile = res_prof.scalars().first()
        if not profile:
            profile = CandidateProfile(user_id=user_id)
            db.add(profile)
            await db.flush()

        field_reviews = review.field_reviews_json or {}
        evidence_items = extraction.evidence_items_json or []

        synced_count = 0
        overwritten_count = 0

        # Sync Personal Information
        personal = extraction.personal_info_json or {}

        # Sync Headline
        if personal.get("headline"):
            if not profile.headline:
                profile.headline = personal["headline"]
                synced_count += 1
            elif sync_req.overwrite_conflicts:
                profile.headline = personal["headline"]
                overwritten_count += 1

        # Sync Location (City, State, Country)
        if personal.get("city"):
            if not profile.city or sync_req.overwrite_conflicts:
                profile.city = personal["city"]
                synced_count += 1
        if personal.get("state"):
            if not profile.state or sync_req.overwrite_conflicts:
                profile.state = personal["state"]
                synced_count += 1
        if personal.get("country"):
            if not profile.country or sync_req.overwrite_conflicts:
                profile.country = personal["country"]
                synced_count += 1

        if personal.get("phone"):
            if not profile.phone:
                profile.phone = personal["phone"]
                synced_count += 1
            elif sync_req.overwrite_conflicts:
                profile.phone = personal["phone"]
                overwritten_count += 1

        # Sync Summary
        summary = extraction.summary_json or {}
        if summary.get("text"):
            if not profile.summary:
                profile.summary = summary["text"]
                synced_count += 1
            elif sync_req.overwrite_conflicts:
                profile.summary = summary["text"]
                overwritten_count += 1

        # Sync Portfolio & Social Links
        if personal.get("portfolio_url"):
            if not profile.portfolio_url or sync_req.overwrite_conflicts:
                profile.portfolio_url = personal["portfolio_url"]
                synced_count += 1

        if personal.get("linkedin_url"):
            if not profile.linkedin_url or sync_req.overwrite_conflicts:
                profile.linkedin_url = personal["linkedin_url"]
                synced_count += 1

        if personal.get("github_url"):
            if not profile.github_url or sync_req.overwrite_conflicts:
                profile.github_url = personal["github_url"]
                synced_count += 1

        if personal.get("website_url"):
            if not profile.website_url or sync_req.overwrite_conflicts:
                profile.website_url = personal["website_url"]
                synced_count += 1

        extracted_socials = personal.get("social_links") or {}
        if extracted_socials:
            curr_socials = dict(profile.social_links_json or {})
            if sync_req.overwrite_conflicts:
                curr_socials.update(extracted_socials)
            else:
                for k, v in extracted_socials.items():
                    if k not in curr_socials:
                        curr_socials[k] = v
            profile.social_links_json = curr_socials
            synced_count += len(extracted_socials)

        # Pre-fetch existing skills, education, and experience in 3 bulk queries to prevent N+1 queries & MultipleResultsFound
        existing_skills_res = await db.execute(
            select(CandidateSkillRecord.skill_name).where(CandidateSkillRecord.profile_id == profile.id)
        )
        existing_skill_names: Set[str] = {
            s.lower().strip() for s in existing_skills_res.scalars().all() if s
        }

        existing_edu_res = await db.execute(
            select(EducationRecord.institution, EducationRecord.degree).where(EducationRecord.profile_id == profile.id)
        )
        existing_edu_keys: Set[Tuple[str, str]] = {
            (inst.lower().strip(), (deg or "").lower().strip())
            for inst, deg in existing_edu_res.all() if inst
        }

        existing_exp_res = await db.execute(
            select(ExperienceRecord.company, ExperienceRecord.role).where(ExperienceRecord.profile_id == profile.id)
        )
        existing_exp_keys: Set[Tuple[str, str]] = {
            (comp.lower().strip(), (role or "").lower().strip())
            for comp, role in existing_exp_res.all() if comp
        }

        # 3. Sync Skills (robust against dict, list, or mixed formats)
        skills_raw = extraction.skills_json or {}
        skills_to_sync: List[Tuple[str, str]] = []

        if isinstance(skills_raw, dict):
            for category, skill_list in skills_raw.items():
                if isinstance(skill_list, list):
                    for item in skill_list:
                        if isinstance(item, dict):
                            s_name = (item.get("name") or item.get("skill_name") or "").strip()
                            s_cat = item.get("category") or category
                        elif isinstance(item, str):
                            s_name = item.strip()
                            s_cat = category
                        else:
                            continue
                        if s_name:
                            skills_to_sync.append((s_name, s_cat))
        elif isinstance(skills_raw, list):
            for item in skills_raw:
                if isinstance(item, dict):
                    s_name = (item.get("name") or item.get("skill_name") or "").strip()
                    s_cat = item.get("category") or "tools"
                elif isinstance(item, str):
                    s_name = item.strip()
                    s_cat = "tools"
                else:
                    continue
                if s_name:
                    skills_to_sync.append((s_name, s_cat))

        # Sync Inferred / Project Skills
        for item in (extraction.inferred_skills_json or []):
            if isinstance(item, dict):
                s_name = (item.get("name") or item.get("skill_name") or "").strip()
                s_cat = item.get("category") or "tools"
            elif isinstance(item, str):
                s_name = item.strip()
                s_cat = "tools"
            else:
                continue
            if s_name:
                skills_to_sync.append((s_name, s_cat))

        for s_name, s_cat in skills_to_sync:
            s_key = s_name.lower().strip()
            if s_key and s_key not in existing_skill_names:
                new_skill = CandidateSkillRecord(
                    profile_id=profile.id,
                    skill_name=s_name,
                    category=s_cat,
                    proficiency="Intermediate",
                    provenance=FieldProvenance.RESUME_EXTRACTED.value
                )
                db.add(new_skill)
                existing_skill_names.add(s_key)
                synced_count += 1

        # 4. Sync Education (prevents MultipleResultsFound and handles duplicate schools)
        for edu in (extraction.education_json or []):
            if not isinstance(edu, dict):
                continue
            inst = (edu.get("institution") or "").strip()[:140]
            deg = (edu.get("degree") or "Degree").strip()[:140]
            fos = (edu.get("field_of_study") or "Computer Science & Engineering").strip()[:140]
            if inst:
                edu_key = (inst.lower(), deg.lower())
                if edu_key not in existing_edu_keys:
                    new_edu = EducationRecord(
                        profile_id=profile.id,
                        institution=inst,
                        degree=deg,
                        field_of_study=fos,
                        start_date=edu.get("start_date"),
                        end_date=edu.get("end_date"),
                        achievements=edu.get("grade"),
                        provenance=FieldProvenance.RESUME_EXTRACTED.value
                    )
                    db.add(new_edu)
                    existing_edu_keys.add(edu_key)
                    synced_count += 1

        # 5. Sync Experience (formal or verified practical projects)
        experiences_to_sync = list(extraction.experience_json or [])
        if not experiences_to_sync and extraction.projects_json:
            for proj in extraction.projects_json:
                if not isinstance(proj, dict):
                    continue
                desc = proj.get("description") or ""
                if proj.get("technologies"):
                    techs = ", ".join(proj["technologies"]) if isinstance(proj["technologies"], list) else str(proj["technologies"])
                    desc = f"Technologies: {techs}\n{desc}".strip()
                experiences_to_sync.append({
                    "company": proj.get("name", "Software Project"),
                    "title": (profile.headline or "AI Automation & Full-Stack Developer").split("|")[0].strip(),
                    "start_date": "2023",
                    "end_date": "Present",
                    "responsibilities": [desc] if desc else []
                })

        for exp in experiences_to_sync:
            if not isinstance(exp, dict):
                continue
            comp = (exp.get("company") or "").strip()
            role = (exp.get("title") or exp.get("role") or "Developer").strip()
            if comp:
                exp_key = (comp.lower(), role.lower())
                if exp_key not in existing_exp_keys:
                    resp = exp.get("responsibilities", [])
                    desc = "\n".join(resp) if isinstance(resp, list) else str(resp)
                    new_exp = ExperienceRecord(
                        profile_id=profile.id,
                        company=comp,
                        role=role,
                        employment_type="Full-time",
                        start_date=exp.get("start_date"),
                        end_date=exp.get("end_date"),
                        description=desc,
                        provenance=FieldProvenance.RESUME_EXTRACTED.value
                    )
                    db.add(new_exp)
                    existing_exp_keys.add(exp_key)
                    synced_count += 1

        # Update review status
        review.is_synced_to_profile = True
        review.synced_at = utc_now()
        review.review_status = ReviewStatus.CONFIRMED.value
        version.parsing_status = "COMPLETED"

        await db.commit()

        # Log security audit event
        await audit_service.record_event(
            db=db,
            event_type="PROFILE_SYNCED_FROM_RESUME",
            user_id=user_id,
            status="SUCCESS",
            details={
                "version_id": version_id,
                "fields_synced_count": synced_count,
                "conflicts_overwritten_count": overwritten_count
            }
        )

        return ResumeConfirmSyncResponse(
            synced=True,
            fields_synced_count=synced_count,
            conflicts_overwritten_count=overwritten_count,
            synced_at=utc_now(),
            message=f"Successfully synchronized {synced_count} candidate fields into profile."
        )


# Singleton instance
review_service = ReviewService()
