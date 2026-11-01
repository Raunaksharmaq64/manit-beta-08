"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { apiClient } from "@/services/apiClient";
import { fastCache } from "@/services/fastCache";

interface CandidateFit {
  fit_score: number;
  fit_percentage: number;
  fit_rating: string;
  how_you_fit: string;
  matched_skills: string[];
  missing_skills: string[];
  opportunity_domain: string;
  domain_display_name: string;
  domain_icon: string;
  tailored_resume_bullets?: Array<{
    skill: string;
    action: string;
    sample_bullet: string;
  }>;
  why_fit_points?: string[];
  resume_action_plan?: {
    add_skills: string[];
    emphasize_skills: string[];
    ats_boost_percentage: number;
  };
}

interface SavedEnvelope {
  schema_version: string;
  opportunity_id: string;
  opportunity_type: "JOB" | "FREELANCE" | "STARTUP_PAIN_POINT";
  title: string;
  short_description: string;
  organization_name: string;
  source_service: string;
  source_name: string;
  source_url?: string;
  location?: string;
  saved_id?: string;
  saved_notes?: string;
  saved_category?: string;
  saved_at?: string;
  opportunity_domain?: string;
  domain_display_name?: string;
  domain_icon?: string;
  candidate_fit?: CandidateFit;
  trust_metrics?: any;
  type_specific_payload: any;
}

const CATEGORY_TAGS: Record<string, { label: string; color: string; icon: string }> = {
  HIGH_PRIORITY: { label: "High Priority Fit", color: "text-emerald-400 bg-emerald-950/80 border-emerald-800", icon: "🎯" },
  APPLY_SOON: { label: "Apply This Week", color: "text-blue-400 bg-blue-950/80 border-blue-800", icon: "⚡" },
  STARTUP_SOLVE: { label: "Startup Solution", color: "text-purple-400 bg-purple-950/80 border-purple-800", icon: "💡" },
  OUTREACH_LEAD: { label: "Direct Outreach", color: "text-amber-400 bg-amber-950/80 border-amber-800", icon: "🤝" },
  RESEARCHING: { label: "Researching", color: "text-slate-400 bg-slate-800 border-slate-700", icon: "📁" },
  SAVED: { label: "Saved", color: "text-indigo-400 bg-indigo-950/80 border-indigo-800", icon: "★" },
};

