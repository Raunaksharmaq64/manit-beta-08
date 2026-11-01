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

interface OpportunityEnvelope {
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
  first_discovered_at?: string;
  last_checked_at?: string;
  freshness_state?: string;
  classification_state?: string;
  evidence_count?: number;
  is_saved?: boolean;
  is_new_signal?: boolean;
  opportunity_domain?: string;
  domain_display_name?: string;
  domain_icon?: string;
  candidate_fit?: CandidateFit;
  trust_metrics?: any;
  contact_info?: any;
  type_specific_payload: any;
}

interface CountsByType {
  jobs: number;
  freelance: number;
  startup_pain_points: number;
  total: number;
  jobs_breakdown?: {
    full_time: number;
    internship: number;
    contract: number;
  };
}

interface CandidatePersona {
  has_profile: boolean;
  primary_domain: string;
  domain_display_name: string;
  domain_icon: string;
  skills: string[];
  target_roles: string[];
}

interface ServiceAvailability {
  aggregation_state: string;
  core: string;
  leadhunter: string;
  startup_intelligence: string;
  is_partial_results: boolean;
}

const DISCIPLINES = [
  { id: "ALL", label: "🌐 All Disciplines" },
  { id: "SOFTWARE_ENGINEERING", label: "💻 Engineering & Tech" },
  { id: "MARKETING_GROWTH", label: "🚀 Marketing & Growth" },
  { id: "SALES_BD", label: "💼 Sales & Business Dev" },
  { id: "PRODUCT_DESIGN", label: "🎨 Product & Design" },
  { id: "FINANCE_ACCOUNTING", label: "📊 Finance & Accounting" },
  { id: "OPERATIONS_LOGISTICS", label: "⚙️ Operations & Logistics" },
  { id: "HR_TALENT", label: "👥 HR & Talent" },
  { id: "CUSTOMER_SUCCESS", label: "🤝 Customer Success" },
  { id: "DATA_ANALYTICS", label: "📈 Data & Analytics" },
  { id: "HEALTHCARE_MEDICAL", label: "🏥 Healthcare & Bio" },
  { id: "LEGAL_COMPLIANCE", label: "⚖️ Legal & Compliance" },
];

const BOOKMARK_CATEGORIES = [
  { id: "HIGH_PRIORITY", label: "🎯 High Priority Fit", color: "text-emerald-400 bg-emerald-950/80 border-emerald-800" },
  { id: "APPLY_SOON", label: "⚡ Apply This Week", color: "text-blue-400 bg-blue-950/80 border-blue-800" },
  { id: "STARTUP_SOLVE", label: "💡 Startup Solution", color: "text-purple-400 bg-purple-950/80 border-purple-800" },
  { id: "OUTREACH_LEAD", label: "🤝 Direct Outreach", color: "text-amber-400 bg-amber-950/80 border-amber-800" },
  { id: "RESEARCHING", label: "📁 Researching / Under Review", color: "text-slate-400 bg-slate-800 border-slate-700" },
];

