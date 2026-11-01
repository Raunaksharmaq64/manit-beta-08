"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { apiClient } from "@/services/apiClient";
import { fastCache } from "@/services/fastCache";
import VerificationProofModal, { VerificationItem } from "@/components/opportunities/VerificationProofModal";

interface SummaryMetrics {
  total_opportunities: number;
  total_jobs: number;
  total_freelance: number;
  total_startups: number;
  total_saved: number;
  active_applications: number;
  high_urgency_signals: number;
  new_this_week: number;
}

interface SourceHealth {
  core_career_engine: string;
  leadhunter_satellite: string;
  startup_intelligence_satellite: string;
  all_systems_operational: boolean;
}

interface OpportunityItem {
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
  is_remote?: boolean;
  published_at?: string;
  freshness_state?: string;
  classification_state?: string;
  is_saved?: boolean;
  is_new_signal?: boolean;
  opportunity_domain?: string;
  domain_display_name?: string;
  domain_icon?: string;
  candidate_fit?: {
    fit_score: number;
    fit_percentage: number;
    fit_rating: string;
    how_you_fit: string;
    matched_skills: string[];
    missing_skills: string[];
  };
  trust_metrics?: any;
  type_specific_payload: any;
}

export default function UnifiedDashboardPage() {
  const [metrics, setMetrics] = useState<SummaryMetrics | null>(() => {
    return fastCache.get<SummaryMetrics>("dash_metrics") || null;
  });
  const [health, setHealth] = useState<SourceHealth | null>(() => {
    return fastCache.get<SourceHealth>("dash_health") || null;
  });
  const [recentOpportunities, setRecentOpportunities] = useState<OpportunityItem[]>(() => {
    return fastCache.get<OpportunityItem[]>("dash_recent_opps") || [];
  });
  const [loading, setLoading] = useState(() => {
    return !fastCache.get<SummaryMetrics>("dash_metrics");
  });
  const [error, setError] = useState<string | null>(null);
  const [savingId, setSavingId] = useState<string | null>(null);
  const [proofItem, setProofItem] = useState<VerificationItem | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const fetchDashboard = async (forceFresh = false) => {
    if (!metrics) setLoading(true);
    if (forceFresh) setIsRefreshing(true);
    setError(null);
    try {
      const url = forceFresh ? `/dashboard?refresh=true&_t=${Date.now()}` : "/dashboard";
      const res: any = await apiClient.get(url);
      const data = res.data;
      setMetrics(data.summary_metrics);
      setHealth(data.source_health);
      setRecentOpportunities(data.recent_opportunities || []);
      fastCache.set("dash_metrics", data.summary_metrics, 30000);
      fastCache.set("dash_health", data.source_health, 30000);
      fastCache.set("dash_recent_opps", data.recent_opportunities || [], 30000);
    } catch (err: any) {
      if (!metrics) setError(err?.message || "Failed to load dashboard metrics.");
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    // Always trigger fresh background sync on reload / navigation
    fetchDashboard(true);
  }, []);

  const handleToggleSave = async (item: OpportunityItem) => {
    setSavingId(item.opportunity_id);
    try {
      if (item.is_saved) {
        await apiClient.delete(`/opportunities/${item.opportunity_type}/${item.opportunity_id}/save`);
        item.is_saved = false;
        if (metrics) setMetrics({ ...metrics, total_saved: Math.max(0, metrics.total_saved - 1) });
      } else {
        await apiClient.post(`/opportunities/${item.opportunity_type}/${item.opportunity_id}/save`, {
          notes: "Saved from Unified Dashboard",
        });
        item.is_saved = true;
        if (metrics) setMetrics({ ...metrics, total_saved: metrics.total_saved + 1 });
      }
      setRecentOpportunities([...recentOpportunities]);
    } catch (err: any) {
      alert(err?.message || "Failed to update saved status.");
    } finally {
      setSavingId(null);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-3xl font-black tracking-tight text-slate-900 sm:text-4xl">
            Career Intelligence Dashboard
          </h1>
          <p className="mt-2 text-sm text-slate-400">
            Unified view across verified full-time jobs, freelance gigs, startup pain points, and applications.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => fetchDashboard(true)}
            disabled={isRefreshing}
            className="neo-pill inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold text-slate-800 hover:text-indigo-600 transition-all duration-200 disabled:opacity-60"
            title="Fetch real-time updates and fresh metrics"
          >
            <span className={isRefreshing ? "animate-spin" : ""}>🔄</span>
            {isRefreshing ? "Refreshing..." : "Refresh Live Data"}
          </button>
          <Link
            href="/opportunities"
            className="neo-btn-primary inline-flex items-center px-4 py-2 rounded-xl text-xs font-bold transition-all shadow-md"
          >
            Explore All Opportunities →
          </Link>
          <Link
            href="/saved-opportunities"
            className="neo-pill inline-flex items-center px-4 py-2 rounded-xl text-xs font-bold text-slate-800 hover:text-indigo-600 transition-all duration-200"
          >
            View Bookmarks ({metrics?.total_saved ?? 0})
          </Link>
        </div>
      </div>



      {error && (
        <div className="rounded-xl border border-rose-800/60 bg-rose-950/40 p-4 text-sm text-rose-300">
          {error}
        </div>
      )}

      {/* Summary KPI Grid */}
      {loading && !metrics ? (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 animate-pulse">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="h-28 rounded-xl bg-slate-900 border border-slate-800" />
          ))}
        </div>
      ) : metrics ? (
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs text-slate-700 font-bold">

            <span className="font-black tracking-wide uppercase text-slate-900">Live Opportunities Overview</span>
            <span className="neo-pill px-3 py-1 rounded-xl text-emerald-800 font-bold text-xs flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              Live Synchronized Pipeline
            </span>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {/* 1. Total Opportunities */}
            <Link
              href="/opportunities"
              className="neo-card neo-box-hover p-5 rounded-2xl border border-white/90 group cursor-pointer"
            >
              <div className="text-xs font-medium text-indigo-700 uppercase tracking-wider font-extrabold">Total Opportunities</div>
              <div className="mt-2 text-3xl font-black text-slate-900 group-hover:text-indigo-600 transition-colors font-black">
                {metrics.total_opportunities}
              </div>
              <div className="mt-1 text-xs text-slate-600 font-semibold">Aggregated live openings</div>
            </Link>

            {/* 2. Canonical Jobs */}
            <Link
              href="/opportunities?type=JOB"
              className="neo-card neo-box-hover p-5 rounded-2xl border border-white/90 group cursor-pointer"
            >
              <div className="text-xs font-medium text-blue-700 uppercase tracking-wider font-extrabold">Full-Time Jobs</div>
              <div className="mt-2 text-3xl font-black text-slate-900 group-hover:text-blue-600 transition-colors font-black">
                {metrics.total_jobs}
              </div>
              <div className="mt-1 text-xs text-slate-600 font-semibold">Verified canonical openings</div>
            </Link>

            {/* 3. Freelance Leads */}
            <Link
              href="/opportunities?type=FREELANCE"
              className="neo-card neo-box-hover p-5 rounded-2xl border border-white/90 group cursor-pointer"
            >
              <div className="text-xs font-medium text-emerald-700 uppercase tracking-wider font-extrabold">Freelance Projects</div>
              <div className="mt-2 text-3xl font-black text-slate-900 group-hover:text-emerald-600 transition-colors font-black">
                {metrics.total_freelance}
              </div>
              <div className="mt-1 text-xs text-slate-600 font-semibold">Direct business outreach</div>
            </Link>

            {/* 4. Startup Pain Points */}
            <Link
              href="/opportunities?type=STARTUP_PAIN_POINT"
              className="neo-card neo-box-hover p-5 rounded-2xl border border-white/90 group cursor-pointer"
            >
              <div className="text-xs font-medium text-purple-700 uppercase tracking-wider font-extrabold">Startup Pain Points</div>
              <div className="mt-2 text-3xl font-black text-slate-900 group-hover:text-purple-600 transition-colors font-black">
                {metrics.total_startups}
              </div>
              <div className="mt-1 text-xs text-slate-600 font-semibold">Technical bottlenecks & demands</div>
            </Link>

            {/* 5. Total Bookmarks */}
            <Link
              href="/saved-opportunities"
              className="neo-card neo-box-hover p-5 rounded-2xl border border-white/90 group cursor-pointer"
            >
              <div className="text-xs font-medium text-amber-700 uppercase tracking-wider font-extrabold">Saved Bookmarks</div>
              <div className="mt-2 text-3xl font-black text-slate-900 group-hover:text-amber-600 transition-colors font-black">
                {metrics.total_saved}
              </div>
              <div className="mt-1 text-xs text-slate-600 font-semibold">Cross-module saved items</div>
            </Link>

            {/* 6. Active CRM Applications */}
            <Link
              href="/applications"
              className="neo-card neo-box-hover p-5 rounded-2xl border border-white/90 group cursor-pointer"
            >
              <div className="text-xs font-medium text-cyan-700 uppercase tracking-wider font-extrabold">Active Applications</div>
              <div className="mt-2 text-3xl font-black text-slate-900 group-hover:text-cyan-600 transition-colors font-black">
                {metrics.active_applications}
              </div>
              <div className="mt-1 text-xs text-slate-600 font-semibold">Tracked in Application CRM</div>
            </Link>

            {/* 7. High Urgency Startups */}
            <Link
              href="/opportunities?type=STARTUP_PAIN_POINT"
              className="neo-card neo-box-hover p-5 rounded-2xl border border-white/90 group cursor-pointer"
            >
              <div className="text-xs font-medium text-rose-700 uppercase tracking-wider font-extrabold">High-Urgency Problems</div>
              <div className="mt-2 text-3xl font-black text-slate-900 group-hover:text-rose-600 transition-colors font-black">
                {metrics.high_urgency_signals}
              </div>
              <div className="mt-1 text-xs text-slate-600 font-semibold">High-conviction founders</div>
            </Link>

            {/* 8. New This Week */}
            <div className="neo-card neo-box-hover p-5 rounded-2xl border border-white/90 group">
              <div className="text-xs font-medium text-teal-700 uppercase tracking-wider font-extrabold">Discovered This Week</div>
              <div className="mt-2 text-3xl font-black text-slate-900">
                +{metrics.new_this_week}
              </div>
              <div className="mt-1 text-xs text-slate-600 font-semibold">Ingested past 7 days</div>
            </div>
          </div>
        </div>
      ) : null}

      {/* Recent Opportunities Across Modules */}
      <div className="space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div>
            <h2 className="text-xl font-black text-slate-900">Recent Live Opportunities</h2>
            <p className="text-xs text-slate-600 font-semibold">Latest discovered positions and pain points across live job boards, freelance leads, and startup intelligence.</p>
          </div>
          <Link
            href="/opportunities"
            className="text-xs font-semibold text-indigo-700 hover:text-indigo-900 font-bold transition-colors"
          >
            View all opportunities →
          </Link>
        </div>

        {loading && recentOpportunities.length === 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-44 rounded-xl bg-slate-900 border border-slate-800 animate-pulse" />
            ))}
          </div>
        ) : recentOpportunities.length === 0 ? (
          <div className="text-center py-12 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 text-sm">
            No opportunities discovered yet. Trigger connectors or lead discovery to populate.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {recentOpportunities.map((item) => {
              const typeBadgeColors = {
                JOB: "bg-blue-100 text-blue-900 border-blue-300",
                FREELANCE: "bg-emerald-100 text-emerald-900 border-emerald-300",
                STARTUP_PAIN_POINT: "bg-purple-100 text-purple-900 border-purple-300",
              };

              const typeLabels = {
                JOB: "Full-Time Job",
                FREELANCE: "Freelance Lead",
                STARTUP_PAIN_POINT: "Startup Pain Point",
              };

              return (
                <div
                  key={`${item.opportunity_type}-${item.opportunity_id}`}
                  className="neo-card neo-box-hover p-5 rounded-2xl border border-white/90 flex flex-col justify-between transition-all duration-200"
                >
                  <div className="space-y-2.5">
                    <div className="flex items-center justify-between gap-2 flex-wrap">
                      <div className="flex items-center gap-1.5 flex-wrap">
                        <span
                          className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded border ${
                            typeBadgeColors[item.opportunity_type] || "bg-slate-800 text-slate-300 border-slate-700"
                          }`}
                        >
                          {typeLabels[item.opportunity_type]}
                        </span>
                        {item.domain_display_name && (
                          <span className="text-[10px] font-medium px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                            {item.domain_icon} {item.domain_display_name}
                          </span>
                        )}
                        {item.is_new_signal && (
                          <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800 animate-pulse">
                            ✨ NEW
                          </span>
                        )}
                      </div>
                      <span className="text-xs text-slate-600 font-semibold font-medium">
                        {item.source_name}
                      </span>
                    </div>

                    <h3 className="text-base font-bold text-slate-900 line-clamp-1 hover:text-indigo-600 transition-colors">
                      {item.title}
                    </h3>
                    <div className="text-xs text-indigo-700 font-bold">
                      {item.organization_name}
                      {item.location && <span className="text-slate-400"> • {item.location}</span>}
                    </div>

                    <p className="text-xs text-slate-700 font-medium line-clamp-2 leading-relaxed">
                      {item.short_description}
                    </p>

                    {/* Dynamic Candidate Fit */}
                    {item.candidate_fit && (
                      <div className="neo-inset p-3 rounded-xl text-[11px] space-y-1 text-slate-800 font-medium">
                        <div className="flex items-center justify-between font-extrabold text-slate-900">
                          <span className="flex items-center gap-1">
                            <span
                              className={`w-1.5 h-1.5 rounded-full ${
                                item.candidate_fit.fit_percentage >= 80 ? "bg-emerald-400" : "bg-blue-400"
                              }`}
                            />
                            Fit: {item.candidate_fit.fit_percentage}% ({item.candidate_fit.fit_rating})
                          </span>
                          <span className="text-[10px] text-indigo-300 font-mono">Resume Synergy</span>
                        </div>
                        <p className="text-slate-700 font-semibold line-clamp-1 text-[11px]">
                          {item.candidate_fit.how_you_fit}
                        </p>
                      </div>
                    )}

                    {/* Specific payload badges */}
                    <div className="text-xs text-slate-600 font-semibold flex flex-wrap gap-2 pt-1 font-mono">
                      {item.opportunity_type === "JOB" && item.type_specific_payload.salary_min && (
                        <span className="neo-pill px-2.5 py-0.5 rounded-lg text-slate-900 font-bold">
                          ${item.type_specific_payload.salary_min.toLocaleString()} - ${item.type_specific_payload.salary_max?.toLocaleString()}
                        </span>
                      )}
                      {item.opportunity_type === "FREELANCE" && (
                        <span className="neo-pill px-2.5 py-0.5 rounded-lg text-emerald-900 font-bold">
                          {item.type_specific_payload.service_category}
                        </span>
                      )}
                      {item.opportunity_type === "STARTUP_PAIN_POINT" && (
                        <span className="neo-pill px-2.5 py-0.5 rounded-lg text-rose-900 font-bold">
                          Urgency: {item.type_specific_payload.urgency_score}/10
                        </span>
                      )}
                    </div>

                    {/* Trust Tier & Ghost Job Indicator */}
                    {item.trust_metrics && (
                      <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between gap-1 flex-wrap text-[10px]">
                        <span className="inline-flex items-center gap-1 font-semibold text-emerald-400 bg-emerald-950/60 border border-emerald-800/80 px-2 py-0.5 rounded-full">
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                          {item.trust_metrics.trust_tier_label}
                        </span>
                        <span className="text-slate-400 font-mono">
                          👻 {item.trust_metrics.ghost_job_risk.urgency_label}
                        </span>
                      </div>
                    )}
                  </div>

                  <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between gap-2 flex-wrap">
                    <div className="flex items-center gap-1.5">
                      <button
                        onClick={() => handleToggleSave(item)}
                        disabled={savingId === item.opportunity_id}
                        className={`text-xs font-semibold px-2.5 py-1 rounded transition-colors ${
                          item.is_saved
                            ? "bg-amber-900/60 text-amber-300 border border-amber-700/60"
                            : "neo-pill text-slate-800 hover:text-indigo-700 font-bold"
                        }`}
                      >
                        {item.is_saved ? "★ Bookmarked" : "☆ Save"}
                      </button>

                      <button
                        type="button"
                        onClick={() => setProofItem(item as any)}
                        className="text-xs font-bold px-2.5 py-1.5 rounded-xl neo-pill text-indigo-900 border border-indigo-200 hover:text-indigo-600 transition-all flex items-center gap-1"
                        title="Inspect verifiable proof and ATS handshake"
                      >
                        <span>🛡️</span>
                        <span>Proof</span>
                      </button>

                      {item.opportunity_type === "JOB" && (
                        <Link
                          href={`/jobs/${item.opportunity_id}`}
                          className="text-xs font-bold px-2.5 py-1.5 rounded-xl neo-pill text-indigo-900 border border-indigo-200 hover:text-indigo-600 transition-all flex items-center gap-1"
                          title="View match breakdown and missing skills for your resume"
                        >
                          <span>🎯</span>
                          <span>Match & Gaps</span>
                        </Link>
                      )}
                    </div>

                    {item.source_url ? (
                      <a
                        href={item.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs font-medium text-indigo-700 hover:text-indigo-900 font-bold transition-colors"
                      >
                        Apply / Source →
                      </a>
                    ) : (
                      <Link
                        href={`/opportunities?type=${item.opportunity_type}`}
                        className="text-xs font-medium text-slate-400 hover:text-white transition-colors"
                      >
                        Details →
                      </Link>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Authenticity & Verification Proof Modal */}
      <VerificationProofModal
        item={proofItem}
        onClose={() => setProofItem(null)}
      />
    </div>
  );
}

