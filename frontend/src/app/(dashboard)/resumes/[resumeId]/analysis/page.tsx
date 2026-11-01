"use client";

import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { apiClient } from "../../../../../services/apiClient";
import { ResumeSubNav } from "../../../../../features/resume/ResumeSubNav";

export default function ResumeAnalysisPage() {
  const params = useParams();
  const resumeId = params?.resumeId as string;

  const [extraction, setExtraction] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showEvidence, setShowEvidence] = useState(true);
  const [suggestedJobs, setSuggestedJobs] = useState<any[]>([]);
  const [loadingJobs, setLoadingJobs] = useState(false);
  const [syncingProfile, setSyncingProfile] = useState(false);
  const [syncSuccessMsg, setSyncSuccessMsg] = useState<string | null>(null);

  const handleSyncToProfile = async () => {
    try {
      setSyncingProfile(true);
      setSyncSuccessMsg(null);
      const res: any = await apiClient.post(`/api/v1/resumes/${resumeId}/sync-profile`);
      if (res.success || res.data) {
        setSyncSuccessMsg(
          res.data?.message ||
            "✓ Successfully synced skills, portfolio links, social handles, experience, and education to your Candidate Profile!"
        );
        setTimeout(() => setSyncSuccessMsg(null), 8000);
      }
    } catch (err: any) {
      alert("Failed to sync to profile: " + (err.message || "Unknown error"));
    } finally {
      setSyncingProfile(false);
    }
  };

  useEffect(() => {
    const fetchSuggestedJobs = async () => {
      try {
        setLoadingJobs(true);
        const res: any = await apiClient.get(`/resumes/${resumeId}/suggested-jobs?limit=3`);
        if (res?.data) {
          setSuggestedJobs(res.data);
        }
      } catch (err) {
        console.error("Failed to load suggested jobs for resume:", err);
      } finally {
        setLoadingJobs(false);
      }
    };
    if (resumeId) {
      fetchSuggestedJobs();
    }
  }, [resumeId]);

  useEffect(() => {
    const fetchExtraction = async () => {
      try {
        setLoading(true);
        setError(null);
        const res = await apiClient.get<any>(`/api/v1/resumes/${resumeId}/extraction`);
        if (res.success && res.data) {
          setExtraction(res.data);
        }
      } catch (err: any) {
        setError(err.message || "Failed to load extraction details. Make sure the resume has been parsed.");
      } finally {
        setLoading(false);
      }
    };

    if (resumeId) {
      fetchExtraction();
    }
  }, [resumeId]);

  const getConfidenceBadge = (level: string) => {
    switch (level) {
      case "HIGH":
        return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">High Confidence</span>;
      case "MEDIUM":
        return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-amber-100 text-amber-800 border border-amber-300">Medium Confidence</span>;
      case "LOW":
        return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-rose-100 text-rose-800 border border-rose-300">Low Confidence</span>;
      default:
        return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-slate-200 text-slate-800 border border-slate-300">Evidence Unavailable</span>;
    }
  };

  const getEvidenceForField = (fieldNamePrefix: string) => {
    if (!extraction?.evidence_items) return null;
    return extraction.evidence_items.find((ev: any) => ev.field_name?.startsWith(fieldNamePrefix));
  };

  // Extract skills fallback
  const skillsMap = extraction?.skills || extraction?.explicit_skills || {};
  const inferredList: any[] = extraction?.inferred_skills || [];

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 sm:px-6 lg:px-8 space-y-6 animate-fade-in">
      {/* Navigation & Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-6 border-b border-slate-300/80 gap-4">
        <div>
          <Link href="/resumes" className="text-xs font-bold text-indigo-700 hover:text-indigo-900 flex items-center gap-1 mb-1 transition-colors">
            ← Back to Resumes
          </Link>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
            Resume Profile &amp; Extracted Skills
          </h1>
          <p className="mt-1 text-sm text-slate-600 font-semibold">
            Parsed professional background, verified skills, and calibrated career opportunities.
          </p>
        </div>

        <div className="flex items-center space-x-3 flex-wrap gap-2">
          <button
            type="button"
            disabled={syncingProfile}
            onClick={handleSyncToProfile}
            className="px-4 py-2.5 rounded-xl neo-pill text-xs font-black text-emerald-800 hover:text-emerald-900 border border-emerald-300 shadow-sm flex items-center gap-1.5 transition-all disabled:opacity-50"
          >
            <span>{syncingProfile ? "⏳" : "🔄"}</span>
            <span>{syncingProfile ? "Syncing..." : "Auto-Sync to My Profile"}</span>
          </button>
          <Link
            href={`/resumes/${resumeId}/ats`}
            className="neo-btn-primary px-4 py-2.5 rounded-xl text-xs font-bold transition-all shadow-md flex items-center gap-1.5 shrink-0"
          >
            <span>🎯</span>
            <span>ATS Optimizer &amp; Matcher →</span>
          </Link>
        </div>
      </div>

      <ResumeSubNav resumeId={resumeId} />

      {/* Sync Success Banner */}
      {syncSuccessMsg && (
        <div className="p-4 rounded-2xl bg-emerald-100 border border-emerald-300 text-emerald-950 text-xs font-bold flex items-center justify-between shadow-sm animate-fade-in">
          <div className="flex items-center gap-2">
            <span>✨</span>
            <span>{syncSuccessMsg}</span>
          </div>
          <Link
            href="/profile"
            className="px-3 py-1 rounded-xl bg-emerald-600 text-white hover:bg-emerald-700 text-xs font-black transition-all shrink-0 shadow-sm"
          >
            View Candidate Profile →
          </Link>
        </div>
      )}

      {/* Scanned PDF Warning Banner */}
      {extraction?.is_scanned_pdf && (
        <div className="p-4 rounded-2xl neo-inset border border-amber-300/80 text-amber-950 text-xs leading-relaxed flex items-start space-x-3">
          <span className="text-base font-bold">⚠️</span>
          <div>
            <p className="font-extrabold text-amber-950">Scanned Document or Low Embedded Text Detected</p>
            <p className="mt-0.5 text-amber-900 font-semibold">
              This document contains very few parseable character glyphs and may be an image scan or flattened PDF.
              Please verify your extracted details below or upload a clean, text-searchable PDF.
            </p>
          </div>
        </div>
      )}

      {/* Extraction Warnings/Notes */}
      {extraction?.extraction_notes && extraction.extraction_notes.length > 0 && (
        <div className="p-4 rounded-2xl neo-card border border-white/90 text-xs text-slate-700 font-semibold">
          <p className="font-black text-slate-900 mb-1">Extraction Notes:</p>
          <ul className="list-disc list-inside space-y-1">
            {extraction.extraction_notes.map((note: string, idx: number) => (
              <li key={idx}>{note}</li>
            ))}
          </ul>
        </div>
      )}

      {error && (
        <div className="p-4 rounded-2xl neo-inset border border-rose-300 text-rose-950 text-sm font-bold">
          {error}
          <div className="mt-3">
            <button
              onClick={async () => {
                setLoading(true);
                try {
                  await apiClient.post(`/api/v1/resumes/${resumeId}/parse`);
                  window.location.reload();
                } catch (e: any) {
                  setError(e.message);
                  setLoading(false);
                }
              }}
              className="neo-btn-primary px-4 py-2 rounded-xl text-xs font-bold"
            >
              Parse Resume Now →
            </button>
          </div>
        </div>
      )}

      {loading ? (
        <div className="py-20 text-center text-slate-700 font-bold">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto mb-3"></div>
          Loading document extractions...
        </div>
      ) : extraction ? (
        <div className="space-y-6">
          {/* Detected Domain & Career Archetypes Banner */}
          {(extraction.domain_info || extraction.sections?.domain_info) && (() => {
            const dom = extraction.domain_info || extraction.sections?.domain_info;
            return (
              <section className="p-6 rounded-2xl neo-box neo-box-hover border border-white/90 text-slate-900 space-y-3">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-2xl">{dom.icon || "🎯"}</span>
                      <h2 className="text-lg sm:text-xl font-black text-slate-900">
                        Detected Domain: {dom.display_name}
                      </h2>
                      <span className="text-xs font-extrabold px-3 py-0.5 rounded-full bg-indigo-100 border border-indigo-300 text-indigo-900">
                        {Math.round((dom.confidence_score || 0.9) * 100)}% Confidence
                      </span>
                    </div>
                    <p className="text-xs text-slate-700 font-semibold">
                      Opportunities, freelance contracts, and startup bottlenecks across RightFit are automatically tailored to this discipline.
                    </p>
                    {dom.target_archetypes && dom.target_archetypes.length > 0 && (
                      <div className="flex flex-wrap items-center gap-1.5 pt-1">
                        <span className="text-xs text-slate-600 font-bold">Target Archetypes:</span>
                        {dom.target_archetypes.map((arch: string) => (
                          <span
                            key={arch}
                            className="neo-pill text-xs px-3 py-1 rounded-xl text-indigo-900 font-bold border border-white/90"
                          >
                            {arch}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  <div>
                    <Link
                      href="/opportunities"
                      className="neo-btn-primary inline-flex items-center px-4 py-2.5 rounded-xl text-xs font-bold transition-all shadow-md shrink-0 whitespace-nowrap"
                    >
                      View Recommended Opportunities →
                    </Link>
                  </div>
                </div>
              </section>
            );
          })()}

          {/* Calibrated Real Opportunities for this Resume */}
          {suggestedJobs.length > 0 && (
            <section className="neo-box p-6 rounded-2xl border border-white/90 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-300/80">
                <div>
                  <h2 className="text-base font-black text-slate-900 flex items-center gap-2">
                    <span>🎯</span> Top Opportunities Calibrated for this Resume
                  </h2>
                  <p className="text-xs text-slate-600 font-semibold mt-0.5">
                    Live career opportunities scored against your verified resume skills and target domain.
                  </p>
                </div>
                <Link
                  href="/opportunities"
                  className="text-xs font-bold text-indigo-700 hover:text-indigo-900 flex items-center gap-1 shrink-0 transition-colors"
                >
                  Explore Live Opportunities →
                </Link>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {suggestedJobs.map((job) => (
                  <div
                    key={job.job_id}
                    className="p-5 rounded-2xl neo-card neo-box-hover flex flex-col justify-between space-y-3 transition-all"
                  >
                    <div className="space-y-2">
                      <div className="flex items-center justify-between gap-1">
                        <span className="text-[10px] font-black uppercase tracking-wider px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300 font-mono">
                          {Math.round(job.match_score)}% Match
                        </span>
                        <span className="text-[11px] text-slate-600 font-bold truncate max-w-[120px]">
                          {job.company_name}
                        </span>
                      </div>

                      <h3 className="text-sm font-bold text-slate-900 line-clamp-1 hover:text-indigo-700">
                        {job.title}
                      </h3>

                      <p className="text-xs text-slate-700 font-medium line-clamp-2 leading-relaxed">
                        {job.description_snippet}
                      </p>

                      {job.matched_skills && job.matched_skills.length > 0 && (
                        <div className="flex flex-wrap items-center gap-1 pt-1">
                          <span className="text-[10px] text-emerald-800 font-bold">Matched:</span>
                          {job.matched_skills.slice(0, 2).map((s: string) => (
                            <span
                              key={s}
                              className="text-[10px] px-2 py-0.5 rounded-lg bg-emerald-100 border border-emerald-300 text-emerald-900 font-bold font-mono"
                            >
                              ✓ {s}
                            </span>
                          ))}
                        </div>
                      )}

                      {job.missing_skills && job.missing_skills.length > 0 && (
                        <div className="flex flex-wrap items-center gap-1">
                          <span className="text-[10px] text-amber-800 font-bold">Add to Resume:</span>
                          {job.missing_skills.slice(0, 2).map((s: string) => (
                            <span
                              key={s}
                              className="text-[10px] px-2 py-0.5 rounded-lg bg-amber-100 border border-amber-300 text-amber-900 font-bold font-mono"
                            >
                              + {s}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>

                    <div className="pt-2 border-t border-slate-300/80 flex items-center justify-between">
                      <span className="text-[11px] text-slate-600 font-bold">
                        {job.location} {job.is_remote && "• Remote"}
                      </span>
                      <Link
                        href={`/jobs/${job.job_id}`}
                        className="text-xs font-bold text-indigo-700 hover:text-indigo-900 transition-colors"
                      >
                        Fit Breakdown →
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* 1. Contact & Personal Info */}
          <section className="neo-card p-6 rounded-2xl border border-white/90">
            <h2 className="text-base font-black text-slate-900 mb-4 pb-2 border-b border-slate-300/80 flex items-center justify-between">
              <span>Personal &amp; Contact Information</span>
              {getEvidenceForField("personal_info") && getConfidenceBadge(getEvidenceForField("personal_info")?.confidence_level)}
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              <div>
                <p className="text-xs text-slate-600 font-bold">Full Name</p>
                <p className="text-sm font-extrabold text-slate-900 mt-0.5">{extraction.personal_info?.full_name || "—"}</p>
              </div>
              <div>
                <p className="text-xs text-slate-600 font-bold">Email Address</p>
                <p className="text-sm font-extrabold text-slate-900 mt-0.5">{extraction.personal_info?.email || "—"}</p>
              </div>
              <div>
                <p className="text-xs text-slate-600 font-bold">Phone</p>
                <p className="text-sm font-extrabold text-slate-900 mt-0.5">{extraction.personal_info?.phone || "—"}</p>
              </div>
              <div>
                <p className="text-xs text-slate-600 font-bold">LinkedIn</p>
                <p className="text-sm font-bold text-indigo-700 mt-0.5 truncate">
                  {extraction.personal_info?.linkedin_url ? (
                    <a href={extraction.personal_info.linkedin_url} target="_blank" rel="noopener noreferrer" className="hover:underline">
                      {extraction.personal_info.linkedin_url}
                    </a>
                  ) : "—"}
                </p>
              </div>
              <div>
                <p className="text-xs text-slate-600 font-bold">GitHub</p>
                <p className="text-sm font-bold text-indigo-700 mt-0.5 truncate">
                  {extraction.personal_info?.github_url ? (
                    <a href={extraction.personal_info.github_url} target="_blank" rel="noopener noreferrer" className="hover:underline">
                      {extraction.personal_info.github_url}
                    </a>
                  ) : "—"}
                </p>
              </div>
              <div>
                <p className="text-xs text-slate-600 font-bold">Portfolio</p>
                <p className="text-sm font-bold text-indigo-700 mt-0.5 truncate">
                  {extraction.personal_info?.portfolio_url ? (
                    <a href={extraction.personal_info.portfolio_url} target="_blank" rel="noopener noreferrer" className="hover:underline">
                      {extraction.personal_info.portfolio_url}
                    </a>
                  ) : "—"}
                </p>
              </div>
            </div>
          </section>

          {/* 2. Professional Summary */}
          {extraction.summary && (
            <section className="neo-card p-6 rounded-2xl border border-white/90">
              <h2 className="text-base font-black text-slate-900 mb-3 pb-2 border-b border-slate-300/80 flex items-center justify-between">
                <span>Professional Summary</span>
                {getEvidenceForField("summary") && getConfidenceBadge(getEvidenceForField("summary")?.confidence_level)}
              </h2>
              <p className="text-sm text-slate-800 font-medium leading-relaxed">{extraction.summary.text}</p>
            </section>
          )}

          {/* 3. Work Experience */}
          <section className="neo-card p-6 rounded-2xl border border-white/90">
            <h2 className="text-base font-black text-slate-900 mb-4 pb-2 border-b border-slate-300/80">
              Work Experience ({extraction.experience?.length || 0})
            </h2>

            {extraction.experience?.length === 0 ? (
              <p className="text-sm text-slate-600 italic font-semibold">No work experience sections detected.</p>
            ) : (
              <div className="space-y-6">
                {extraction.experience?.map((exp: any, idx: number) => {
                  const ev = getEvidenceForField(`experience[${idx}]`);
                  return (
                    <div key={idx} className="pb-5 border-b border-slate-300/70 last:border-0 last:pb-0">
                      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
                        <div>
                          <h3 className="text-sm font-black text-slate-900">{exp.title}</h3>
                          <p className="text-xs font-bold text-indigo-700">{exp.company}</p>
                        </div>
                        <div className="mt-1 sm:mt-0 flex items-center space-x-2">
                          <span className="text-xs text-slate-600 font-bold">{exp.start_date} – {exp.end_date}</span>
                          {ev && getConfidenceBadge(ev.confidence_level)}
                        </div>
                      </div>

                      {exp.responsibilities?.length > 0 && (
                        <ul className="mt-3 space-y-1.5 list-disc list-inside text-xs text-slate-800 font-medium">
                          {exp.responsibilities.map((r: string, rIdx: number) => (
                            <li key={rIdx}>{r}</li>
                          ))}
                        </ul>
                      )}

                      {showEvidence && ev && (
                        <div className="mt-3 p-3 rounded-xl neo-inset text-[11px] text-slate-700 font-medium">
                          <span className="font-bold text-slate-900">Evidence Citation:</span> Page {ev.page_number || 1} • &ldquo;{ev.excerpt}&rdquo;
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </section>

          {/* 4. Internships (if present) */}
          {extraction.internships && extraction.internships.length > 0 && (
            <section className="neo-card p-6 rounded-2xl border border-white/90">
              <h2 className="text-base font-black text-slate-900 mb-4 pb-2 border-b border-slate-300/80">
                Internships &amp; Apprenticeships ({extraction.internships.length})
              </h2>
              <div className="space-y-4">
                {extraction.internships.map((intern: any, idx: number) => (
                  <div key={idx} className="pb-4 border-b border-slate-300/70 last:border-0 last:pb-0">
                    <div className="flex justify-between items-center">
                      <h3 className="text-sm font-black text-slate-900">{intern.title || "Intern"}</h3>
                      <span className="text-xs text-slate-600 font-bold">{intern.duration || ""}</span>
                    </div>
                    <p className="text-xs font-bold text-indigo-700">{intern.company || ""}</p>
                    {intern.responsibilities && (
                      <p className="text-xs text-slate-800 font-medium mt-1">{intern.responsibilities}</p>
                    )}
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* 5. Education */}
          <section className="neo-card p-6 rounded-2xl border border-white/90">
            <h2 className="text-base font-black text-slate-900 mb-4 pb-2 border-b border-slate-300/80">
              Education ({extraction.education?.length || 0})
            </h2>

            {extraction.education?.length === 0 ? (
              <p className="text-sm text-slate-600 italic font-semibold">No academic degrees detected.</p>
            ) : (
              <div className="space-y-4">
                {extraction.education?.map((edu: any, idx: number) => {
                  const ev = getEvidenceForField(`education[${idx}]`);
                  return (
                    <div key={idx} className="pb-4 border-b border-slate-300/70 last:border-0 last:pb-0">
                      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
                        <div>
                          <h3 className="text-sm font-black text-slate-900">{edu.degree || "Degree"}</h3>
                          <p className="text-xs text-slate-700 font-bold">{edu.institution}</p>
                        </div>
                        <div className="mt-1 sm:mt-0 flex items-center space-x-2">
                          {edu.start_date && (
                            <span className="text-xs text-slate-600 font-bold">{edu.start_date} – {edu.end_date}</span>
                          )}
                          {ev && getConfidenceBadge(ev.confidence_level)}
                        </div>
                      </div>
                      {edu.grade && (
                        <p className="text-xs text-emerald-800 font-bold mt-1">{edu.grade}</p>
                      )}

                      {showEvidence && ev && (
                        <div className="mt-2.5 p-3 rounded-xl neo-inset text-[11px] text-slate-700 font-medium">
                          <span className="font-bold text-slate-900">Evidence Citation:</span> Page {ev.page_number || 1} • &ldquo;{ev.excerpt}&rdquo;
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </section>

          {/* 6. Skills: Explicit vs. Inferred (HIGH CONTRAST & FULLY VISIBLE) */}
          <section className="neo-box p-6 rounded-2xl border border-white/95 space-y-6">
            <div className="border-b border-slate-300/80 pb-3 flex items-center justify-between">
              <div>
                <h2 className="text-lg font-black text-slate-900">
                  Categorized Technical Skills (Explicitly Stated)
                </h2>
                <p className="text-xs text-slate-600 font-semibold mt-0.5">
                  Directly verified from your resume sections. Click to inspect or copy.
                </p>
              </div>
              <span className="neo-pill text-xs px-3 py-1 rounded-xl text-indigo-700 font-bold">
                Verified Skills
              </span>
            </div>

            {/* Explicit Skills Categories */}
            <div className="space-y-5">
              {Object.keys(skillsMap).length === 0 ? (
                <p className="text-xs text-slate-600 italic font-semibold">No explicit skills categories detected.</p>
              ) : (
                Object.entries(skillsMap).map(([category, skillList]: [string, any]) => {
                  if (!skillList || (Array.isArray(skillList) && skillList.length === 0)) return null;
                  const list = Array.isArray(skillList) ? skillList : [skillList];

                  return (
                    <div key={category} className="space-y-2">
                      <p className="text-xs font-black text-indigo-700 uppercase tracking-wider flex items-center gap-1.5">
                        <span className="w-1.5 h-1.5 rounded-full bg-indigo-600" />
                        {category.replace(/_/g, " ")} ({list.length})
                      </p>
                      <div className="flex flex-wrap gap-2.5">
                        {list.map((s: any, sIdx: number) => {
                          const skillName = typeof s === "string" ? s : s?.name || JSON.stringify(s);
                          return (
                            <span
                              key={sIdx}
                              className="neo-pill px-3.5 py-1.5 rounded-xl text-xs font-bold text-slate-900 border border-white/90 shadow-sm inline-flex items-center gap-2 hover:scale-[1.03] transition-transform cursor-default"
                            >
                              <span className="w-2 h-2 rounded-full bg-indigo-600" />
                              <span>{skillName}</span>
                            </span>
                          );
                        })}
                      </div>
                    </div>
                  );
                })
              )}
            </div>

            {/* Inferred Skills Subsection */}
            {inferredList && inferredList.length > 0 && (
              <div className="mt-6 pt-5 border-t border-slate-300/80 space-y-3">
                <div className="flex items-center space-x-2">
                  <span className="text-xs font-black uppercase tracking-wider text-amber-900">
                    Inferred Technical Skills
                  </span>
                  <span className="text-[10px] px-2.5 py-0.5 rounded-full bg-amber-100 border border-amber-300 text-amber-950 font-bold">
                    Contextual Discovery • Unverified
                  </span>
                </div>
                <p className="text-xs text-slate-700 font-semibold">
                  These technologies were detected inside experience descriptions or project context. Confirm them in the Review Workbench.
                </p>
                <div className="flex flex-wrap gap-2.5">
                  {inferredList.map((s: any, sIdx: number) => {
                    const skillName = typeof s === "string" ? s : s?.name || JSON.stringify(s);
                    return (
                      <span
                        key={sIdx}
                        className="neo-inset px-3.5 py-1.5 rounded-xl text-xs font-bold text-amber-950 border border-amber-300/80 shadow-inner inline-flex items-center gap-2"
                      >
                        <span className="w-2 h-2 rounded-full bg-amber-600" />
                        <span>{skillName}</span>
                      </span>
                    );
                  })}
                </div>
              </div>
            )}
          </section>

          {/* 7. Supplementary Entities: Publications, Awards, Languages */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Publications */}
            <section className="neo-card p-6 rounded-2xl border border-white/90">
              <h2 className="text-base font-black text-slate-900 mb-3 pb-2 border-b border-slate-300/80">
                Publications ({extraction.publications?.length || 0})
              </h2>
              {(!extraction.publications || extraction.publications.length === 0) ? (
                <p className="text-xs text-slate-600 italic font-semibold">No publications detected.</p>
              ) : (
                <ul className="space-y-2 text-xs text-slate-800 font-semibold">
                  {extraction.publications.map((pub: any, idx: number) => (
                    <li key={idx} className="pb-2 border-b border-slate-300/70 last:border-0">
                      {pub.title || JSON.stringify(pub)}
                    </li>
                  ))}
                </ul>
              )}
            </section>

            {/* Awards */}
            <section className="neo-card p-6 rounded-2xl border border-white/90">
              <h2 className="text-base font-black text-slate-900 mb-3 pb-2 border-b border-slate-300/80">
                Awards &amp; Honors ({extraction.awards?.length || 0})
              </h2>
              {(!extraction.awards || extraction.awards.length === 0) ? (
                <p className="text-xs text-slate-600 italic font-semibold">No awards detected.</p>
              ) : (
                <ul className="space-y-2 text-xs text-slate-800 font-semibold">
                  {extraction.awards.map((aw: any, idx: number) => (
                    <li key={idx} className="pb-2 border-b border-slate-300/70 last:border-0">
                      {aw.title || JSON.stringify(aw)}
                    </li>
                  ))}
                </ul>
              )}
            </section>

            {/* Languages */}
            <section className="neo-card p-6 rounded-2xl border border-white/90">
              <h2 className="text-base font-black text-slate-900 mb-3 pb-2 border-b border-slate-300/80">
                Languages ({extraction.languages?.length || 0})
              </h2>
              {(!extraction.languages || extraction.languages.length === 0) ? (
                <p className="text-xs text-slate-600 italic font-semibold">No languages detected.</p>
              ) : (
                <div className="flex flex-wrap gap-2">
                  {extraction.languages.map((lang: any, idx: number) => (
                    <span key={idx} className="neo-pill px-3 py-1 rounded-xl text-xs font-bold text-slate-900 border border-white/90">
                      {lang.language || JSON.stringify(lang)}
                    </span>
                  ))}
                </div>
              )}
            </section>
          </div>

          {/* 8. Projects & Certifications */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <section className="neo-card p-6 rounded-2xl border border-white/90">
              <h2 className="text-base font-black text-slate-900 mb-4 pb-2 border-b border-slate-300/80">
                Key Projects ({extraction.projects?.length || 0})
              </h2>
              {extraction.projects?.length === 0 ? (
                <p className="text-xs text-slate-600 italic font-semibold">No specific projects section detected.</p>
              ) : (
                <div className="space-y-3">
                  {extraction.projects?.map((proj: any, idx: number) => (
                    <div key={idx} className="pb-3 border-b border-slate-300/70 last:border-0">
                      <p className="text-sm font-bold text-slate-900">{proj.name}</p>
                      <p className="text-xs text-slate-700 font-medium mt-1">{proj.description}</p>
                    </div>
                  ))}
                </div>
              )}
            </section>

            <section className="neo-card p-6 rounded-2xl border border-white/90">
              <h2 className="text-base font-black text-slate-900 mb-4 pb-2 border-b border-slate-300/80">
                Certifications ({extraction.certifications?.length || 0})
              </h2>
              {extraction.certifications?.length === 0 ? (
                <p className="text-xs text-slate-600 italic font-semibold">No certifications detected.</p>
              ) : (
                <div className="space-y-3">
                  {extraction.certifications?.map((cert: any, idx: number) => (
                    <div key={idx} className="pb-3 border-b border-slate-300/70 last:border-0">
                      <p className="text-sm font-bold text-slate-900">{cert.name}</p>
                    </div>
                  ))}
                </div>
              )}
            </section>
          </div>
        </div>
      ) : null}
    </div>
  );
}
