"""
RIGHT FIT Core — Resume Service
Lifecycle management, multi-version orchestration, and parsing execution.
Phase: 4 — Resume Intelligence & Reviewed Candidate Evidence
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from contracts.resume.schemas import (
    ConfidenceLevel,
    EvidenceDTO,
    ParsingStatus,
    ResumeExtractionResponse,
    ResumeSummaryResponse,
    ResumeUploadResponse,
    ResumeVersionResponse,
    ReviewStatus,
)
from app.db.models import (
    ResumeExtractionRecord,
    ResumeRecord,
    ResumeReviewRecord,
    ResumeVersionRecord,
    utc_now,
)
from app.services.audit_service import audit_service
from app.services.resume_parser_service import ParsingError, resume_parser_service
from app.services.storage_service import storage_service


class ResumeService:
    """Orchestrates candidate resumes, versions, parsing execution, and cleanup."""

    async def upload_initial_resume(
        self,
        db: AsyncSession,
        user_id: str,
        title: str,
        file_bytes: bytes,
        filename: str
    ) -> ResumeUploadResponse:
        """Uploads a new candidate resume and creates version 1."""
        clean_filename = storage_service.sanitize_filename(filename)

        # 1. Create resume container
        resume = ResumeRecord(
            user_id=user_id,
            title=title.strip() or "My Resume"
        )
        db.add(resume)
        await db.flush()

        # 2. Create version 1 record
        version = ResumeVersionRecord(
            resume_id=resume.id,
            user_id=user_id,
            version_number=1,
            version_label="v1 - Initial",
            original_filename=clean_filename,
            file_type="pdf",  # placeholder, updated below
            mime_type="application/pdf",
            file_size_bytes=len(file_bytes),
            storage_path="",
            file_hash_sha256="",
            parsing_status=ParsingStatus.UPLOADED.value,
            is_active=True
        )
        db.add(version)
        await db.flush()

        # 3. Save file to private storage
        storage_path, file_type, mime_type, file_size, file_hash = storage_service.save_resume_file(
            user_id=user_id,
            version_id=version.id,
            file_bytes=file_bytes,
            original_filename=clean_filename
        )

        version.storage_path = storage_path
        version.file_type = file_type
        version.mime_type = mime_type
        version.file_size_bytes = file_size
        version.file_hash_sha256 = file_hash

        resume.active_version_id = version.id
        await db.commit()
        await db.refresh(version)

        # 4. Audit log
        await audit_service.record_event(
            db=db,
            event_type="RESUME_UPLOADED",
            user_id=user_id,
            status="SUCCESS",
            details={
                "resume_id": resume.id,
                "version_id": version.id,
                "filename": clean_filename,
                "file_size": file_size
            }
        )

        return ResumeUploadResponse(
            resume_id=resume.id,
            version_id=version.id,
            version_number=version.version_number,
            version_label=version.version_label,
            filename=clean_filename,
            file_type=file_type,
            file_size_bytes=file_size,
            parsing_status=ParsingStatus(version.parsing_status),
            uploaded_at=version.uploaded_at
        )

    async def upload_new_version(
        self,
        db: AsyncSession,
        user_id: str,
        resume_id: str,
        file_bytes: bytes,
        filename: str,
        version_label: Optional[str] = None
    ) -> ResumeUploadResponse:
        """Uploads an additional version to an existing candidate resume."""
        # Validate resume ownership
        stmt = select(ResumeRecord).where(
            ResumeRecord.id == resume_id,
            ResumeRecord.user_id == user_id
        )
        res = await db.execute(stmt)
        resume = res.scalar_one_or_none()
        if not resume:
            raise ValueError("Resume not found or access denied.")

        # Determine next version number
        stmt_max = select(func.max(ResumeVersionRecord.version_number)).where(
            ResumeVersionRecord.resume_id == resume_id
        )
        res_max = await db.execute(stmt_max)
        current_max = res_max.scalar() or 0
        next_ver_num = current_max + 1

        clean_filename = storage_service.sanitize_filename(filename)
        label = version_label.strip() if version_label else f"v{next_ver_num}"

        version = ResumeVersionRecord(
            resume_id=resume.id,
            user_id=user_id,
            version_number=next_ver_num,
            version_label=label,
            original_filename=clean_filename,
            file_type="pdf",
            mime_type="application/pdf",
            file_size_bytes=len(file_bytes),
            storage_path="",
            file_hash_sha256="",
            parsing_status=ParsingStatus.UPLOADED.value,
            is_active=False
        )
        db.add(version)
        await db.flush()

        storage_path, file_type, mime_type, file_size, file_hash = storage_service.save_resume_file(
            user_id=user_id,
            version_id=version.id,
            file_bytes=file_bytes,
            original_filename=clean_filename
        )

        version.storage_path = storage_path
        version.file_type = file_type
        version.mime_type = mime_type
        version.file_size_bytes = file_size
        version.file_hash_sha256 = file_hash

        await db.commit()
        await db.refresh(version)

        return ResumeUploadResponse(
            resume_id=resume.id,
            version_id=version.id,
            version_number=version.version_number,
            version_label=version.version_label,
            filename=clean_filename,
            file_type=file_type,
            file_size_bytes=file_size,
            parsing_status=ParsingStatus(version.parsing_status),
            uploaded_at=version.uploaded_at
        )

    async def list_resumes(self, db: AsyncSession, user_id: str) -> List[ResumeSummaryResponse]:
        """Lists all resumes for a candidate with their active version details."""
        stmt = (
            select(ResumeRecord)
            .where(ResumeRecord.user_id == user_id)
            .options(selectinload(ResumeRecord.versions))
            .order_by(ResumeRecord.updated_at.desc())
        )
        res = await db.execute(stmt)
        resumes = res.scalars().all()

        summaries: List[ResumeSummaryResponse] = []
        for r in resumes:
            active_ver: Optional[ResumeVersionResponse] = None
            for v in r.versions:
                if v.id == r.active_version_id or v.is_active:
                    active_ver = ResumeVersionResponse(
                        id=v.id,
                        resume_id=v.resume_id,
                        version_number=v.version_number,
                        version_label=v.version_label,
                        original_filename=v.original_filename,
                        file_type=v.file_type,
                        file_size_bytes=v.file_size_bytes,
                        parsing_status=ParsingStatus(v.parsing_status),
                        error_message=v.error_message,
                        is_active=v.is_active,
                        uploaded_at=v.uploaded_at,
                        parsed_at=v.parsed_at
                    )
                    break

            summaries.append(ResumeSummaryResponse(
                id=r.id,
                title=r.title,
                active_version_id=r.active_version_id,
                active_version=active_ver,
                version_count=len(r.versions),
                created_at=r.created_at,
                updated_at=r.updated_at
            ))

        return summaries

    async def get_resume_summary(self, db: AsyncSession, user_id: str, resume_id: str) -> ResumeSummaryResponse:
        """Fetches a single resume summary."""
        stmt = (
            select(ResumeRecord)
            .where(ResumeRecord.id == resume_id, ResumeRecord.user_id == user_id)
            .options(selectinload(ResumeRecord.versions))
        )
        res = await db.execute(stmt)
        resume = res.scalar_one_or_none()
        if not resume:
            raise ValueError("Resume not found or access denied.")

        active_ver = None
        for v in resume.versions:
            if v.id == resume.active_version_id or v.is_active:
                active_ver = ResumeVersionResponse(
                    id=v.id,
                    resume_id=v.resume_id,
                    version_number=v.version_number,
                    version_label=v.version_label,
                    original_filename=v.original_filename,
                    file_type=v.file_type,
                    file_size_bytes=v.file_size_bytes,
                    parsing_status=ParsingStatus(v.parsing_status),
                    error_message=v.error_message,
                    is_active=v.is_active,
                    uploaded_at=v.uploaded_at,
                    parsed_at=v.parsed_at
                )
                break

        return ResumeSummaryResponse(
            id=resume.id,
            title=resume.title,
            active_version_id=resume.active_version_id,
            active_version=active_ver,
            version_count=len(resume.versions),
            created_at=resume.created_at,
            updated_at=resume.updated_at
        )

    async def list_versions(self, db: AsyncSession, user_id: str, resume_id: str) -> List[ResumeVersionResponse]:
        """Lists all versions of a candidate's resume."""
        # Check ownership
        stmt_r = select(ResumeRecord).where(ResumeRecord.id == resume_id, ResumeRecord.user_id == user_id)
        res_r = await db.execute(stmt_r)
        if not res_r.scalar_one_or_none():
            raise ValueError("Resume not found or access denied.")

        stmt = (
            select(ResumeVersionRecord)
            .where(ResumeVersionRecord.resume_id == resume_id, ResumeVersionRecord.user_id == user_id)
            .order_by(ResumeVersionRecord.version_number.desc())
        )
        res = await db.execute(stmt)
        versions = res.scalars().all()

        return [
            ResumeVersionResponse(
                id=v.id,
                resume_id=v.resume_id,
                version_number=v.version_number,
                version_label=v.version_label,
                original_filename=v.original_filename,
                file_type=v.file_type,
                file_size_bytes=v.file_size_bytes,
                parsing_status=ParsingStatus(v.parsing_status),
                error_message=v.error_message,
                is_active=v.is_active,
                uploaded_at=v.uploaded_at,
                parsed_at=v.parsed_at
            )
            for v in versions
        ]

    async def set_active_version(
        self,
        db: AsyncSession,
        user_id: str,
        resume_id: str,
        version_id: str
    ) -> ResumeSummaryResponse:
        """Designates an uploaded version as the active resume."""
        stmt = (
            select(ResumeRecord)
            .where(ResumeRecord.id == resume_id, ResumeRecord.user_id == user_id)
            .options(selectinload(ResumeRecord.versions))
        )
        res = await db.execute(stmt)
        resume = res.scalar_one_or_none()
        if not resume:
            raise ValueError("Resume not found.")

        matched_ver = None
        for v in resume.versions:
            if v.id == version_id:
                v.is_active = True
                matched_ver = v
            else:
                v.is_active = False

        if not matched_ver:
            raise ValueError("Version not found in this resume.")

        resume.active_version_id = version_id
        await db.commit()
        return await self.get_resume_summary(db, user_id, resume_id)

    async def execute_parse_pipeline(
        self,
        db: AsyncSession,
        user_id: str,
        resume_id: str,
        version_id: Optional[str] = None
    ) -> ResumeExtractionResponse:
        """
        Executes document text extraction, section detection, and evidenced entity parsing.
        """
        # 1. Resolve version
        if version_id:
            stmt = select(ResumeVersionRecord).where(
                ResumeVersionRecord.id == version_id,
                ResumeVersionRecord.resume_id == resume_id,
                ResumeVersionRecord.user_id == user_id
            )
        else:
            stmt_r = select(ResumeRecord).where(
                ResumeRecord.id == resume_id,
                ResumeRecord.user_id == user_id
            )
            res_r = await db.execute(stmt_r)
            resume = res_r.scalar_one_or_none()
            if not resume or not resume.active_version_id:
                raise ValueError("Active resume version not found.")
            stmt = select(ResumeVersionRecord).where(
                ResumeVersionRecord.id == resume.active_version_id,
                ResumeVersionRecord.user_id == user_id
            )

        res = await db.execute(stmt)
        version = res.scalar_one_or_none()
        if not version:
            raise ValueError("Resume version not found.")

        # Update status to processing
        version.parsing_status = ParsingStatus.PROCESSING.value
        version.error_message = None
        await db.commit()

        try:
            # 2. Read private file
            file_bytes = storage_service.read_resume_file(version.storage_path, user_id)

            # 3. Parse document
            raw_text, extractions, evidence_list = resume_parser_service.parse_document(
                file_bytes=file_bytes,
                file_type=version.file_type
            )

            # 4. Save or update extraction record
            stmt_ext = select(ResumeExtractionRecord).where(
                ResumeExtractionRecord.resume_version_id == version.id
            )
            res_ext = await db.execute(stmt_ext)
            ext_record = res_ext.scalar_one_or_none()

            evidence_dicts = [ev.model_dump() for ev in evidence_list]

            enriched_sections = dict(extractions["sections"])
            enriched_sections["_internships"] = extractions.get("internships", [])
            enriched_sections["_inferred_skills"] = extractions.get("inferred_skills", [])
            enriched_sections["_explicit_skills"] = extractions.get("explicit_skills", extractions.get("skills", {}))
            enriched_sections["domain_info"] = extractions.get("domain_info", {})
            enriched_sections["_domain_info"] = extractions.get("domain_info", {})
            enriched_sections["_publications"] = extractions.get("publications", [])
            enriched_sections["_languages"] = extractions.get("languages", [])
            enriched_sections["_awards"] = extractions.get("awards", [])
            enriched_sections["_is_scanned_pdf"] = extractions.get("is_scanned_pdf", False)
            enriched_sections["_is_mixed_content"] = extractions.get("is_mixed_content", False)
            enriched_sections["_ocr_required"] = extractions.get("ocr_required", False)
            enriched_sections["_low_text_pages"] = extractions.get("low_text_pages", [])
            enriched_sections["_extraction_notes"] = extractions.get("extraction_notes", [])

            if not ext_record:
                ext_record = ResumeExtractionRecord(
                    resume_version_id=version.id,
                    user_id=user_id,
                    raw_text=raw_text,
                    summary_json=extractions["summary"],
                    sections_json=enriched_sections,
                    personal_info_json=extractions["personal_info"],
                    education_json=extractions["education"],
                    experience_json=extractions["experience"],
                    skills_json=extractions["skills"],
                    projects_json=extractions["projects"],
                    certifications_json=extractions["certifications"],
                    evidence_items_json=evidence_dicts
                )
                db.add(ext_record)
            else:
                ext_record.raw_text = raw_text
                ext_record.summary_json = extractions["summary"]
                ext_record.sections_json = enriched_sections
                ext_record.personal_info_json = extractions["personal_info"]
                ext_record.education_json = extractions["education"]
                ext_record.experience_json = extractions["experience"]
                ext_record.skills_json = extractions["skills"]
                ext_record.projects_json = extractions["projects"]
                ext_record.certifications_json = extractions["certifications"]
                ext_record.evidence_items_json = evidence_dicts

            version.parsing_status = ParsingStatus.REVIEW_REQUIRED.value
            version.parsed_at = utc_now()
            await db.commit()

            # Automatically sync extracted candidate facts (skills, portfolio & social links, contact, experience, education) to CandidateProfile
            try:
                from app.services.review_service import review_service
                from contracts.resume.schemas import ResumeConfirmSyncRequest
                await review_service.get_or_create_review(db, version.id, user_id)
                await review_service.sync_approved_to_profile(
                    db=db,
                    version_id=version.id,
                    user_id=user_id,
                    sync_req=ResumeConfirmSyncRequest(overwrite_conflicts=False)
                )
            except Exception as sync_exc:
                # Non-fatal so parsing result is still returned cleanly
                print(f"[AutoSync Warning] Resume auto-sync to profile encountered notice: {sync_exc}")

            return ResumeExtractionResponse(
                resume_id=resume_id,
                version_id=version.id,
                parsing_status=ParsingStatus.REVIEW_REQUIRED,
                personal_info=extractions["personal_info"],
                summary=extractions["summary"],
                education=extractions["education"],
                experience=extractions["experience"],
                internships=extractions.get("internships", []),
                skills=extractions["skills"],
                explicit_skills=extractions.get("explicit_skills", extractions["skills"]),
                inferred_skills=extractions.get("inferred_skills", []),
                projects=extractions["projects"],
                certifications=extractions["certifications"],
                publications=extractions.get("publications", []),
                languages=extractions.get("languages", []),
                awards=extractions.get("awards", []),
                is_scanned_pdf=extractions.get("is_scanned_pdf", False),
                is_mixed_content=extractions.get("is_mixed_content", False),
                ocr_required=extractions.get("ocr_required", False),
                low_text_pages=extractions.get("low_text_pages", []),
                extraction_notes=extractions.get("extraction_notes", []),
                evidence_items=evidence_list,
                parsed_at=version.parsed_at
            )

        except ParsingError as e:
            version.parsing_status = ParsingStatus.FAILED.value
            version.error_message = str(e)
            await db.commit()
            raise ValueError(f"Parsing failed: {str(e)}")

        except Exception as e:
            version.parsing_status = ParsingStatus.FAILED.value
            version.error_message = f"Internal parsing failure: {str(e)}"
            await db.commit()
            raise ValueError(f"Document parsing error: {str(e)}")

    async def get_extraction(
        self,
        db: AsyncSession,
        user_id: str,
        resume_id: str,
        version_id: Optional[str] = None
    ) -> ResumeExtractionResponse:
        """Retrieves structured extractions and evidence for a resume version."""
        # 1. Resolve version
        if version_id:
            stmt_v = select(ResumeVersionRecord).where(
                ResumeVersionRecord.id == version_id,
                ResumeVersionRecord.resume_id == resume_id,
                ResumeVersionRecord.user_id == user_id
            )
        else:
            stmt_r = select(ResumeRecord).where(ResumeRecord.id == resume_id, ResumeRecord.user_id == user_id)
            res_r = await db.execute(stmt_r)
            resume = res_r.scalar_one_or_none()
            if not resume or not resume.active_version_id:
                raise ValueError("Active resume version not found.")
            stmt_v = select(ResumeVersionRecord).where(
                ResumeVersionRecord.id == resume.active_version_id,
                ResumeVersionRecord.user_id == user_id
            )

        res_v = await db.execute(stmt_v)
        version = res_v.scalar_one_or_none()
        if not version:
            raise ValueError("Resume version not found.")

        stmt_ext = select(ResumeExtractionRecord).where(
            ResumeExtractionRecord.resume_version_id == version.id
        )
        res_ext = await db.execute(stmt_ext)
        ext = res_ext.scalar_one_or_none()
        if not ext:
            raise ValueError("No extraction records found. Please parse the resume first.")

        evidence_items = [
            EvidenceDTO(
                field_id=item["field_id"],
                field_name=item["field_name"],
                extracted_value=item["extracted_value"],
                source_section=item.get("source_section"),
                excerpt=item.get("excerpt", ""),
                page_number=item.get("page_number"),
                extraction_method=item.get("extraction_method", "STRUCTURED_PARSER"),
                confidence_score=float(item.get("confidence_score", 0.85)),
                confidence_level=ConfidenceLevel(item.get("confidence_level", "HIGH")),
                review_status=ReviewStatus(item.get("review_status", "PENDING")),
                user_correction=item.get("user_correction"),
                reviewed_at=None
            )
            for item in (ext.evidence_items_json or [])
        ]

        # Unpack supplementary sections stored in sections_json if present
        sections = ext.sections_json or {}
        internships = sections.get("_internships", [])
        inferred_skills = sections.get("_inferred_skills", [])
        explicit_skills = sections.get("_explicit_skills", ext.skills_json or {})
        publications = sections.get("_publications", [])
        languages = sections.get("_languages", [])
        awards = sections.get("_awards", [])
        is_scanned_pdf = bool(sections.get("_is_scanned_pdf", False))
        is_mixed_content = bool(sections.get("_is_mixed_content", False))
        ocr_required = bool(sections.get("_ocr_required", False))
        low_text_pages = sections.get("_low_text_pages", [])
        extraction_notes = sections.get("_extraction_notes", [])

        return ResumeExtractionResponse(
            resume_id=resume_id,
            version_id=version.id,
            parsing_status=ParsingStatus(version.parsing_status),
            personal_info=ext.personal_info_json,
            summary=ext.summary_json,
            education=ext.education_json or [],
            experience=ext.experience_json or [],
            internships=internships,
            skills=ext.skills_json or {},
            explicit_skills=explicit_skills,
            inferred_skills=inferred_skills,
            projects=ext.projects_json or [],
            certifications=ext.certifications_json or [],
            publications=publications,
            languages=languages,
            awards=awards,
            is_scanned_pdf=is_scanned_pdf,
            is_mixed_content=is_mixed_content,
            ocr_required=ocr_required,
            low_text_pages=low_text_pages,
            extraction_notes=extraction_notes,
            evidence_items=evidence_items,
            parsed_at=version.parsed_at
        )

    async def delete_resume(self, db: AsyncSession, user_id: str, resume_id: str) -> bool:
        """Permanently deletes resume, versions, extractions, and stored disk files."""
        stmt = (
            select(ResumeRecord)
            .where(ResumeRecord.id == resume_id, ResumeRecord.user_id == user_id)
            .options(selectinload(ResumeRecord.versions))
        )
        res = await db.execute(stmt)
        resume = res.scalar_one_or_none()
        if not resume:
            raise ValueError("Resume not found or access denied.")

        # 1. Delete private disk files
        for v in resume.versions:
            if v.storage_path:
                storage_service.delete_resume_file(v.storage_path, user_id)

        # 2. Database cascade delete
        await db.delete(resume)
        await db.commit()

        # 3. Log audit event
        await audit_service.record_event(
            db=db,
            event_type="RESUME_DELETED",
            user_id=user_id,
            status="SUCCESS",
            details={"resume_id": resume_id}
        )
        return True


# Singleton instance
resume_service = ResumeService()
