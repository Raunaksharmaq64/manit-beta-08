"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { apiClient } from "@/services/apiClient";
import { fastCache } from "@/services/fastCache";
import { useAuth } from "@/context/AuthContext";

interface JobItem {
  id: string;
  title: string;
  company_name: string;
  city?: string;
  state?: string;
  country?: string;
  workplace_type: string;
  is_remote: boolean;
  employment_type: string;
  min_salary?: number;
  max_salary?: number;
  currency?: string;
  salary_period?: string;
  required_skills: string[];
  application_url: string;
  verification_status: string;
  freshness_state: string;
  first_seen_at: string;
  last_verified_at?: string;
  source_name: string;
  is_saved: boolean;
  saved_job_id?: string;
  skill_fit_score?: number;
  eligibility_status?: string;
  relevance_score?: number;
  matched_skills_preview: string[];
  missing_skills_preview: string[];
}

interface SourceCoverage {
  total_configured_sources: number;
  healthy_sources_count: number;
  degraded_sources_count: number;
  is_partial_results: boolean;
  coverage_details: Array<{
    source_key: string;
    display_name: string;
    status: string;
    records_count: number;
    outage_reason?: string;
  }>;
}

const POPULAR_SKILLS = [
  "React",
  "Python",
  "TypeScript",
  "Node.js",
  "Next.js",
  "FastAPI",
  "SQL",
  "PostgreSQL",
  "AWS",
  "Docker",
  "Kubernetes",
  "Figma",
  "UI/UX",
  "B2B Sales",
  "Growth Marketing",
  "SEO",
  "Content Strategy",
  "Financial Modeling",
  "Commercial Contracts",
  "Customer Success",
];

const POPULAR_COMPANIES = [
  "Cloudflare",
  "Perplexity AI",
  "Figma",
  "Palantir",
  "Stripe",
  "OpenAI",
  "Spotify",
  "Linear",
];

const QUICK_SEARCH_PILLS = [
  { label: "⚡ React", value: "react" },
  { label: "🌐 WebDev", value: "webdev" },
  { label: "💻 Full Stack", value: "full stack" },
  { label: "🐍 Python", value: "python" },
  { label: "🎨 Figma", value: "figma" },
  { label: "☁️ DevOps", value: "devops" },
  { label: "📈 B2B Sales", value: "sales" },
  { label: "📢 Marketing", value: "marketing" },
];

function SearchContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user } = useAuth();

  // Search filter states
  const [query, setQuery] = useState(searchParams.get("q") || "");
  const [role, setRole] = useState(searchParams.get("role") || "");
  const [company, setCompany] = useState(searchParams.get("company") || "");
  const [city, setCity] = useState(searchParams.get("city") || "");
  const [isRemoteOnly, setIsRemoteOnly] = useState(searchParams.get("remote") === "true");
  const [workplaceType, setWorkplaceType] = useState(searchParams.get("workplace") || "");
  const [employmentType, setEmploymentType] = useState(searchParams.get("employment") || "");
  const [experienceLevel, setExperienceLevel] = useState(searchParams.get("level") || "");
  const [selectedSkills, setSelectedSkills] = useState<string[]>(
    searchParams.get("skills") ? searchParams.get("skills")!.split(",").filter(Boolean) : []
  );
  const [minSalary, setMinSalary] = useState(Number(searchParams.get("min_salary") || 0));
  const [sortBy, setSortBy] = useState(searchParams.get("sort_by") || "BEST_FIT");
  const [verificationFilter, setVerificationFilter] = useState(searchParams.get("verification") || "");
  const [page, setPage] = useState(Number(searchParams.get("page") || 1));

  // Debounced input states for instant typing responsiveness
  const [debouncedQuery, setDebouncedQuery] = useState(query);
  const [debouncedRole, setDebouncedRole] = useState(role);
  const [debouncedCompany, setDebouncedCompany] = useState(company);
  const [debouncedCity, setDebouncedCity] = useState(city);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(query);
      setDebouncedRole(role);
      setDebouncedCompany(company);
      setDebouncedCity(city);
    }, 350);
    return () => clearTimeout(timer);
  }, [query, role, company, city]);

  // Result states
  const [jobs, setJobs] = useState<JobItem[]>(() => {
    return fastCache.get<JobItem[]>("search_jobs_default") || [];
  });
  const [totalCount, setTotalCount] = useState<number>(() => {
    return fastCache.get<number>("search_total_default") || 0;
  });
  const [totalPages, setTotalPages] = useState<number>(() => {
    return fastCache.get<number>("search_pages_default") || 1;
  });
  const [coverage, setCoverage] = useState<SourceCoverage | null>(null);
  const [isLoading, setIsLoading] = useState(() => {
    return (fastCache.get<JobItem[]>("search_jobs_default") || []).length === 0;
  });
  const [isFiltering, setIsFiltering] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Save Search Modal state
  const [isSaveModalOpen, setIsSaveModalOpen] = useState(false);
  const [saveSearchName, setSaveSearchName] = useState("");
  const [alertFrequency, setAlertFrequency] = useState("DAILY");
  const [isSavingSearch, setIsSavingSearch] = useState(false);
  const [saveSuccessMsg, setSaveSuccessMsg] = useState<string | null>(null);

  const fetchJobs = async (overrides?: {
    q?: string;
    role?: string;
    company?: string;
    city?: string;
    isRemoteOnly?: boolean;
    workplaceType?: string;
    employmentType?: string;
    experienceLevel?: string;
    selectedSkills?: string[];
    minSalary?: number;
    verificationFilter?: string;
    sortBy?: string;
    page?: number;
  }) => {
    const qTerm = (overrides?.q !== undefined ? overrides.q : debouncedQuery).trim();
    const roleTerm = (overrides?.role !== undefined ? overrides.role : debouncedRole).trim();
    const compTerm = (overrides?.company !== undefined ? overrides.company : debouncedCompany).trim();
    const cityTerm = (overrides?.city !== undefined ? overrides.city : debouncedCity).trim();
    const expLevel = overrides?.experienceLevel !== undefined ? overrides.experienceLevel : experienceLevel;
    const wpType = overrides?.workplaceType !== undefined ? overrides.workplaceType : workplaceType;
    const empType = overrides?.employmentType !== undefined ? overrides.employmentType : employmentType;
    const remoteOnly = overrides?.isRemoteOnly !== undefined ? overrides.isRemoteOnly : isRemoteOnly;
    const skillsList = overrides?.selectedSkills !== undefined ? overrides.selectedSkills : selectedSkills;
    const minSal = overrides?.minSalary !== undefined ? overrides.minSalary : minSalary;
    const verifFilt = overrides?.verificationFilter !== undefined ? overrides.verificationFilter : verificationFilter;
    const sortVal = overrides?.sortBy !== undefined ? overrides.sortBy : sortBy;
    const pageNum = overrides?.page !== undefined ? overrides.page : page;

    const cacheKey = `search_${qTerm}_${roleTerm}_${compTerm}_${cityTerm}_${remoteOnly}_${wpType}_${empType}_${expLevel}_${skillsList.join(",")}_${minSal}_${verifFilt}_${sortVal}_${pageNum}`;
    const cached = fastCache.get<any>(cacheKey);
    if (cached && cached.items) {
      setJobs(cached.items);
      setTotalCount(cached.total_count || 0);
      setTotalPages(cached.total_pages || 1);
      setIsLoading(false);
      setIsFiltering(false);
    } else if (jobs.length > 0) {
      setIsFiltering(true);
    } else {
      setIsLoading(true);
    }

    setErrorMsg(null);
    try {
      const params = new URLSearchParams();
      if (qTerm) params.set("q", qTerm);
      if (roleTerm) params.set("role", roleTerm);
      if (compTerm) params.set("company", compTerm);
      if (cityTerm) params.set("city", cityTerm);
      if (remoteOnly) params.set("is_remote", "true");
      if (wpType) params.append("workplace_types", wpType);
      if (empType) params.append("employment_types", empType);
      if (expLevel === "FRESHER") params.set("is_fresher_friendly", "true");
      if (expLevel === "INTERNSHIP") params.set("is_internship", "true");
      if (skillsList.length > 0) {
        skillsList.forEach((s) => params.append("skills", s));
      }
      if (minSal > 0) params.set("min_salary", minSal.toString());
      if (verifFilt) params.append("verification_statuses", verifFilt);
      params.set("sort_by", sortVal);
      params.set("page", pageNum.toString());
      params.set("page_size", "15");

      const res = await apiClient<any>(`/search/jobs?${params.toString()}`);
      if (res.data) {
        setJobs(res.data.items || []);
        setTotalCount(res.data.total_count || 0);
        setTotalPages(res.data.total_pages || 1);
        setCoverage(res.data.source_coverage || null);

        fastCache.set(cacheKey, res.data, 120000);
        if (!qTerm && !roleTerm && !compTerm && !cityTerm && !expLevel && !wpType && !empType && skillsList.length === 0 && pageNum === 1) {
          fastCache.set("search_jobs_default", res.data.items || [], 120000);
          fastCache.set("search_total_default", res.data.total_count || 0, 120000);
          fastCache.set("search_pages_default", res.data.total_pages || 1, 120000);
        }
      }
    } catch (err: any) {
      if (jobs.length === 0) setErrorMsg(err.message || "Failed to load job listings.");
    } finally {
      setIsLoading(false);
      setIsFiltering(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, [
    page,
    sortBy,
    debouncedQuery,
    debouncedRole,
    debouncedCompany,
    debouncedCity,
    selectedSkills,
    experienceLevel,
    workplaceType,
    employmentType,
    minSalary,
    isRemoteOnly,
    verificationFilter,
  ]);

  const toggleSkill = (skill: string) => {
    const next = selectedSkills.some((s) => s.toLowerCase() === skill.toLowerCase())
      ? selectedSkills.filter((s) => s.toLowerCase() !== skill.toLowerCase())
      : [...selectedSkills, skill];
    setSelectedSkills(next);
    setPage(1);
    fetchJobs({ selectedSkills: next, page: 1 });
  };

  const handleQuickPill = (val: string) => {
    const nextVal = query.toLowerCase() === val.toLowerCase() ? "" : val;
    setQuery(nextVal);
    setDebouncedQuery(nextVal);
    setPage(1);
    fetchJobs({ q: nextVal, page: 1 });
  };

  const handleResetFilters = () => {
    setQuery("");
    setRole("");
    setCompany("");
    setCity("");
    setDebouncedQuery("");
    setDebouncedRole("");
    setDebouncedCompany("");
    setDebouncedCity("");
    setIsRemoteOnly(false);
    setWorkplaceType("");
    setEmploymentType("");
    setExperienceLevel("");
    setSelectedSkills([]);
    setMinSalary(0);
    setVerificationFilter("");
    setSortBy("BEST_FIT");
    setPage(1);
    fetchJobs({
      q: "",
      role: "",
      company: "",
      city: "",
      isRemoteOnly: false,
      workplaceType: "",
      employmentType: "",
      experienceLevel: "",
      selectedSkills: [],
      minSalary: 0,
      verificationFilter: "",
      sortBy: "BEST_FIT",
      page: 1,
    });
  };

  const handleSearchSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setDebouncedQuery(query);
    setDebouncedRole(role);
    setDebouncedCompany(company);
    setDebouncedCity(city);
    setPage(1);
    fetchJobs({
      q: query,
      role,
      company,
      city,
      experienceLevel,
      workplaceType,
      employmentType,
      isRemoteOnly,
      selectedSkills,
      minSalary,
      verificationFilter,
      sortBy,
      page: 1,
    });
  };

  const handleToggleSaveJob = async (job: JobItem) => {
    if (!user) {
      router.push("/login");
      return;
    }

    try {
      if (job.is_saved) {
        await apiClient(`/saved-jobs/${job.id}`, { method: "DELETE" });
        setJobs((prev) =>
          prev.map((j) => (j.id === job.id ? { ...j, is_saved: false, saved_job_id: undefined } : j))
        );
      } else {
        const res = await apiClient<any>("/saved-jobs", {
          method: "POST",
          body: JSON.stringify({ opportunity_id: job.id }),
        });
        setJobs((prev) =>
          prev.map((j) => (j.id === job.id ? { ...j, is_saved: true, saved_job_id: res.data.id } : j))
        );
      }
    } catch (err: any) {
      alert("Failed to update saved job status: " + err.message);
    }
  };

  const handleSaveSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) {
      router.push("/login");
      return;
    }
    if (!saveSearchName.trim()) return;

    setIsSavingSearch(true);
    setSaveSuccessMsg(null);
    try {
      await apiClient("/saved-searches", {
        method: "POST",
        body: JSON.stringify({
          name: saveSearchName,
          query: query || undefined,
          filters: {
            role: role || undefined,
            company: company || undefined,
            city: city || undefined,
            is_remote: isRemoteOnly || undefined,
            verification_status: verificationFilter || undefined,
          },
          alert_enabled: true,
          alert_frequency: alertFrequency,
        }),
      });
      setSaveSuccessMsg("Search and alert notifications saved successfully!");
      setTimeout(() => {
        setIsSaveModalOpen(false);
        setSaveSuccessMsg(null);
        setSaveSearchName("");
      }, 1500);
    } catch (err: any) {
      alert("Failed to save search: " + err.message);
    } finally {
      setIsSavingSearch(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-fade-in">
      {/* Header & Save Search Action */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-300">
        <div>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">Job Discovery & Matching</h1>
          <p className="text-sm text-slate-700 font-bold mt-1">
            Search verified career opportunities evaluated with transparent, evidence-based candidate matching.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsSaveModalOpen(true)}
            className="neo-pill inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold text-indigo-900 hover:text-indigo-600 transition-all cursor-pointer"
          >
            <svg className="w-4 h-4 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            Save Search & Alerts
          </button>
        </div>
      </div>



      {/* Main Grid: Filters Sidebar + Results */}
      <div className="mt-6 grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Filters Sidebar */}
        <div className="lg:col-span-1 space-y-6 neo-box p-6 rounded-2xl border border-white/90 shadow-sm">
          <form onSubmit={handleSearchSubmit} className="space-y-4">
            {/* Keywords */}
            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-800">
                  Smart Keywords Search
                </label>
                {query && (
                  <button
                    type="button"
                    onClick={() => {
                      setQuery("");
                      setDebouncedQuery("");
                      setPage(1);
                      fetchJobs({ q: "", page: 1 });
                    }}
                    className="text-[10px] text-slate-700 font-bold hover:text-indigo-600"
                  >
                    Clear
                  </button>
                )}
              </div>
              <input
                type="text"
                placeholder="e.g. React, WebDev, Python, AWS..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => { if (e.key === "Enter") handleSearchSubmit(e); }}
                className="w-full neo-inset rounded-xl px-3.5 py-2 text-slate-900 font-bold text-xs focus:outline-none"
              />
              {/* Quick Suggestion Pills */}
              <div className="flex flex-wrap gap-1 mt-2">
                {QUICK_SEARCH_PILLS.map((pill) => {
                  const isActive = query.toLowerCase() === pill.value.toLowerCase();
                  return (
                    <button
                      key={pill.value}
                      type="button"
                      onClick={() => handleQuickPill(pill.value)}
                      className={`text-[11px] px-2.5 py-0.5 rounded-full transition-all cursor-pointer ${
                        isActive
                          ? "neo-pill font-black text-indigo-900 border border-indigo-400 shadow-sm"
                          : "neo-pill text-slate-800 font-bold hover:text-indigo-600"
                      }`}
                    >
                      {pill.label}
                    </button>
                  );
                })}
              </div>
              <p className="text-[11px] text-slate-600 font-medium mt-1.5">
                Dynamic smart search across job titles, required skills, and tech stacks.
              </p>
            </div>

            {/* Popular Skills Multi-Select Chips */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-xs font-bold uppercase tracking-wider text-slate-800">
                  Required Skills
                </label>
                {selectedSkills.length > 0 && (
                  <button
                    type="button"
                    onClick={() => {
                      setSelectedSkills([]);
                      setPage(1);
                      fetchJobs({ selectedSkills: [], page: 1 });
                    }}
                    className="text-[10px] text-slate-700 font-bold hover:text-indigo-600"
                  >
                    Clear ({selectedSkills.length})
                  </button>
                )}
              </div>
              <div className="flex flex-wrap gap-1.5 max-h-40 overflow-y-auto pr-1">
                {POPULAR_SKILLS.map((sk) => {
                  const isSelected = selectedSkills.some((s) => s.toLowerCase() === sk.toLowerCase());
                  return (
                    <button
                      key={sk}
                      type="button"
                      onClick={() => toggleSkill(sk)}
                      className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                        isSelected
                          ? "bg-emerald-100 border border-emerald-400 text-emerald-900 shadow-sm font-black"
                          : "neo-pill text-slate-800 hover:text-indigo-600"
                      }`}
                    >
                      {isSelected ? `✓ ${sk}` : `+ ${sk}`}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Career Stage / Fresher Filter */}
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-800 mb-1">
                Experience / Level
              </label>
              <select
                value={experienceLevel}
                onChange={(e) => {
                  const val = e.target.value;
                  setExperienceLevel(val);
                  setPage(1);
                  fetchJobs({ experienceLevel: val, page: 1 });
                }}
                className="w-full neo-inset rounded-xl px-3.5 py-2 text-slate-900 font-bold text-xs focus:outline-none cursor-pointer"
              >
                <option value="">All Experience Levels</option>
                <option value="FRESHER">🎓 Freshers & Entry Level (0-1 yrs)</option>
                <option value="INTERNSHIP">💼 Internships Only</option>
              </select>
            </div>

            {/* Workplace Mode */}
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-800 mb-1">
                Workplace Mode
              </label>
              <select
                value={workplaceType}
                onChange={(e) => {
                  const val = e.target.value;
                  setWorkplaceType(val);
                  const isRem = val === "REMOTE";
                  if (isRem) setIsRemoteOnly(true);
                  setPage(1);
                  fetchJobs({ workplaceType: val, isRemoteOnly: isRem, page: 1 });
                }}
                className="w-full neo-inset rounded-xl px-3.5 py-2 text-slate-900 font-bold text-xs focus:outline-none cursor-pointer"
              >
                <option value="">All Workplace Modes</option>
                <option value="REMOTE">🌐 Remote</option>
                <option value="HYBRID">🏢 Hybrid</option>
                <option value="ON_SITE">📍 On-Site</option>
              </select>
            </div>

            {/* Employment Type */}
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-800 mb-1">
                Employment Type
              </label>
              <select
                value={employmentType}
                onChange={(e) => {
                  const val = e.target.value;
                  setEmploymentType(val);
                  setPage(1);
                  fetchJobs({ employmentType: val, page: 1 });
                }}
                className="w-full neo-inset rounded-xl px-3.5 py-2 text-slate-900 font-bold text-xs focus:outline-none cursor-pointer"
              >
                <option value="">All Employment Types</option>
                <option value="FULL_TIME">Full-Time</option>
                <option value="CONTRACT">Contract / Freelance</option>
                <option value="PART_TIME">Part-Time</option>
                <option value="INTERNSHIP">Internship</option>
              </select>
            </div>

            {/* Role / Title */}
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-800 mb-1">
                Role / Title
              </label>
              <input
                type="text"
                placeholder="e.g. Frontend Engineer"
                value={role}
                onChange={(e) => setRole(e.target.value)}
                onKeyDown={(e) => { if (e.key === "Enter") handleSearchSubmit(e); }}
                className="w-full neo-inset rounded-xl px-3.5 py-2 text-slate-900 font-bold text-xs focus:outline-none"
              />
            </div>

            {/* Company */}
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-800 mb-1">
                Company
              </label>
              <input
                type="text"
                placeholder="e.g. Stripe, Cloudflare, OpenAI"
                value={company}
                onChange={(e) => setCompany(e.target.value)}
                onKeyDown={(e) => { if (e.key === "Enter") handleSearchSubmit(e); }}
                className="w-full neo-inset rounded-xl px-3.5 py-2 text-slate-900 font-bold text-xs focus:outline-none"
              />
            </div>

            {/* Location */}
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-800 mb-1">
                Location
              </label>
              <input
                type="text"
                placeholder="City, State, or Country"
                value={city}
                onChange={(e) => setCity(e.target.value)}
                onKeyDown={(e) => { if (e.key === "Enter") handleSearchSubmit(e); }}
                className="w-full neo-inset rounded-xl px-3.5 py-2 text-slate-900 font-bold text-xs focus:outline-none"
              />
            </div>

            {/* Minimum Salary */}
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-800 mb-1">
                Minimum Compensation
              </label>
              <select
                value={minSalary}
                onChange={(e) => {
                  const val = Number(e.target.value);
                  setMinSalary(val);
                  setPage(1);
                  fetchJobs({ minSalary: val, page: 1 });
                }}
                className="w-full neo-inset rounded-xl px-3.5 py-2 text-slate-900 font-bold text-xs focus:outline-none cursor-pointer"
              >
                <option value={0}>Any Compensation</option>
                <option value={50000}>$50,000+ / year</option>
                <option value={80000}>$80,000+ / year</option>
                <option value={100000}>$100,000+ / year</option>
                <option value={120000}>$120,000+ / year</option>
                <option value={150000}>$150,000+ / year</option>
              </select>
            </div>

            {/* Verification Status */}
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-800 mb-1">
                Verification Status
              </label>
              <select
                value={verificationFilter}
                onChange={(e) => {
                  const val = e.target.value;
                  setVerificationFilter(val);
                  setPage(1);
                  fetchJobs({ verificationFilter: val, page: 1 });
                }}
                className="w-full neo-inset rounded-xl px-3.5 py-2 text-slate-900 font-bold text-xs focus:outline-none cursor-pointer"
              >
                <option value="">All Listings</option>
                <option value="OPEN_CONFIRMED">✓ Open Confirmed (Active ATS)</option>
                <option value="UNVERIFIED">Unverified Only</option>
              </select>
            </div>

            {/* Action Buttons */}
            <div className="pt-2 space-y-2">
              <button
                type="submit"
                className="w-full py-2.5 px-4 neo-btn-primary text-white rounded-xl font-bold text-sm shadow-md transition-all cursor-pointer"
              >
                Search & Apply Filters
              </button>
              <button
                type="button"
                onClick={handleResetFilters}
                className="w-full py-2.5 px-4 neo-pill text-slate-800 hover:text-indigo-600 rounded-xl text-xs font-bold transition-all cursor-pointer"
              >
                Reset All Filters
              </button>
            </div>
          </form>
        </div>

        {/* Results Column */}
        <div className="lg:col-span-3 space-y-4">
          {/* Active Filter Chips Ribbon */}
          {(query || selectedSkills.length > 0 || isRemoteOnly || experienceLevel || workplaceType || employmentType || minSalary > 0 || role || company || city || verificationFilter) && (
            <div className="flex flex-wrap items-center gap-1.5 p-3 rounded-xl neo-box border border-white/90 text-xs shadow-sm">
              <span className="text-slate-800 font-bold mr-1">Active Filters:</span>
              {query && (
                <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full neo-pill text-indigo-950 font-bold border border-indigo-200">
                  <span>Keyword: {query}</span>
                  <button type="button" onClick={() => { setQuery(""); setDebouncedQuery(""); setPage(1); fetchJobs({ q: "", page: 1 }); }} className="hover:text-indigo-600 ml-0.5 cursor-pointer">✕</button>
                </span>
              )}
              {selectedSkills.map((sk) => (
                <span key={sk} className="inline-flex items-center gap-1 px-3 py-1 rounded-full neo-pill text-emerald-950 font-bold border border-emerald-200">
                  <span>Skill: {sk}</span>
                  <button type="button" onClick={() => toggleSkill(sk)} className="hover:text-emerald-600 ml-0.5 cursor-pointer">✕</button>
                </span>
              ))}
              {experienceLevel && (
                <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full neo-pill text-amber-950 font-bold border border-amber-200">
                  <span>{experienceLevel === "FRESHER" ? "Freshers / Entry-Level" : "Internships"}</span>
                  <button type="button" onClick={() => { setExperienceLevel(""); setPage(1); fetchJobs({ experienceLevel: "", page: 1 }); }} className="hover:text-amber-600 ml-0.5 cursor-pointer">✕</button>
                </span>
              )}
              {workplaceType && (
                <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full neo-pill text-blue-950 font-bold border border-blue-200">
                  <span>Mode: {workplaceType}</span>
                  <button type="button" onClick={() => { setWorkplaceType(""); setPage(1); fetchJobs({ workplaceType: "", page: 1 }); }} className="hover:text-blue-600 ml-0.5 cursor-pointer">✕</button>
                </span>
              )}
              {isRemoteOnly && !workplaceType && (
                <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full neo-pill text-blue-950 font-bold border border-blue-200">
                  <span>Remote Only</span>
                  <button type="button" onClick={() => { setIsRemoteOnly(false); setPage(1); fetchJobs({ isRemoteOnly: false, page: 1 }); }} className="hover:text-blue-600 ml-0.5 cursor-pointer">✕</button>
                </span>
              )}
              {employmentType && (
                <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full neo-pill text-purple-950 font-bold border border-purple-200">
                  <span>Type: {employmentType}</span>
                  <button type="button" onClick={() => { setEmploymentType(""); setPage(1); fetchJobs({ employmentType: "", page: 1 }); }} className="hover:text-purple-600 ml-0.5 cursor-pointer">✕</button>
                </span>
              )}
              {minSalary > 0 && (
                <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full neo-pill text-emerald-950 font-bold border border-emerald-200">
                  <span>Min: ${minSalary.toLocaleString()}</span>
                  <button type="button" onClick={() => { setMinSalary(0); setPage(1); fetchJobs({ minSalary: 0, page: 1 }); }} className="hover:text-emerald-600 ml-0.5 cursor-pointer">✕</button>
                </span>
              )}
              {role && (
                <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full neo-pill text-slate-900 font-bold border border-white/90 shadow-sm">
                  <span>Role: {role}</span>
                  <button type="button" onClick={() => { setRole(""); setDebouncedRole(""); setPage(1); fetchJobs({ role: "", page: 1 }); }} className="hover:text-indigo-600 ml-0.5 cursor-pointer">✕</button>
                </span>
              )}
              {company && (
                <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full neo-pill text-slate-900 font-bold border border-white/90 shadow-sm">
                  <span>Company: {company}</span>
                  <button type="button" onClick={() => { setCompany(""); setDebouncedCompany(""); setPage(1); fetchJobs({ company: "", page: 1 }); }} className="hover:text-indigo-600 ml-0.5 cursor-pointer">✕</button>
                </span>
              )}
              {city && (
                <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full neo-pill text-slate-900 font-bold border border-white/90 shadow-sm">
                  <span>Location: {city}</span>
                  <button type="button" onClick={() => { setCity(""); setDebouncedCity(""); setPage(1); fetchJobs({ city: "", page: 1 }); }} className="hover:text-indigo-600 ml-0.5 cursor-pointer">✕</button>
                </span>
              )}
              {verificationFilter && (
                <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full neo-pill text-slate-900 font-bold border border-white/90 shadow-sm">
                  <span>Status: {verificationFilter === "OPEN_CONFIRMED" ? "Open Confirmed" : verificationFilter}</span>
                  <button type="button" onClick={() => { setVerificationFilter(""); setPage(1); fetchJobs({ verificationFilter: "", page: 1 }); }} className="hover:text-indigo-600 ml-0.5 cursor-pointer">✕</button>
                </span>
              )}
              <button
                type="button"
                onClick={handleResetFilters}
                className="text-xs text-rose-600 hover:text-rose-800 underline font-bold ml-auto cursor-pointer"
              >
                Clear All
              </button>
            </div>
          )}

          {/* Controls Bar */}
          <div className="flex flex-wrap items-center justify-between gap-4 neo-card px-4 py-3 rounded-xl border border-white/90 shadow-sm">
            <div className="text-sm text-slate-800 font-bold">
              Showing <span className="font-black text-indigo-900">{jobs.length}</span> of{" "}
              <span className="font-black text-indigo-900">{totalCount}</span> opportunities
            </div>
            <div className="flex items-center gap-2 text-sm text-slate-800 font-bold">
              <label>Sort by:</label>
              <select
                value={sortBy}
                onChange={(e) => {
                  const val = e.target.value;
                  setSortBy(val);
                  setPage(1);
                  fetchJobs({ sortBy: val, page: 1 });
                }}
                className="px-3 py-1.5 neo-inset rounded-lg text-slate-900 font-bold text-xs focus:outline-none cursor-pointer"
              >
                <option value="BEST_FIT">Best Fit (Match & Verified)</option>
                <option value="RELEVANCE">🎯 Relevance / Smart Match</option>
                <option value="MOST_RECENT">Most Recent</option>
                <option value="HIGHEST_SALARY">Highest Compensation</option>
                <option value="SKILL_MATCH">Skill Match %</option>
              </select>
            </div>
          </div>

          {/* Error Message */}
          {errorMsg && (
            <div className="p-4 rounded-xl neo-box border border-red-300 text-red-900 font-bold text-sm shadow-sm">
              {errorMsg}
            </div>
          )}

          {/* Top Background Revalidation Glow Bar */}
          {isFiltering && (
            <div className="fixed top-0 left-0 right-0 h-[3px] bg-gradient-to-r from-indigo-500 via-purple-500 to-emerald-400 animate-pulse z-50 shadow-sm" />
          )}

          {/* Loading Skeleton */}
          {isLoading && jobs.length === 0 ? (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="animate-pulse neo-card rounded-2xl p-6 border border-white/90 h-44 shadow-sm" />
              ))}
            </div>
          ) : jobs.length === 0 ? (
            <div className="text-center py-12 px-6 neo-box rounded-2xl border border-white/90 shadow-sm space-y-4">
              <div className="w-12 h-12 mx-auto rounded-full neo-pill flex items-center justify-center text-indigo-600 font-bold text-xl">
                🔍
              </div>
              <div>
                <h3 className="text-base font-bold text-slate-900">No opportunities matching your criteria</h3>
                <p className="text-xs text-slate-700 font-bold mt-1">
                  {company
                    ? `No active openings found for "${company}" in our current index.`
                    : "Try broadening your keywords or removing location filters."}
                </p>
              </div>

              {/* Popular Actively Hiring Companies */}
              <div className="pt-2 max-w-lg mx-auto">
                <p className="text-xs font-bold text-slate-700 mb-2">Actively hiring companies with open roles:</p>
                <div className="flex flex-wrap items-center justify-center gap-1.5">
                  {POPULAR_COMPANIES.map((c) => (
                    <button
                      key={c}
                      type="button"
                      onClick={() => {
                        setCompany(c);
                        setDebouncedCompany(c);
                        setPage(1);
                        fetchJobs({ company: c, page: 1 });
                      }}
                      className="neo-pill px-3 py-1 text-xs font-bold text-indigo-900 hover:text-indigo-600 hover:scale-105 transition-all cursor-pointer"
                    >
                      {c}
                    </button>
                  ))}
                </div>
              </div>

              <div className="pt-2">
                <button
                  type="button"
                  onClick={handleResetFilters}
                  className="px-4 py-2 neo-pill text-xs font-bold text-indigo-900 hover:text-indigo-600 transition-all cursor-pointer"
                >
                  Reset All Filters
                </button>
              </div>
            </div>
          ) : (
            /* Opportunity Cards */
            <div className={`space-y-4 transition-opacity duration-150 ${isFiltering ? "opacity-80" : "opacity-100"}`}>
              {jobs.map((job) => (
                <div
                  key={job.id}
                  className="neo-card neo-box-hover rounded-2xl p-6 border border-white/90 space-y-4 shadow-sm"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <div className="flex items-center gap-2 flex-wrap">
                        <Link
                          href={`/jobs/${job.id}`}
                          className="text-lg font-bold text-slate-900 hover:text-indigo-600 transition-colors"
                        >
                          {job.title}
                        </Link>
                        {job.is_remote && (
                          <span className="px-2.5 py-0.5 text-xs font-bold rounded-full neo-pill text-emerald-800 border border-emerald-300">
                            🌐 Remote
                          </span>
                        )}
                        <span className="px-2.5 py-0.5 text-xs font-bold rounded-full neo-pill text-slate-900 border border-white/90">
                          {job.workplace_type}
                        </span>
                      </div>
                      <div className="text-sm text-slate-700 font-bold mt-1.5 flex items-center gap-2.5 flex-wrap">
                        <span className="font-black text-indigo-950">{job.company_name}</span>
                        <span>•</span>
                        <span>{job.city ? `${job.city}${job.country ? `, ${job.country}` : ""}` : job.country || "Worldwide"}</span>
                        <span>•</span>
                        <span className="text-xs text-slate-700 font-bold">Source: {job.source_name}</span>
                      </div>
                    </div>

                    {/* Save / Bookmark Button */}
                    <button
                      type="button"
                      onClick={() => handleToggleSaveJob(job)}
                      title={job.is_saved ? "Remove from saved jobs" : "Save this job"}
                      className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                        job.is_saved
                          ? "neo-pill text-amber-700 border border-amber-300 shadow-sm"
                          : "neo-pill text-slate-800 hover:text-indigo-600"
                      }`}
                    >
                      <svg
                        className={`w-3.5 h-3.5 ${job.is_saved ? "text-amber-500 fill-current" : "text-slate-600"}`}
                        fill={job.is_saved ? "currentColor" : "none"}
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
                      <span>{job.is_saved ? "★ Saved" : "☆ Save Job"}</span>
                    </button>
                  </div>

                  {/* Badges: Verification, Freshness, Skill Fit & Eligibility */}
                  <div className="flex items-center gap-3 flex-wrap text-xs pt-1">
                    {/* Verification Badge */}
                    <span
                      className={`px-2.5 py-1 rounded-md font-bold border ${
                        job.verification_status === "OPEN_CONFIRMED"
                          ? "neo-pill bg-emerald-50 text-emerald-800 border-emerald-300"
                          : "neo-pill text-slate-700 font-bold"
                      }`}
                    >
                      {job.verification_status === "OPEN_CONFIRMED" ? "✓ Open Confirmed" : job.verification_status}
                    </span>

                    {/* Freshness Badge */}
                    <span
                      className={`px-2.5 py-1 rounded-md font-bold neo-pill ${
                        job.freshness_state === "FRESH"
                          ? "text-blue-900 border-blue-300"
                          : job.freshness_state === "RECENT"
                            ? "text-cyan-900 border-cyan-300"
                            : "text-slate-700 font-bold"
                      }`}
                    >
                      Freshness: {job.freshness_state}
                    </span>

                    {/* Smart Match Relevance Badge */}
                    {job.relevance_score !== undefined && job.relevance_score !== null && job.relevance_score > 0 && (
                      <span className="px-2.5 py-1 rounded-md font-bold neo-pill bg-purple-50 text-purple-900 border-purple-300 flex items-center gap-1">
                        🎯 Smart Match ({Math.round(job.relevance_score)})
                      </span>
                    )}

                    {/* Skill Fit Badge */}
                    {job.skill_fit_score !== undefined && job.skill_fit_score !== null && (
                      <span className="px-2.5 py-1 rounded-md font-bold neo-pill bg-indigo-50 text-indigo-900 border-indigo-300">
                        ★ {job.skill_fit_score}% Skill Fit
                      </span>
                    )}

                    {/* Mandatory Eligibility Badge */}
                    {job.eligibility_status && (
                      <span
                        className={`px-2.5 py-1 rounded-md font-bold neo-pill ${
                          job.eligibility_status === "MEETS_REQUIREMENTS"
                            ? "text-emerald-800 border-emerald-300"
                            : job.eligibility_status === "UNKNOWN"
                              ? "text-slate-700 font-bold"
                              : "text-rose-800 border-rose-300"
                        }`}
                      >
                        Eligibility: {job.eligibility_status.replace(/_/g, " ")}
                      </span>
                    )}
                  </div>

                  {/* Company Requirements & Skill Alignment */}
                  <div className="p-3.5 rounded-xl neo-inset space-y-2.5">
                    {/* Company Required Skills */}
                    {job.required_skills && job.required_skills.length > 0 && (
                      <div className="space-y-1.5">
                        <div className="flex items-center justify-between text-[11px] font-bold text-slate-800 uppercase tracking-wider">
                          <span>Company Required Skills</span>
                          <span className="text-[10px] text-slate-600 font-medium">
                            {job.required_skills.length} required
                          </span>
                        </div>
                        <div className="flex flex-wrap gap-1.5">
                          {job.required_skills.map((skill, idx) => {
                            const skillLower = skill.toLowerCase();
                            const isMatched = job.matched_skills_preview?.some(
                              (m) => m.toLowerCase() === skillLower
                            );
                            const isSearchMatched =
                              debouncedQuery &&
                              (skillLower.includes(debouncedQuery.toLowerCase()) ||
                                debouncedQuery.toLowerCase().includes(skillLower));
                            const isSkillSelected = selectedSkills.some(
                              (s) => s.toLowerCase() === skillLower
                            );
                            const isHighlighted = isMatched || isSearchMatched || isSkillSelected;

                            return (
                              <span
                                key={idx}
                                className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-[11px] font-bold border transition-all ${
                                  isHighlighted
                                    ? "bg-emerald-100 border-emerald-300 text-emerald-900 shadow-sm"
                                    : "neo-pill text-slate-800 border-white/90"
                                }`}
                                title={
                                  isMatched
                                    ? "Matched from candidate profile / resume"
                                    : isSearchMatched || isSkillSelected
                                      ? "Matches your active search filter"
                                      : "Required by employer"
                                }
                              >
                                {isHighlighted && <span className="text-emerald-700 font-bold">✓</span>}
                                <span>{skill}</span>
                              </span>
                            );
                          })}
                        </div>
                      </div>
                    )}

                    {/* Candidate Matched & Missing Skills from Resume */}
                    <div className="flex flex-wrap items-center gap-x-4 gap-y-1 pt-1 border-t border-slate-300 text-xs">
                      {job.matched_skills_preview && job.matched_skills_preview.length > 0 && (
                        <div className="flex items-center gap-1.5 flex-wrap">
                          <span className="text-[11px] font-bold text-emerald-800">Matched in Resume:</span>
                          <div className="flex items-center gap-1 flex-wrap">
                            {job.matched_skills_preview.map((ms, idx) => (
                              <span
                                key={idx}
                                className="text-[10px] px-2 py-0.5 rounded-lg bg-emerald-100 text-emerald-900 border border-emerald-300 font-mono font-bold"
                              >
                                ✓ {ms}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                      {job.missing_skills_preview && job.missing_skills_preview.length > 0 && (
                        <div className="flex items-center gap-1.5 flex-wrap">
                          <span className="text-[11px] font-bold text-amber-800">Missing from Resume:</span>
                          <div className="flex items-center gap-1 flex-wrap">
                            {job.missing_skills_preview.map((mis, idx) => (
                              <span
                                key={idx}
                                className="text-[10px] px-2 py-0.5 rounded-lg bg-amber-50 text-amber-900 border border-amber-300 font-mono font-bold"
                              >
                                {mis}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Card Footer: Salary & Actions */}
                  <div className="flex items-center justify-between pt-3 border-t border-slate-300 text-sm">
                    <div className="font-bold text-slate-900">
                      {job.min_salary || job.max_salary ? (
                        <>
                          {job.currency || "$"}
                          {job.min_salary?.toLocaleString()} - {job.max_salary?.toLocaleString()}{" "}
                          <span className="text-xs text-slate-700 font-bold font-normal">/ {job.salary_period || "year"}</span>
                        </>
                      ) : (
                        <span className="text-xs text-slate-600 font-medium">Salary not disclosed</span>
                      )}
                    </div>
                    <div className="flex items-center gap-2 flex-wrap">
                      <Link
                        href={`/jobs/${job.id}`}
                        className="px-3.5 py-1.5 rounded-xl text-xs font-bold neo-pill text-indigo-900 hover:text-indigo-600 border border-indigo-200 transition-all cursor-pointer"
                      >
                        View Details →
                      </Link>
                      <a
                        href={job.application_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="px-3.5 py-1.5 rounded-xl text-xs font-bold neo-btn-primary text-white shadow-sm transition-all cursor-pointer"
                      >
                        Direct Apply ↗
                      </a>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between pt-6 border-t border-slate-300">
              <button
                disabled={page <= 1}
                onClick={() => {
                  const newPage = Math.max(1, page - 1);
                  setPage(newPage);
                  fetchJobs({ page: newPage });
                }}
                className="px-4 py-2 rounded-xl neo-pill text-xs font-bold text-slate-900 hover:text-indigo-600 disabled:opacity-40 disabled:cursor-not-allowed transition-all cursor-pointer"
              >
                ← Previous
              </button>
              <span className="text-xs text-slate-800 font-bold">
                Page <span className="text-indigo-900 font-black">{page}</span> of {totalPages}
              </span>
              <button
                disabled={page >= totalPages}
                onClick={() => {
                  const newPage = Math.min(totalPages, page + 1);
                  setPage(newPage);
                  fetchJobs({ page: newPage });
                }}
                className="px-4 py-2 rounded-xl neo-pill text-xs font-bold text-slate-900 hover:text-indigo-600 disabled:opacity-40 disabled:cursor-not-allowed transition-all cursor-pointer"
              >
                Next →
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Save Search & Alert Modal */}
      {isSaveModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="neo-box border border-white/90 rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <h3 className="text-lg font-black text-slate-900">Save Search & Configure Alerts</h3>
            <p className="text-xs text-slate-700 font-bold">
              Receive automatic notifications when fresh opportunities matching your filters are ingested.
            </p>

            <form onSubmit={handleSaveSearch} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-800 mb-1">Search Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Remote Backend Python Roles"
                  value={saveSearchName}
                  onChange={(e) => setSaveSearchName(e.target.value)}
                  className="w-full px-3.5 py-2 neo-inset rounded-xl text-xs font-bold text-slate-900 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-800 mb-1">Notification Cadence</label>
                <select
                  value={alertFrequency}
                  onChange={(e) => setAlertFrequency(e.target.value)}
                  className="w-full px-3.5 py-2 neo-inset rounded-xl text-xs font-bold text-slate-900 focus:outline-none cursor-pointer"
                >
                  <option value="INSTANT">Instant (Real-Time Ingestion)</option>
                  <option value="DAILY">Daily Digest</option>
                  <option value="WEEKLY">Weekly Summary</option>
                </select>
              </div>

              {saveSuccessMsg && (
                <div className="p-3 rounded-xl bg-emerald-100 border border-emerald-300 text-emerald-900 text-xs font-bold">
                  {saveSuccessMsg}
                </div>
              )}

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-300">
                <button
                  type="button"
                  onClick={() => setIsSaveModalOpen(false)}
                  className="px-4 py-2 rounded-xl neo-pill text-xs font-bold text-slate-800 hover:text-slate-900 cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSavingSearch}
                  className="px-4 py-2 rounded-xl neo-btn-primary text-xs font-bold text-white shadow-sm disabled:opacity-50 cursor-pointer"
                >
                  {isSavingSearch ? "Saving..." : "Save Subscription"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default function JobSearchPage() {
  return (
    <React.Suspense
      fallback={
        <div className="max-w-7xl mx-auto px-4 py-16 text-slate-800 font-bold text-sm">
          Loading Job Discovery & Matching...
        </div>
      }
    >
      <SearchContent />
    </React.Suspense>
  );
}