export default function UnifiedSavedOpportunitiesPage() {
  const [savedItems, setSavedItems] = useState<SavedEnvelope[]>(() => {
    return fastCache.get<SavedEnvelope[]>("saved_opportunities_all") || [];
  });
  const [loading, setLoading] = useState(() => {
    return (fastCache.get<SavedEnvelope[]>("saved_opportunities_all") || []).length === 0;
  });
  const [error, setError] = useState<string | null>(null);
  const [removingId, setRemovingId] = useState<string | null>(null);
  const [activeCategory, setActiveCategory] = useState<string>("ALL");
  const [filterType, setFilterType] = useState<string>("ALL");
  const [expandedSkillsCards, setExpandedSkillsCards] = useState<Record<string, boolean>>({});

  const toggleSkillsExpanded = (id: string) => {
    setExpandedSkillsCards((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
  };


  const fetchSaved = async () => {
    if (savedItems.length === 0) setLoading(true);
    setError(null);
    try {
      const res: any = await apiClient.get("/opportunities/saved/all");
      const data = res.data || [];
      setSavedItems(data);
      fastCache.set("saved_opportunities_all", data, 120000);
    } catch (err: any) {
      if (savedItems.length === 0) setError(err?.message || "Failed to load saved opportunities.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSaved();
  }, []);

  const handleUnsave = async (item: SavedEnvelope) => {
    setRemovingId(item.opportunity_id);
    try {
      await apiClient.delete(`/opportunities/${item.opportunity_type}/${item.opportunity_id}/save`);
      setSavedItems(savedItems.filter((i) => i.opportunity_id !== item.opportunity_id));
    } catch (err: any) {
      alert(err?.message || "Failed to remove bookmark.");
    } finally {
      setRemovingId(null);
    }
  };

  const filteredItems = savedItems.filter((i) => {
    if (filterType !== "ALL" && i.opportunity_type !== filterType) return false;
    if (activeCategory !== "ALL") {
      const cat = i.saved_category || "SAVED";
      if (cat !== activeCategory) return false;
    }
    return true;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-3xl font-black tracking-tight text-slate-900 sm:text-4xl">
            Saved Opportunities & Bookmarks
          </h1>
          <p className="mt-2 text-sm text-slate-400">
            Organized candidate folders across Full-Time Jobs, Freelance Opportunities, and Startup Solutions.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            href="/dashboard"
            className="inline-flex items-center px-4 py-2 rounded-xl neo-pill text-xs sm:text-sm font-bold text-slate-900 hover:text-indigo-600 transition-all shadow-sm"
          >
            ← Back to Dashboard
          </Link>
          <Link
            href="/opportunities"
            className="inline-flex items-center px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-sm font-semibold text-white shadow-sm transition-colors"
          >
            Explore Pipeline →
          </Link>
        </div>
      </div>

      {/* Category Folders Filter Bar */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
            Bookmark Folders & Priorities:
          </span>
          <span className="text-xs text-slate-500">
            {savedItems.length} Total Bookmarks
          </span>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {[
            { id: "ALL", label: "All Bookmarks", icon: "📚", count: savedItems.length },
            {
              id: "HIGH_PRIORITY",
              label: "High Priority Fit",
              icon: "🎯",
              count: savedItems.filter((i) => i.saved_category === "HIGH_PRIORITY").length,
            },
            {
              id: "APPLY_SOON",
              label: "Apply This Week",
              icon: "⚡",
              count: savedItems.filter((i) => i.saved_category === "APPLY_SOON").length,
            },
            {
              id: "STARTUP_SOLVE",
              label: "Startup Solution",
              icon: "💡",
              count: savedItems.filter((i) => i.saved_category === "STARTUP_SOLVE").length,
            },
            {
              id: "OUTREACH_LEAD",
              label: "Direct Outreach",
              icon: "🤝",
              count: savedItems.filter((i) => i.saved_category === "OUTREACH_LEAD").length,
            },
            {
              id: "RESEARCHING",
              label: "Researching",
              icon: "📁",
              count: savedItems.filter((i) => i.saved_category === "RESEARCHING").length,
            },
          ].map((cat) => {
            const isActive = activeCategory === cat.id;
            return (
              <button
                key={cat.id}
                onClick={() => setActiveCategory(cat.id)}
                className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5 ${isActive
                    ? "bg-indigo-600 text-white shadow"
                    : "bg-slate-900 text-slate-400 hover:bg-slate-800 border border-slate-800"
                  }`}
              >
                <span>{cat.icon}</span>
                <span>{cat.label}</span>
                <span
                  className={`px-1.5 py-0.2 rounded-full text-[10px] ${isActive ? "bg-indigo-800 text-indigo-200" : "bg-slate-800 text-slate-400"
                    }`}
                >
                  {cat.count}
                </span>
              </button>
            );
          })}
        </div>

        {/* Opportunity Type Sub-filters */}
        <div className="flex items-center gap-2 pt-2 border-t border-slate-800/60">
          <span className="text-[11px] text-slate-500 font-medium">Type:</span>
          {[
            { id: "ALL", label: "All Types" },
            { id: "JOB", label: "Jobs" },
            { id: "FREELANCE", label: "Freelance" },
            { id: "STARTUP_PAIN_POINT", label: "Startup Signals" },
          ].map((t) => (
            <button
              key={t.id}
              onClick={() => setFilterType(t.id)}
              className={`text-xs px-2.5 py-0.5 rounded transition-colors ${filterType === t.id
                  ? "bg-slate-700 text-white font-semibold"
                  : "text-slate-400 hover:text-slate-200"
                }`}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl border border-rose-800/60 bg-rose-950/40 text-sm text-rose-300">
          {error}
        </div>
      )}

      {loading && savedItems.length === 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-pulse">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-60 rounded-xl bg-slate-900 border border-slate-800" />
          ))}
        </div>
      ) : filteredItems.length === 0 ? (
        <div className="text-center py-16 rounded-xl bg-slate-900 border border-slate-800 text-slate-400">
          <p className="text-base font-medium text-slate-300">No saved bookmarks in this folder.</p>
          <p className="text-xs text-slate-500 mt-1">
            Bookmark opportunities from the Unified Pipeline to organize them into folders.
          </p>
          <div className="mt-4">
            <Link
              href="/opportunities"
              className="text-xs font-semibold text-indigo-400 hover:text-indigo-300"
            >
              Browse pipeline now →
            </Link>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredItems.map((item) => {
            const isJob = item.opportunity_type === "JOB";
            const isFreelance = item.opportunity_type === "FREELANCE";

            const badgeColor = isJob
              ? "bg-blue-950 text-blue-300 border-blue-800"
              : isFreelance
                ? "bg-emerald-950 text-emerald-300 border-emerald-800"
                : "bg-purple-950 text-purple-300 border-purple-800";

            const badgeText = isJob ? "Full-Time Job" : isFreelance ? "💼 Freelance Client Lead" : "💡 Startup Pain Point";

            const categoryMeta =
              CATEGORY_TAGS[item.saved_category || "SAVED"] || CATEGORY_TAGS["SAVED"];

            const fit = item.candidate_fit;

            const requiredSkills: string[] =
              Array.isArray(item.type_specific_payload?.required_skills) && item.type_specific_payload.required_skills.length > 0
                ? item.type_specific_payload.required_skills
                : Array.isArray(item.type_specific_payload?.tech_stack) && item.type_specific_payload.tech_stack.length > 0
                  ? item.type_specific_payload.tech_stack
                  : [];

            const matchedSkills: string[] =
              Array.isArray(fit?.matched_skills) && fit.matched_skills.length > 0
                ? fit.matched_skills
                : Array.isArray(item.type_specific_payload?.matched_skills)
                  ? item.type_specific_payload.matched_skills
                  : [];

            const missingSkills: string[] =
              Array.isArray(fit?.missing_skills) && fit.missing_skills.length > 0
                ? fit.missing_skills
                : Array.isArray(item.type_specific_payload?.missing_skills)
                  ? item.type_specific_payload.missing_skills
                  : [];

            return (
              <div
                key={`${item.opportunity_type}-${item.opportunity_id}`}
                className="neo-card neo-box-hover p-5 rounded-2xl border border-white/90 flex flex-col justify-between transition-all duration-200 space-y-3"
              >
                <div className="space-y-3">
                  {/* Category Folder Badge & Opportunity Type */}
                  <div className="flex items-center justify-between gap-2 flex-wrap">
                    <div className="flex items-center gap-1.5 flex-wrap">
                      <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded border ${badgeColor}`}>
                        {badgeText}
                      </span>
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded border flex items-center gap-1 ${categoryMeta.color}`}
                      >
                        <span>{categoryMeta.icon}</span>
                        <span>{categoryMeta.label}</span>
                      </span>
                      {item.domain_display_name && (
                        <span className="text-[10px] font-medium px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                          {item.domain_icon} {item.domain_display_name}
                        </span>
                      )}
                    </div>
                    <span className="text-xs text-slate-400 font-medium">
                      {item.source_name}
                    </span>
                  </div>

                  <div>
                    <h3 className="text-base font-black text-slate-900 line-clamp-2 hover:text-indigo-600 transition-colors">
                      {item.title}
                    </h3>
                    <div className="text-xs font-medium text-indigo-400 mt-0.5">
                      {item.organization_name}
                      {item.location && <span className="text-slate-400"> • {item.location}</span>}
                    </div>
                  </div>

                  <p className="text-xs text-slate-700 font-medium line-clamp-2 leading-relaxed">
                    {item.short_description}
                  </p>

                  {/* Company Requirements & Skills Alignment */}
                  {(requiredSkills.length > 0 || matchedSkills.length > 0) && (
                    <div className="p-3.5 rounded-xl neo-inset space-y-2.5">
                      {/* Company Required Skills */}
                      {requiredSkills.length > 0 && (
                        <div className="space-y-1.5">
                          <div className="flex items-center justify-between text-[11px] font-bold text-slate-700 uppercase tracking-wider">
                            <span>Company Required Skills</span>
                            <span className="text-[10px] text-slate-600 font-bold">
                              {requiredSkills.length} required
                            </span>
                          </div>
                          <div className="flex flex-wrap gap-1.5">
                            {requiredSkills.map((skill: string, sIdx: number) => {
                              const isMatched = matchedSkills.some(
                                (m) => m.toLowerCase() === skill.toLowerCase()
                              );
                              return (
                                <span
                                  key={sIdx}
                                  className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-[11px] font-bold border transition-all ${isMatched
                                      ? "bg-emerald-100 border-emerald-300 text-emerald-900 shadow-sm"
                                      : "neo-pill text-slate-800 border-slate-200"
                                    }`}
                                  title={isMatched ? "Matched in your resume" : "Company required skill"}
                                >
                                  {isMatched && <span className="text-emerald-700 font-black">✓</span>}
                                  <span>{skill}</span>
                                </span>
                              );
                            })}
                          </div>
                        </div>
                      )}

                      {/* Matched & Missing Skills Summary */}
                      {(() => {
                        const isSkillsExpanded = !!expandedSkillsCards[item.opportunity_id];
                        const visibleMatched = isSkillsExpanded ? matchedSkills : matchedSkills.slice(0, 4);
                        const visibleMissing = isSkillsExpanded ? missingSkills : missingSkills.slice(0, 3);
                        return (
                          <div className="flex flex-wrap items-center gap-x-4 gap-y-1.5 pt-2 border-t border-slate-200/80 text-xs">
                            {matchedSkills.length > 0 && (
                              <div className="flex items-center gap-1.5 flex-wrap">
                                <span className="text-[11px] font-bold text-emerald-800">Matched in Resume:</span>
                                <div className="flex items-center gap-1 flex-wrap">
                                  {visibleMatched.map((ms, idx) => (
                                    <span
                                      key={idx}
                                      className="text-[10px] px-2 py-0.5 rounded-lg bg-emerald-100 text-emerald-900 border border-emerald-300 font-mono font-bold"
                                    >
                                      ✓ {ms}
                                    </span>
                                  ))}
                                  {matchedSkills.length > 4 && (
                                    <button
                                      type="button"
                                      onClick={() => toggleSkillsExpanded(item.opportunity_id)}
                                      className="text-[10px] px-2 py-0.5 rounded-lg neo-pill text-emerald-800 hover:text-emerald-950 font-mono font-bold cursor-pointer transition-all"
                                      title={isSkillsExpanded ? "Collapse matched skills" : "Show all matched skills"}
                                    >
                                      {isSkillsExpanded ? "▲ Less" : `+${matchedSkills.length - 4} more`}
                                    </button>
                                  )}
                                </div>
                              </div>
                            )}
                            {missingSkills.length > 0 && (
                              <div className="flex items-center gap-1.5 flex-wrap">
                                <span className="text-[11px] font-bold text-amber-800">Missing from Resume:</span>
                                <div className="flex items-center gap-1 flex-wrap">
                                  {visibleMissing.map((mis, idx) => (
                                    <span
                                      key={idx}
                                      className="text-[10px] px-2 py-0.5 rounded-lg bg-amber-100 text-amber-900 border border-amber-300 font-mono font-bold"
                                    >
                                      + {mis}
                                    </span>
                                  ))}
                                  {missingSkills.length > 3 && (
                                    <button
                                      type="button"
                                      onClick={() => toggleSkillsExpanded(item.opportunity_id)}
                                      className="text-[10px] px-2 py-0.5 rounded-lg neo-pill text-amber-800 hover:text-amber-950 font-mono font-bold cursor-pointer transition-all"
                                      title={isSkillsExpanded ? "Collapse missing skills" : "Show all missing skills"}
                                    >
                                      {isSkillsExpanded ? "▲ Less" : `+${missingSkills.length - 3} more`}
                                    </button>
                                  )}
                                </div>
                              </div>
                            )}
                          </div>
                        );
                      })()}
                    </div>
                  )}

                  {/* Dynamic Candidate Fit Note */}
                  {fit && (
                    <div className="p-2.5 rounded-lg bg-slate-950/80 border border-indigo-950 text-xs space-y-1">
                      <div className="flex items-center justify-between text-[11px] font-bold text-white">
                        <span>Synergy: {fit.fit_percentage}% ({fit.fit_rating})</span>
                        <span className="text-[10px] text-indigo-700 font-mono font-bold">Calibrated</span>
                      </div>
                      <p className="text-xs text-slate-700 leading-relaxed font-medium">
                        {fit.how_you_fit}
                      </p>
                    </div>
                  )}

                  {/* Freelance Outreach Channels & Web Health */}
                  {isFreelance && item.type_specific_payload && (
                    <div className="p-2.5 rounded-lg bg-slate-950/80 border border-emerald-950 text-xs space-y-1.5">
                      <div className="flex items-center justify-between text-[11px]">
                        <span className="text-emerald-400 font-medium">
                          Category: {item.type_specific_payload.service_category || "Web Modernization"}
                        </span>
                        {item.type_specific_payload.rating > 0 && (
                          <span className="text-slate-400">
                            ★ {item.type_specific_payload.rating} ({item.type_specific_payload.reviews_count || 0})
                          </span>
                        )}
                      </div>
                      <div className="flex flex-wrap items-center gap-1.5 text-[10px]">
                        {item.type_specific_payload.is_broken_website && (
                          <span className="px-1.5 py-0.5 rounded-lg bg-rose-100 text-rose-900 border border-rose-300 font-bold">
                            ⚠️ Broken Site
                          </span>
                        )}
                        {!item.type_specific_payload.website && !item.type_specific_payload.is_broken_website && (
                          <span className="px-1.5 py-0.5 rounded-lg bg-amber-100 text-amber-900 border border-amber-300 font-bold">
                            ⚠️ No Website
                          </span>
                        )}
                        {item.type_specific_payload.email && (
                          <span className="px-1.5 py-0.5 rounded-lg bg-emerald-100 text-emerald-900 border border-emerald-300 font-mono font-bold">
                            ✉ {item.type_specific_payload.email}
                          </span>
                        )}
                        {item.type_specific_payload.phone && (
                          <span className="px-1.5 py-0.5 rounded-lg bg-blue-100 text-blue-900 border border-blue-300 font-mono font-bold">
                            📞 {item.type_specific_payload.phone}
                          </span>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Live Trust Badge */}
                  {item.trust_metrics && (
                    <div className="pt-2 border-t border-slate-200 flex items-center justify-between gap-1 flex-wrap text-[10px]">
                      <span className="inline-flex items-center gap-1 font-bold text-emerald-900 bg-emerald-100 border border-emerald-300 px-2 py-0.5 rounded-full">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 animate-pulse" />
                        {item.trust_metrics.trust_tier_label}
                      </span>
                      <span className="text-slate-700 font-mono font-bold">
                        {item.trust_metrics.ghost_job_risk.urgency_label}
                      </span>
                    </div>
                  )}

                  {item.saved_notes && (
                    <div className="p-2.5 rounded-xl neo-inset border border-amber-300/80 text-xs text-amber-950 font-sans">
                      <span className="text-slate-700 font-bold uppercase text-[10px] block mb-0.5">
                        Private Note:
                      </span>
                      {item.saved_notes}
                    </div>
                  )}
                </div>

                <div className="mt-4 pt-3 border-t border-slate-200 flex items-center justify-between gap-2 flex-wrap">
                  <div className="flex items-center gap-2 flex-wrap">
                    <button
                      onClick={() => handleUnsave(item)}
                      disabled={removingId === item.opportunity_id}
                      className="text-xs font-bold px-2.5 py-1 rounded-lg neo-pill text-rose-800 hover:text-rose-950 border border-rose-300 transition-colors cursor-pointer"
                    >
                      {removingId === item.opportunity_id ? "Removing..." : "Remove"}
                    </button>

                    {item.opportunity_type === "JOB" && (
                      <>
                        <Link
                          href={`/jobs/${item.opportunity_id}`}
                          className="text-xs font-bold px-3 py-1.5 rounded-xl neo-pill text-indigo-900 hover:text-indigo-600 border border-indigo-200 transition-all"
                        >
                          View Details →
                        </Link>
                        {item.source_url ? (
                          <a
                            href={item.source_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs font-semibold px-2.5 py-1 rounded bg-indigo-600 hover:bg-indigo-500 text-white transition-colors"
                          >
                            Apply on ATS ↗
                          </a>
                        ) : null}
                      </>
                    )}

                    {item.opportunity_type === "FREELANCE" && (
                      <>
                        <Link
                          href={`/freelance/${item.opportunity_id}`}
                          className="text-xs font-semibold px-2.5 py-1 rounded bg-emerald-600 hover:bg-emerald-500 text-white transition-colors shadow-sm"
                        >
                          Pitch Client & Lead Info →
                        </Link>
                        {item.source_url ? (
                          <a
                            href={item.source_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs font-bold px-3 py-1.5 rounded-xl neo-pill text-slate-900 hover:text-indigo-600 transition-all"
                          >
                            Client Website ↗
                          </a>
                        ) : null}
                      </>
                    )}

                    {item.opportunity_type === "STARTUP_PAIN_POINT" && (
                      <>
                        <Link
                          href={`/startups/${item.opportunity_id}`}
                          className="text-xs font-semibold px-2.5 py-1 rounded bg-purple-600 hover:bg-purple-500 text-white transition-colors shadow-sm"
                        >
                          Solve Pain Point →
                        </Link>
                        {item.source_url ? (
                          <a
                            href={item.source_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs font-bold px-3 py-1.5 rounded-xl neo-pill text-slate-900 hover:text-indigo-600 transition-all"
                          >
                            Product Site ↗
                          </a>
                        ) : null}
                      </>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