export default function UnifiedOpportunitiesPage() {
  const [opportunities, setOpportunities] = useState<OpportunityEnvelope[]>(() => {
    const cached = fastCache.get<OpportunityEnvelope[]>("opps_ALL_ALL_BEST_FIT_All_0_");
    if (cached && cached.length > 0 && !cached.some((o) => o.opportunity_type === "FREELANCE" || o.opportunity_type === "STARTUP_PAIN_POINT")) {
      fastCache.delete("opps_ALL_ALL_BEST_FIT_All_0_");
      return [];
    }
    return cached || [];
  });
  const [counts, setCounts] = useState<CountsByType | null>(() => {
    const cached = fastCache.get<CountsByType>("opps_counts");
    if (cached && (cached.freelance === 0 || cached.startup_pain_points === 0)) {
      fastCache.delete("opps_counts");
      return null;
    }
    return cached || null;
  });
  const [candidatePersona, setCandidatePersona] = useState<CandidatePersona | null>(() => {
    return fastCache.get<CandidatePersona>("opps_persona") || null;
  });
  const [availability, setAvailability] = useState<ServiceAvailability | null>(null);
  const [loading, setLoading] = useState(() => {
    return (fastCache.get<OpportunityEnvelope[]>("opps_ALL_ALL_BEST_FIT_All_0_") || []).length === 0;
  });
  const [isFiltering, setIsFiltering] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [activeType, setActiveType] = useState<string>("ALL");
  const [selectedDiscipline, setSelectedDiscipline] = useState<string>("ALL");
  const [sortBy, setSortBy] = useState<string>("BEST_FIT");
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [minScore, setMinScore] = useState<number>(0);
  const [selectedEmploymentType, setSelectedEmploymentType] = useState<string>("ALL");

  // Refresh & Notifications
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [lastRefreshedAt, setLastRefreshedAt] = useState<string>("Just now");
  const [refreshNotification, setRefreshNotification] = useState<string | null>(null);
  const [pendingNewItems, setPendingNewItems] = useState<OpportunityEnvelope[]>([]);

  // Bookmark Category Modal
  const [saveModalItem, setSaveModalItem] = useState<OpportunityEnvelope | null>(null);
  const [selectedSaveCat, setSelectedSaveCat] = useState("HIGH_PRIORITY");
  const [saveNotes, setSaveNotes] = useState("");
  const [savingId, setSavingId] = useState<string | null>(null);

  // Resume Tailoring Bullets State
  const [expandedBulletId, setExpandedBulletId] = useState<string | null>(null);
  const [expandedSkillsCards, setExpandedSkillsCards] = useState<Record<string, boolean>>({});

  const toggleSkillsExpanded = (id: string) => {
    setExpandedSkillsCards((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
  };
  const [copiedBulletId, setCopiedBulletId] = useState<string | null>(null);

  useEffect(() => {
    if (typeof window !== "undefined") {
      const saved = localStorage.getItem("rightfit_auto_refresh");
      if (saved !== null) {
        setAutoRefresh(saved === "true");
      }
    }
  }, []);

  const toggleAutoRefresh = () => {
    const nextVal = !autoRefresh;
    setAutoRefresh(nextVal);
    if (typeof window !== "undefined") {
      localStorage.setItem("rightfit_auto_refresh", String(nextVal));
    }
  };

  const fetchOpportunities = async (
    isBackground = false,
    triggerRefresh = false,
    overrideSearch?: string,
    overrideType?: string,
    overrideCategory?: string,
    overrideDiscipline?: string,
    overrideMinScore?: number,
    overrideEmploymentType?: string
  ) => {
    const effType = overrideType !== undefined ? overrideType : activeType;
    const effDiscipline = overrideDiscipline !== undefined ? overrideDiscipline : selectedDiscipline;
    const effCategory = overrideCategory !== undefined ? overrideCategory : selectedCategory;
    const effMinScore = overrideMinScore !== undefined ? overrideMinScore : minScore;
    const effSearch = overrideSearch !== undefined ? overrideSearch : searchTerm;
    const effEmploymentType = overrideEmploymentType !== undefined ? overrideEmploymentType : selectedEmploymentType;

    const cacheKey = `opps_${effType}_${effDiscipline}_${sortBy}_${effCategory}_${effMinScore}_${effEmploymentType}_${effSearch.trim()}`;

    // Fast-path: Check fastCache for instantaneous zero-latency tab/filter swap
    if (!triggerRefresh && !isBackground) {
      const cached = fastCache.get<OpportunityEnvelope[]>(cacheKey);
      if (cached && cached.length > 0) {
        setOpportunities(cached);
        setLoading(false);
        setIsFiltering(false);
      } else if (opportunities.length > 0) {
        setIsFiltering(true);
      } else {
        setLoading(true);
      }
    } else if (isBackground) {
      setIsRefreshing(true);
    }

    setError(null);
    try {
      const params = new URLSearchParams();
      if (effType !== "ALL") params.append("type", effType);
      if (effDiscipline !== "ALL") params.append("discipline", effDiscipline);
      if (sortBy) params.append("sort_by", sortBy);
      if (triggerRefresh) params.append("refresh", "true");
      if (effSearch.trim()) params.append("search", effSearch.trim());
      if (effCategory !== "All") params.append("category", effCategory);
      if (effMinScore > 0) params.append("min_score", effMinScore.toString());
      if (effEmploymentType && effEmploymentType !== "ALL" && effType === "JOB") {
        params.append("employment_type", effEmploymentType);
      }
      params.append("per_page", "50");

      const res: any = await apiClient.get(`/opportunities/all?${params.toString()}`);
      const fetched: OpportunityEnvelope[] = res.data || [];

      // Save to fast cache
      fastCache.set(cacheKey, fetched, 120000);
      if (res.counts_by_type) fastCache.set("opps_counts", res.counts_by_type, 120000);
      if (res.candidate_persona) fastCache.set("opps_persona", res.candidate_persona, 120000);

      if (isBackground && opportunities.length > 0) {
        const currentIds = new Set(opportunities.map((o) => o.opportunity_id));
        const newOnes = fetched.filter((o) => !currentIds.has(o.opportunity_id));
        if (newOnes.length > 0) {
          setPendingNewItems(newOnes);
        }
      } else {
        setOpportunities(fetched);
        setPendingNewItems([]);
      }

      setCounts(res.counts_by_type || null);
      if (res.candidate_persona) {
        setCandidatePersona(res.candidate_persona);
      }
      setAvailability(res.service_availability || null);
      setLastRefreshedAt(new Date().toLocaleTimeString());
    } catch (err: any) {
      if (!isBackground) setError(err?.message || "Failed to load opportunities.");
    } finally {
      setLoading(false);
      setIsFiltering(false);
      setIsRefreshing(false);
    }
  };

  const applyPendingNewItems = () => {
    setOpportunities((prev) => [...pendingNewItems, ...prev]);
    setPendingNewItems([]);
  };

  useEffect(() => {
    fetchOpportunities(false);
  }, [activeType, selectedDiscipline, sortBy, selectedCategory, minScore, selectedEmploymentType]);

  // Background Auto-Refresh Poller (Selective & Throttled to 45s, runs only when tab is visible)
  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(() => {
      if (typeof document !== "undefined" && document.visibilityState === "visible") {
        fetchOpportunities(true);
      }
    }, 45000);
    return () => clearInterval(interval);
  }, [autoRefresh, activeType, selectedDiscipline, sortBy, selectedCategory, minScore, selectedEmploymentType]);

  const handleManualRefresh = async () => {
    setIsRefreshing(true);
    try {
      const res: any = await apiClient.post("/opportunities/refresh");
      await fetchOpportunities(false, true);
      setRefreshNotification(res.message || "Fresh market opportunities discovered & synced in real-time!");
      setTimeout(() => setRefreshNotification(null), 5000);
    } catch {
      await fetchOpportunities(false, true);
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleSearchSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    fetchOpportunities(false, false, searchTerm.trim());
  };

  const handleOpenSaveModal = (item: OpportunityEnvelope) => {
    if (item.is_saved) {
      handleDirectUnsave(item);
    } else {
      setSaveModalItem(item);
      setSelectedSaveCat(item.opportunity_type === "STARTUP_PAIN_POINT" ? "STARTUP_SOLVE" : "HIGH_PRIORITY");
      setSaveNotes("");
    }
  };

  const handleDirectUnsave = async (item: OpportunityEnvelope) => {
    setSavingId(item.opportunity_id);
    try {
      await apiClient.delete(`/opportunities/${item.opportunity_type}/${item.opportunity_id}/save`);
      item.is_saved = false;
      setOpportunities([...opportunities]);
    } catch (err: any) {
      alert(err?.message || "Failed to remove bookmark.");
    } finally {
      setSavingId(null);
    }
  };

  const handleConfirmSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!saveModalItem) return;
    setSavingId(saveModalItem.opportunity_id);
    try {
      await apiClient.post(
        `/opportunities/${saveModalItem.opportunity_type}/${saveModalItem.opportunity_id}/save`,
        {
          notes: saveNotes.trim() || undefined,
          category: selectedSaveCat,
        }
      );
      saveModalItem.is_saved = true;
      setOpportunities([...opportunities]);
      setSaveModalItem(null);
    } catch (err: any) {
      alert(err?.message || "Failed to save opportunity.");
    } finally {
      setSavingId(null);
    }
  };



  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6 animate-fade-in">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-black tracking-tight text-slate-900 sm:text-4xl">
              Live Opportunities Feed
            </h1>
            <span className="text-xs bg-indigo-950 text-indigo-400 font-mono px-2 py-0.5 rounded border border-indigo-800">
              Universal Multi-Domain v2.0
            </span>
          </div>
          <p className="mt-2 text-sm text-slate-400">
            Real-time verified jobs, freelance contracts, and startup bottlenecks dynamically calibrated to your resume.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            href="/dashboard"
            className="inline-flex items-center px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-sm font-semibold text-slate-200 border border-slate-700 transition-colors"
          >
            ← Back to Dashboard
          </Link>
          <Link
            href="/saved-opportunities"
            className="inline-flex items-center px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-sm font-semibold text-white shadow-sm transition-colors"
          >
            Saved Bookmarks ★
          </Link>
        </div>
      </div>

      {/* Candidate Profile Calibration Header Banner */}
      {candidatePersona && candidatePersona.has_profile && (
        <div className="neo-box p-5 rounded-2xl border border-white/90 shadow-md text-slate-900">
          <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
            <div className="space-y-1.5">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-xl">{candidatePersona.domain_icon || "🎯"}</span>
                <h2 className="text-sm font-black tracking-tight text-slate-900">
                  Feed Calibrated to Your Resume:
                </h2>
                <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-indigo-500/25 border border-indigo-400 text-indigo-200">
                  {candidatePersona.domain_display_name}
                </span>
                <span className="text-[11px] text-emerald-400 font-medium bg-emerald-950/60 border border-emerald-800 px-2 py-0.5 rounded-full">
                  ✓ Resume Active
                </span>
              </div>
              <p className="text-xs text-slate-700 font-semibold">
                Opportunities and startup pain points are ranked by direct synergy with your extracted competencies.
              </p>
              {candidatePersona.skills && candidatePersona.skills.length > 0 && (
                <div className="flex flex-wrap items-center gap-1.5 pt-1">
                  <span className="text-[11px] text-slate-400">Your Skills:</span>
                  {candidatePersona.skills.map((skill: string) => (
                    <span
                      key={skill}
                      className="neo-inset text-[11px] px-2.5 py-0.5 rounded-full text-indigo-800 font-mono font-bold"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              )}
            </div>

            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1.5 neo-pill px-3 py-1.5 rounded-xl border border-white/90">
                <span className="text-xs text-slate-400">Sort:</span>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="bg-transparent text-xs text-slate-900 font-bold focus:outline-none cursor-pointer"
                >
                  <option value="BEST_FIT" className="bg-slate-900 text-white">🎯 Best Fit (Skills + Live Opportunities)</option>
                  <option value="NEWEST" className="bg-slate-900 text-white">⏱️ Newest First</option>
                  <option value="URGENCY" className="bg-slate-900 text-white">🔥 Highest Urgency & Trust</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Live Refresh Toast Notification */}
      {refreshNotification && (
        <div className="p-3.5 rounded-xl bg-emerald-950/90 border border-emerald-700 text-emerald-200 text-xs flex items-center justify-between shadow-lg">
          <div className="flex items-center gap-2">
            <span>✨</span>
            <span className="font-medium">{refreshNotification}</span>
          </div>
          <button
            onClick={() => setRefreshNotification(null)}
            className="text-emerald-400 hover:text-white"
          >
            ✕
          </button>
        </div>
      )}

      {/* Live Auto-Refresh & Controls Bar */}
      <div className="neo-box flex flex-wrap items-center justify-between gap-4 p-4 rounded-2xl text-xs font-bold text-slate-800 border border-white/90">
        <div className="flex items-center gap-3 flex-wrap">
          <button
            onClick={toggleAutoRefresh}
            className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-lg font-semibold transition-colors border ${autoRefresh
              ? "bg-emerald-950/60 border-emerald-800 text-emerald-400"
              : "neo-pill text-slate-800 font-bold"
              }`}
          >
            <span className={`w-2 h-2 rounded-full ${autoRefresh ? "bg-emerald-400 animate-pulse" : "bg-slate-500"}`} />
            Auto-Sync: {autoRefresh ? "LIVE (25s)" : "PAUSED"}
          </button>

          <span className="text-slate-700 font-bold">

            Last synced: <span className="text-slate-900 font-mono font-extrabold">{lastRefreshedAt}</span>
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleManualRefresh}
            disabled={isRefreshing}
            className="neo-btn-primary inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold transition-all shadow-md disabled:opacity-50"
            title="Scan market sources for new job requisitions and startup pain points"
          >
            <span className={isRefreshing ? "animate-spin" : ""}>⟳</span>
            {isRefreshing ? "Scanning Market..." : "Refresh Live Opportunities"}
          </button>
        </div>
      </div>

      {/* Pending New Items Banner */}
      {pendingNewItems.length > 0 && (
        <div className="p-4 rounded-xl bg-indigo-950/80 border border-indigo-700/80 text-white flex items-center justify-between shadow-lg">
          <div className="flex items-center gap-2 text-sm font-semibold">
            <span>✨</span>
            <span>{pendingNewItems.length} fresh opportunities discovered across market feeds!</span>
          </div>
          <button
            onClick={applyPendingNewItems}
            className="px-4 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-xs font-bold transition-colors shadow"
          >
            Load New Opportunities
          </button>
        </div>
      )}


      {/* Type Switcher Tabs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 border-b border-slate-800 pb-4">
        {[
          {
            id: "ALL",
            label: "All Opportunities",
            count: counts?.total,
            icon: "🌐",
            subBadge: "Reconciled Live Stream",
          },
          {
            id: "JOB",
            label: "Job Openings",
            count: counts?.jobs,
            icon: "💼",
            subBadge: counts?.jobs_breakdown
              ? `${counts.jobs_breakdown.full_time} Full-Time · ${counts.jobs_breakdown.internship} Intern · ${counts.jobs_breakdown.contract} Contract`
              : "Full-Time · Internships · Contract Roles",
          },
          {
            id: "FREELANCE",
            label: "Freelance Leads",
            count: counts?.freelance,
            icon: "🚀",
            subBadge: "Web, SEO & Tech Upgrades",
          },
          {
            id: "STARTUP_PAIN_POINT",
            label: "Startup Pain Points",
            count: counts?.startup_pain_points,
            icon: "💡",
            subBadge: "Founder Problems & AI Solves",
          },
        ].map((tab) => {
          const isActive = activeType === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => {
                setActiveType(tab.id);
                setSelectedEmploymentType("ALL");
                fetchOpportunities(false, false, undefined, tab.id, undefined, undefined, undefined, "ALL");
              }}
              className={`p-3.5 rounded-xl text-left transition-all flex flex-col justify-between gap-1.5 border cursor-pointer ${
                isActive
                  ? "bg-indigo-600 text-white border-indigo-500 shadow-md shadow-indigo-600/30"
                  : "neo-pill text-slate-900 hover:text-indigo-600 font-bold"
              }`}
            >
              <div className="flex items-center justify-between w-full">
                <span className="font-bold text-sm flex items-center gap-1.5">
                  <span>{tab.icon}</span>
                  <span>{tab.label}</span>
                </span>
                {tab.count !== undefined && (
                  <span
                    className={`text-xs px-2 py-0.5 rounded-full font-mono font-bold ${
                      isActive ? "bg-indigo-950 text-indigo-200 border border-indigo-700" : "neo-pill text-slate-800 font-bold"
                    }`}
                  >
                    {tab.count}
                  </span>
                )}
              </div>
              <span
                className={`text-[11px] truncate w-full ${
                  isActive ? "text-indigo-200 font-medium" : "text-slate-400"
                }`}
              >
                {tab.subBadge}
              </span>
            </button>
          );
        })}
      </div>

      {/* Active View Context Banner & Sub-Filters (Explicitly specifies active view & sub-filters) */}
      <div className="p-4 rounded-2xl neo-box border border-white/90 shadow-sm space-y-3">
        {activeType === "ALL" && (
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <h2 className="text-sm font-bold text-white flex items-center gap-2">
                <span>🌐</span> Active View: All Opportunities ({counts?.total || opportunities.length} Signals)
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Reconciled real-time opportunities across verified company job portals, freelance projects, and startup intelligence.
              </p>
            </div>
            <div className="flex items-center gap-1.5 flex-wrap text-xs">
              <span className="px-2.5 py-1 rounded-lg bg-blue-950/70 border border-blue-800 text-blue-300 font-mono">
                💼 {counts?.jobs ?? opportunities.length} Jobs
              </span>
              <span className="px-2.5 py-1 rounded-lg bg-emerald-950/70 border border-emerald-800 text-emerald-300 font-mono">
                ⚡ {counts?.freelance ?? opportunities.length} Freelance
              </span>
              <span className="px-2.5 py-1 rounded-lg bg-purple-950/70 border border-purple-800 text-purple-300 font-mono">
                💡 {counts?.startup_pain_points ?? opportunities.length} Startups
              </span>
            </div>
          </div>
        )}

        {activeType === "JOB" && (
          <div className="space-y-3">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 border-b border-slate-800/80">
              <div>
                <h2 className="text-sm font-bold text-white flex items-center gap-2">
                  <span>💼</span> Active View: Direct Job Openings ({counts?.jobs ?? opportunities.length} Positions)
                </h2>
                <p className="text-xs text-slate-400 mt-0.5">
                  Verified listings from company career portals. Select an employment arrangement below:
                </p>
              </div>
            </div>

            {/* Employment Type Sub-Filter Buttons */}
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs text-slate-400 font-medium mr-1">Employment Type:</span>
              {[
                { id: "ALL", label: "⚡ All Jobs", count: counts?.jobs ?? opportunities.length },
                { id: "FULL_TIME", label: "💼 Full-Time Only", count: counts?.jobs_breakdown?.full_time ?? 0 },
                { id: "INTERNSHIP", label: "🎓 Internships", count: counts?.jobs_breakdown?.internship ?? 0 },
                { id: "CONTRACT", label: "📄 Contract Roles", count: counts?.jobs_breakdown?.contract ?? 0 },
              ].map((et) => {
                const isSelected = selectedEmploymentType === et.id;
                return (
                  <button
                    key={et.id}
                    onClick={() => {
                      setSelectedEmploymentType(et.id);
                      fetchOpportunities(false, false, undefined, "JOB", undefined, undefined, undefined, et.id);
                    }}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors flex items-center gap-1.5 cursor-pointer ${
                      isSelected
                        ? "bg-indigo-600 text-white shadow-sm"
                        : "neo-pill text-slate-900 hover:text-indigo-600 font-bold"
                    }`}
                  >
                    <span>{et.label}</span>
                    <span className={`text-[10px] px-1.5 py-0.2 rounded-full font-mono ${
                      isSelected ? "bg-indigo-900 text-indigo-100" : "bg-slate-900 text-slate-400"
                    }`}>
                      {et.count}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {activeType === "FREELANCE" && (
          <div className="space-y-3">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 border-b border-slate-800/80">
              <div>
                <h2 className="text-sm font-bold text-white flex items-center gap-2">
                  <span>🚀</span> Active View: High-Value Freelance Leads ({counts?.freelance ?? opportunities.length} Discovered Leads)
                </h2>
                <p className="text-xs text-slate-400 mt-0.5">
                  Direct client contracts with verified contact channels, business phone numbers, and web infrastructure audits:
                </p>
              </div>
            </div>

            {/* Quick Service Sub-Filter Buttons */}
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs text-slate-400 font-medium mr-1">Service Need:</span>
              {[
                { id: "All", label: "All Freelance Leads" },
                { id: "Modern Responsive Web Rebuild", label: "Modern Web Rebuild" },
                { id: "SEO & Google Search Discovery", label: "SEO & Search Visibility" },
                { id: "Website & Digital Infrastructure", label: "Tech Infrastructure" },
              ].map((cat) => {
                const isSelected = selectedCategory === cat.id;
                return (
                  <button
                    key={cat.id}
                    onClick={() => {
                      setSelectedCategory(cat.id);
                      fetchOpportunities(false, false, undefined, "FREELANCE", cat.id);
                    }}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors cursor-pointer ${
                      isSelected
                        ? "bg-emerald-600 text-white shadow-sm"
                        : "neo-pill text-slate-900 hover:text-indigo-600 font-bold"
                    }`}
                  >
                    {cat.label}
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {activeType === "STARTUP_PAIN_POINT" && (
          <div className="space-y-3">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 border-b border-slate-800/80">
              <div>
                <h2 className="text-sm font-bold text-white flex items-center gap-2">
                  <span>💡</span> Active View: Startup Pain Points & Bottlenecks ({counts?.startup_pain_points ?? opportunities.length} Signals)
                </h2>
                <p className="text-xs text-slate-400 mt-0.5">
                  Verified startup friction points synthesized with Gemini AI root cause analysis, actionable solve plans, and direct founder outreach:
                </p>
              </div>
            </div>

            {/* Urgency Sub-Filters */}
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs text-slate-400 font-medium mr-1">Urgency Score:</span>
              {[
                { score: 0, label: "All Pain Points" },
                { score: 8, label: "🔥 Critical Urgency (Score ≥ 8)" },
                { score: 7, label: "⚡ High Urgency (Score ≥ 7)" },
                { score: 6, label: "Moderate Friction (Score ≥ 6)" },
              ].map((urg) => {
                const isSelected = minScore === urg.score;
                return (
                  <button
                    key={urg.score}
                    onClick={() => {
                      setMinScore(urg.score);
                      fetchOpportunities(false, false, undefined, "STARTUP_PAIN_POINT", undefined, undefined, urg.score);
                    }}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors cursor-pointer ${
                      isSelected
                        ? "bg-purple-600 text-white shadow-sm"
                        : "neo-pill text-slate-900 hover:text-indigo-600 font-bold"
                    }`}
                  >
                    {urg.label}
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Universal Multi-Domain & Filters Form */}
      <div className="space-y-3">
        <form
          onSubmit={handleSearchSubmit}
          className="grid grid-cols-1 md:grid-cols-12 gap-3 p-4 rounded-2xl neo-box border border-white/90 shadow-sm text-xs"
        >
          {/* Search */}
          <div className="md:col-span-5">
            <input
              type="text"
              placeholder="Search roles, skills (e.g. React, WebDev), companies, or problems..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleSearchSubmit(e);
              }}
              className="w-full neo-inset rounded-xl px-3.5 py-2.5 text-sm text-slate-900 font-bold focus:outline-none"
            />
          </div>

          {/* Universal Discipline Filter */}
          <div className="md:col-span-4">
            <select
              value={selectedDiscipline}
              onChange={(e) => {
                const val = e.target.value;
                setSelectedDiscipline(val);
                fetchOpportunities(false, false, searchTerm.trim(), activeType, selectedCategory, val, minScore, selectedEmploymentType);
              }}
              className="w-full neo-inset rounded-xl px-3.5 py-2.5 text-sm text-slate-900 font-bold focus:outline-none cursor-pointer"
            >
              {DISCIPLINES.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.label}
                </option>
              ))}
            </select>
          </div>

          {/* Submit & Reset */}
          <div className="md:col-span-3 flex gap-2">
            <button
              type="submit"
              className="flex-1 px-4 py-2.5 rounded-xl neo-btn-primary text-sm font-bold text-white shadow-md transition-all cursor-pointer hover:shadow-lg"
            >
              Search
            </button>
            <button
              type="button"
              onClick={() => {
                setSearchTerm("");
                setSelectedDiscipline("ALL");
                setSelectedCategory("All");
                setMinScore(0);
                setSelectedEmploymentType("ALL");
                fetchOpportunities(false, false, "", activeType, "All", "ALL", 0, "ALL");
              }}
              className="px-4 py-2.5 rounded-xl neo-pill text-sm font-bold text-slate-800 hover:text-indigo-600 transition-all cursor-pointer"
            >
              Reset
            </button>
          </div>
        </form>
      </div>

      {error && (
        <div className="p-4 rounded-xl neo-box border border-red-300 text-sm font-bold text-red-900 shadow-sm">
          {error}
        </div>
      )}

      {/* Top Background Revalidation Glow Bar */}
      {(isFiltering || isRefreshing) && (
        <div className="fixed top-0 left-0 right-0 h-[3px] bg-gradient-to-r from-indigo-500 via-purple-500 to-emerald-400 animate-pulse z-50 shadow-sm" />
      )}

      {/* Pipeline Grid */}
      {loading && opportunities.length === 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-pulse">
          {[...Array(9)].map((_, i) => (
            <div key={i} className="h-72 rounded-2xl neo-card border border-white/90 shadow-sm" />
          ))}
        </div>
      ) : opportunities.length === 0 ? (
        <div className="text-center py-12 px-6 neo-box rounded-2xl border border-white/90 shadow-sm space-y-4">
          <div className="w-12 h-12 mx-auto rounded-full neo-pill flex items-center justify-center text-indigo-600 font-bold text-xl">
            🔍
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900">No opportunities match your search</h3>
            <p className="text-xs text-slate-700 font-bold mt-1">
              {searchTerm ? `No results found for "${searchTerm}".` : "Try selecting 'All Disciplines' or resetting search filters."}
            </p>
          </div>
          <div className="pt-2 flex items-center justify-center gap-3">
            <button
              onClick={() => {
                setSearchTerm("");
                setSelectedDiscipline("ALL");
                setSelectedCategory("All");
                setMinScore(0);
                setSelectedEmploymentType("ALL");
                fetchOpportunities(false, false, "", activeType, "All", "ALL", 0, "ALL");
              }}
              className="px-4 py-2 rounded-xl neo-pill text-xs font-bold text-indigo-900 hover:text-indigo-600 transition-all cursor-pointer"
            >
              Reset Filters
            </button>
            <button
              onClick={handleManualRefresh}
              className="px-4 py-2 rounded-xl neo-btn-primary text-xs font-bold text-white shadow transition-all cursor-pointer"
            >
              Scan & Refresh Market
            </button>
          </div>
        </div>
      ) : (
        <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 transition-opacity duration-150 ${isFiltering || isRefreshing ? "opacity-80" : "opacity-100"}`}>
          {opportunities.map((item) => {
            const isJob = item.opportunity_type === "JOB";
            const isFreelance = item.opportunity_type === "FREELANCE";
            const isStartup = item.opportunity_type === "STARTUP_PAIN_POINT";

            const empType = item.type_specific_payload?.employment_type;
            const badgeColor = isJob
              ? empType === "INTERNSHIP"
                ? "bg-amber-950 text-amber-300 border-amber-800"
                : empType === "CONTRACT"
                  ? "bg-cyan-950 text-cyan-300 border-cyan-800"
                  : "bg-blue-950 text-blue-300 border-blue-800"
              : isFreelance
                ? "bg-emerald-950 text-emerald-300 border-emerald-800"
                : "bg-purple-950 text-purple-300 border-purple-800";

            const badgeText = isJob
              ? empType === "INTERNSHIP"
                ? "🎓 Internship"
                : empType === "CONTRACT"
                  ? "📄 Contract Role"
                  : "💼 Full-Time Job"
              : isFreelance
                ? "⚡ Freelance Client Lead"
                : "💡 Startup Pain Point";

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
                className="p-5 rounded-2xl neo-card neo-box-hover flex flex-col justify-between transition-all space-y-4"
              >
                <div className="space-y-3">
                  {/* Top Badges & Domain Pill */}
                  <div className="flex items-center justify-between gap-2 flex-wrap">
                    <div className="flex items-center gap-1.5 flex-wrap">
                      <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded border ${badgeColor}`}>
                        {badgeText}
                      </span>
                      {item.domain_display_name && (
                        <span className="text-[10px] font-medium px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 flex items-center gap-1">
                          <span>{item.domain_icon || "🌐"}</span>
                          <span>{item.domain_display_name}</span>
                        </span>
                      )}
                      {item.is_new_signal && (
                        <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-700 animate-pulse">
                          ✨ NEW
                        </span>
                      )}
                    </div>
                    <span className="text-xs text-slate-400 truncate max-w-[140px]">
                      {item.source_name}
                    </span>
                  </div>

                  {/* Title & Organization */}
                  <div>
                    <h3 className="text-base font-black text-slate-900 line-clamp-2 hover:text-indigo-600 transition-colors">
                      {item.title}
                    </h3>
                    <div className="text-xs font-medium text-indigo-400 mt-1">
                      {item.organization_name}
                      {item.location && <span className="text-slate-400"> • {item.location}</span>}
                    </div>
                  </div>

                  {/* Description preview */}
                  <p className="text-xs text-slate-300 line-clamp-2 leading-relaxed">
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
                                <span className="text-[11px] font-bold text-amber-800">Add to Resume:</span>
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

                  {/* Dynamic Candidate Fit & "Why You Fit" Section */}
                  {fit && (
                    <div className="p-3.5 rounded-xl neo-inset space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-black text-slate-900 flex items-center gap-1.5">
                          <span
                            className={`w-2 h-2 rounded-full ${fit.fit_percentage >= 80
                              ? "bg-emerald-400"
                              : fit.fit_percentage >= 65
                                ? "bg-blue-400"
                                : "bg-amber-400"
                              }`}
                          />
                          Fit: {fit.fit_percentage}% ({fit.fit_rating})
                        </span>
                        <span className="text-[10px] text-indigo-700 font-mono font-bold">
                          Verified Synergy
                        </span>
                      </div>

                      <p className="text-xs text-slate-700 leading-relaxed font-medium">
                        {fit.how_you_fit}
                      </p>

                      {/* Tailored Resume Bullets & Action Plan */}
                      {fit.tailored_resume_bullets && fit.tailored_resume_bullets.length > 0 && (
                        <div className="pt-2 border-t border-slate-200">
                          <button
                            type="button"
                            onClick={() =>
                              setExpandedBulletId(
                                expandedBulletId === item.opportunity_id ? null : item.opportunity_id
                              )
                            }
                            className="text-[11px] font-bold text-indigo-700 hover:text-indigo-900 flex items-center justify-between w-full transition-colors"
                          >
                            <span className="flex items-center gap-1.5">
                              <span>📝</span>
                              <span>Tailor Resume for this Role</span>
                              {fit.resume_action_plan?.ats_boost_percentage ? (
                                <span className="text-[10px] px-2 py-0.5 rounded-lg bg-indigo-100 text-indigo-900 border border-indigo-300 font-mono font-bold">
                                  +{fit.resume_action_plan.ats_boost_percentage}% ATS Boost
                                </span>
                              ) : null}
                            </span>
                            <span className="text-[10px] text-slate-600 font-bold">
                              {expandedBulletId === item.opportunity_id ? "▲ Close" : "▼ Show Recommended Bullets"}
                            </span>
                          </button>

                          {expandedBulletId === item.opportunity_id && (
                            <div className="mt-2 space-y-2 p-3 rounded-xl neo-inset border border-slate-200 text-xs animate-in fade-in duration-150">
                              <p className="text-[11px] font-bold text-slate-700">
                                Copy & paste these recommended bullets into your resume to match hiring requirements:
                              </p>
                              {fit.tailored_resume_bullets.map((b, bIdx) => (
                                <div key={bIdx} className="space-y-1.5 bg-white/80 p-2.5 rounded-xl border border-slate-200 shadow-sm">
                                  <div className="flex items-center justify-between">
                                    <span className="text-[10px] font-bold text-amber-800">
                                      Target Skill: {b.skill}
                                    </span>
                                    <button
                                      type="button"
                                      onClick={() => {
                                        navigator.clipboard.writeText(b.sample_bullet);
                                        setCopiedBulletId(`${item.opportunity_id}-${bIdx}`);
                                        setTimeout(() => setCopiedBulletId(null), 2500);
                                      }}
                                      className="text-[10px] px-2.5 py-1 rounded-lg neo-pill text-indigo-700 hover:text-indigo-900 font-bold border border-indigo-200 transition-all cursor-pointer"
                                    >
                                      {copiedBulletId === `${item.opportunity_id}-${bIdx}` ? "✓ Copied!" : "📋 Copy Bullet"}
                                    </button>
                                  </div>
                                  <p className="text-[11px] text-slate-700 italic font-medium leading-relaxed">
                                    &quot;{b.sample_bullet}&quot;
                                  </p>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Type-Specific Discriminator Payload */}
                  <div className="pt-2 border-t border-slate-800/80 text-xs text-slate-300 space-y-1">
                    {isJob && (
                      <div className="flex flex-wrap items-center gap-2 font-mono">
                        {item.type_specific_payload.salary_min && (
                          <span className="bg-slate-800 px-2 py-0.5 rounded text-blue-300">
                            ${item.type_specific_payload.salary_min.toLocaleString()} - ${item.type_specific_payload.salary_max?.toLocaleString()}
                          </span>
                        )}
                        <span className="bg-slate-800 px-2 py-0.5 rounded text-slate-400">
                          {item.type_specific_payload.employment_type}
                        </span>
                      </div>
                    )}

                    {isFreelance && (
                      <div className="space-y-2">
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-emerald-400 font-medium">
                            Category: {item.type_specific_payload.service_category || "Web Modernization"}
                          </span>
                          {item.type_specific_payload.rating > 0 && (
                            <span className="text-slate-400">
                              ★ {item.type_specific_payload.rating} ({item.type_specific_payload.reviews_count || 0} reviews)
                            </span>
                          )}
                        </div>
                        {/* Discovered Outreach Channels & Web Health */}
                        <div className="flex flex-wrap items-center gap-1.5 text-[11px] pt-0.5">
                          {item.type_specific_payload.is_broken_website && (
                            <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-rose-950/80 text-rose-300 border border-rose-800 font-medium">
                              ⚠️ Broken / Outdated Site
                            </span>
                          )}
                          {!item.type_specific_payload.website && !item.type_specific_payload.is_broken_website && (
                            <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-amber-950/70 text-amber-300 border border-amber-800 font-medium">
                              ⚠️ No Business Website (Opportunity)
                            </span>
                          )}
                          {item.type_specific_payload.email && (
                            <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-emerald-950/80 text-emerald-300 border border-emerald-800 font-mono">
                              ✉ {item.type_specific_payload.email}
                            </span>
                          )}
                          {item.type_specific_payload.phone && (
                            <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-blue-950/80 text-blue-300 border border-blue-800 font-mono">
                              📞 {item.type_specific_payload.phone}
                            </span>
                          )}
                        </div>
                      </div>
                    )}

                    {isStartup && (
                      <div className="space-y-2">
                        <div className="flex items-center justify-between text-xs font-mono">
                          <span className="text-purple-300 font-semibold">
                            Urgency: {item.type_specific_payload.urgency_score}/10
                          </span>
                          <span className="text-slate-400">
                            {item.type_specific_payload.corroboration_count} Verified Source{item.type_specific_payload.corroboration_count > 1 ? "s" : ""}
                          </span>
                        </div>

                        {/* Problem & Solution Highlights */}
                        {item.type_specific_payload.problem_explanation && (
                          <div className="p-2 rounded-lg bg-slate-950 border border-rose-900/40 text-[11px] leading-snug">
                            <span className="text-rose-400 font-semibold flex items-center gap-1 mb-0.5">
                              <span>🚨</span> Problem Root Cause:
                            </span>
                            <p className="line-clamp-2 text-slate-300 font-sans">{item.type_specific_payload.problem_explanation}</p>
                          </div>
                        )}

                        {item.type_specific_payload.how_to_solve_strategy && (
                          <div className="p-2 rounded-lg bg-indigo-950/40 border border-emerald-900/40 text-[11px] leading-snug">
                            <span className="text-emerald-400 font-semibold flex items-center gap-1 mb-0.5">
                              <span>🛠️</span> Action Plan:
                            </span>
                            <p className="line-clamp-2 text-slate-300 font-sans">{item.type_specific_payload.how_to_solve_strategy}</p>
                          </div>
                        )}

                        {/* Founder Social Channels */}
                        {(() => {
                          const c = (item as any).contact_info || item.type_specific_payload || {};
                          const email = c.email || item.type_specific_payload.contact_email;
                          const twitter = c.twitter || item.type_specific_payload.twitter_url;
                          const linkedin = c.linkedin || item.type_specific_payload.linkedin_url;
                          const github = c.github || item.type_specific_payload.github_url;
                          if (!email && !twitter && !linkedin && !github) return null;
                          return (
                            <div className="flex flex-wrap items-center gap-1.5 pt-1 text-[10px]">
                              <span className="text-slate-500 font-semibold uppercase mr-0.5">Contacts:</span>
                              {linkedin && (
                                <a
                                  href={linkedin}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="px-1.5 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800 hover:bg-blue-900 transition-colors"
                                >
                                  💼 LinkedIn
                                </a>
                              )}
                              {twitter && (
                                <a
                                  href={twitter}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="px-1.5 py-0.5 rounded bg-slate-950 text-sky-300 border border-sky-800 hover:bg-slate-800 transition-colors"
                                >
                                  𝕏 Twitter
                                </a>
                              )}
                              {github && (
                                <a
                                  href={github}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="px-1.5 py-0.5 rounded bg-slate-950 text-slate-200 border border-slate-700 hover:bg-slate-800 transition-colors"
                                >
                                  🐙 GitHub
                                </a>
                              )}
                              {email && (
                                <a
                                  href={`mailto:${email}`}
                                  className="px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800 hover:bg-emerald-900 transition-colors"
                                >
                                  ✉ Email
                                </a>
                              )}
                            </div>
                          );
                        })()}
                      </div>
                    )}

                    {/* Live Trust & Verification Indicator */}
                    {item.trust_metrics && (
                      <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between gap-1.5 flex-wrap text-[11px]">
                        <span className="inline-flex items-center gap-1 font-semibold text-emerald-400 bg-emerald-950/60 border border-emerald-800/80 px-2 py-0.5 rounded-full">
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                          {item.trust_metrics.trust_tier_label}
                        </span>
                        <span
                          className={`text-[10px] font-medium px-2 py-0.5 rounded border ${item.trust_metrics.ghost_job_risk.level === "LOW"
                            ? "text-emerald-300 bg-emerald-950/50 border-emerald-800/60"
                            : item.trust_metrics.ghost_job_risk.level === "MODERATE"
                              ? "text-amber-300 bg-amber-950/50 border-amber-800/60"
                              : "text-rose-300 bg-rose-950/50 border-rose-800/60"
                            }`}
                        >
                          {item.trust_metrics.ghost_job_risk.urgency_label}
                        </span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Card Footer: Formal Bookmark & Details Actions */}
                <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between gap-3 flex-wrap">
                  {/* Formal Bookmark / Saved Button */}
                  <button
                    type="button"
                    onClick={() => handleOpenSaveModal(item)}
                    disabled={savingId === item.opportunity_id}
                    className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold border transition-all cursor-pointer ${item.is_saved ? "bg-amber-100 border-amber-300 text-amber-900 shadow-sm" : "neo-pill text-slate-800 border-slate-200 hover:text-indigo-600"}`}
                    title={item.is_saved ? "Bookmarked in folder" : "Bookmark this opportunity"}
                  >
                    <svg
                      className={`w-3.5 h-3.5 ${item.is_saved ? "text-amber-400 fill-current" : "text-slate-400"}`}
                      fill={item.is_saved ? "currentColor" : "none"}
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"
                      />
                    </svg>
                    <span>{item.is_saved ? "★ Bookmarked" : "☆ Bookmark"}</span>
                  </button>

                  {/* Formal Navigation / Details Actions */}
                  <div className="flex items-center gap-2 flex-wrap">
                    {item.opportunity_type === "JOB" && (
                      <>
                        <Link
                          href={`/jobs/${item.opportunity_id}`}
                          className="inline-flex items-center gap-1 px-3 py-1.5 rounded-xl text-xs font-bold neo-pill text-indigo-900 hover:text-indigo-600 border border-indigo-200 transition-all"
                        >
                          View Details →
                        </Link>
                        {item.source_url ? (
                          <a
                            href={item.source_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white transition-colors shadow-sm"
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
                          className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white transition-colors shadow-sm"
                        >
                          Pitch Client & Lead Info →
                        </Link>
                        {item.source_url ? (
                          <a
                            href={item.source_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 px-3 py-1.5 rounded-xl text-xs font-bold neo-pill text-slate-900 hover:text-indigo-600 transition-all"
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
                          className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold bg-purple-600 hover:bg-purple-500 text-white transition-colors shadow-sm"
                        >
                          Solve Pain Point →
                        </Link>
                        {item.source_url ? (
                          <a
                            href={item.source_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 px-3 py-1.5 rounded-xl text-xs font-bold neo-pill text-slate-900 hover:text-indigo-600 transition-all"
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

      {/* Bookmark Categorization Modal */}
      {saveModalItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="w-full max-w-md rounded-2xl bg-slate-900 border border-slate-800 p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <span>★</span> Categorize Bookmark
              </h3>
              <button
                onClick={() => setSaveModalItem(null)}
                className="text-slate-400 hover:text-white text-sm"
              >
                ✕
              </button>
            </div>

            <p className="text-xs text-slate-300">
              Save <strong className="text-white">{saveModalItem.title}</strong> into your bookmarks & collections:
            </p>

            <form onSubmit={handleConfirmSave} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                  Select Folder / Category *
                </label>
                <div className="grid grid-cols-1 gap-2">
                  {BOOKMARK_CATEGORIES.map((cat) => (
                    <button
                      key={cat.id}
                      type="button"
                      onClick={() => setSelectedSaveCat(cat.id)}
                      className={`text-left px-3.5 py-2.5 rounded-lg border text-xs font-semibold transition-all flex items-center justify-between ${selectedSaveCat === cat.id
                        ? "bg-indigo-600 text-white border-indigo-400 shadow"
                        : "bg-slate-950 text-slate-300 border-slate-800 hover:border-slate-700"
                        }`}
                    >
                      <span>{cat.label}</span>
                      {selectedSaveCat === cat.id && <span>✓</span>}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Private Notes (Optional)
                </label>
                <textarea
                  value={saveNotes}
                  onChange={(e) => setSaveNotes(e.target.value)}
                  placeholder="e.g. Highlight CRM automation experience in intro pitch..."
                  rows={2}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setSaveModalItem(null)}
                  className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={savingId === saveModalItem.opportunity_id}
                  className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-xs font-semibold text-white shadow-sm"
                >
                  {savingId === saveModalItem.opportunity_id ? "Saving..." : "Save to Folder"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}


    </div>
  );
}
