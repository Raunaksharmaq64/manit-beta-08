"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { apiClient } from "../../../services/apiClient";

interface Education {
  id: string;
  institution: string;
  degree: string;
  field_of_study: string;
  start_date?: string;
  end_date?: string;
  is_current: boolean;
  achievements?: string;
  provenance: string;
}

interface Experience {
  id: string;
  company: string;
  role: string;
  employment_type: string;
  start_date?: string;
  end_date?: string;
  is_current: boolean;
  description?: string;
  skills: string[];
  provenance: string;
}

interface Skill {
  id: string;
  skill_name: string;
  category: string;
  proficiency: string;
  years_experience?: number;
  provenance: string;
}

interface Profile {
  id: string;
  user_id: string;
  headline?: string;
  summary?: string;
  phone?: string;
  city?: string;
  state?: string;
  country?: string;
  timezone?: string;
  portfolio_url?: string;
  linkedin_url?: string;
  github_url?: string;
  website_url?: string;
  social_links?: Record<string, string>;
  education: Education[];
  experience: Experience[];
  skills: Skill[];
}

interface CompletenessSectionImpact {
  section_key: string;
  section_name: string;
  is_completed: boolean;
  weight_percentage: number;
  why_it_matters: string;
  unlocks: string;
  is_required: boolean;
}

interface Completeness {
  score_percentage: number;
  has_basic_info: boolean;
  has_education: boolean;
  has_experience: boolean;
  has_skills: boolean;
  has_preferences: boolean;
  missing_sections: string[];
  section_breakdown?: CompletenessSectionImpact[];
}

export default function ProfilePage() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [completeness, setCompleteness] = useState<Completeness | null>(null);
  const [loading, setLoading] = useState(true);
  const [editingBasic, setEditingBasic] = useState(false);
  const [syncingResume, setSyncingResume] = useState(false);
  const [syncNotice, setSyncNotice] = useState<string | null>(null);

  // Edit form state
  const [headline, setHeadline] = useState("");
  const [summary, setSummary] = useState("");
  const [phone, setPhone] = useState("");
  const [city, setCity] = useState("");
  const [country, setCountry] = useState("");
  const [portfolioUrl, setPortfolioUrl] = useState("");
  const [linkedinUrl, setLinkedinUrl] = useState("");
  const [githubUrl, setGithubUrl] = useState("");
  const [websiteUrl, setWebsiteUrl] = useState("");

  // Modal forms
  const [showEduModal, setShowEduModal] = useState(false);
  const [eduInst, setEduInst] = useState("");
  const [eduDegree, setEduDegree] = useState("");
  const [eduField, setEduField] = useState("");

  const [showExpModal, setShowExpModal] = useState(false);
  const [expCompany, setExpCompany] = useState("");
  const [expRole, setExpRole] = useState("");
  const [expDesc, setExpDesc] = useState("");
  const [expStart, setExpStart] = useState("");
  const [expEnd, setExpEnd] = useState("");

  const [showSkillModal, setShowSkillModal] = useState(false);
  const [skillName, setSkillName] = useState("");
  const [skillProf, setSkillProf] = useState("Intermediate");

  const loadData = async () => {
    try {
      const [pResp, cResp] = await Promise.all([
        apiClient<Profile>("/candidate/profile"),
        apiClient<Completeness>("/candidate/profile/completeness"),
      ]);
      setProfile(pResp.data);
      setCompleteness(cResp.data);
      setHeadline(pResp.data.headline || "");
      setSummary(pResp.data.summary || "");
      setPhone(pResp.data.phone || "");
      setCity(pResp.data.city || "");
      setCountry(pResp.data.country || "");
      setPortfolioUrl(pResp.data.portfolio_url || "");
      setLinkedinUrl(pResp.data.linkedin_url || "");
      setGithubUrl(pResp.data.github_url || "");
      setWebsiteUrl(pResp.data.website_url || "");
    } catch (err) {
      console.error("Failed to load profile:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSyncFromLatestResume = async () => {
    try {
      setSyncingResume(true);
      setSyncNotice(null);
      const res: any = await apiClient("/candidate/profile/sync-latest-resume", {
        method: "POST",
      });
      if (res.data || res.success) {
        setSyncNotice("✓ Successfully synced skills, links, experience, and contact details from your latest resume!");
        setTimeout(() => setSyncNotice(null), 8000);
        await loadData();
      }
    } catch (err: any) {
      alert("Failed to sync from resume: " + (err.message || "Unknown error"));
    } finally {
      setSyncingResume(false);
    }
  };

  const handleSaveBasic = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const resp = await apiClient<Profile>("/candidate/profile", {
        method: "PUT",
        body: JSON.stringify({
          headline,
          summary,
          phone,
          city,
          country,
          portfolio_url: portfolioUrl || null,
          linkedin_url: linkedinUrl || null,
          github_url: githubUrl || null,
          website_url: websiteUrl || null,
        }),
      });
      setProfile(resp.data);
      setEditingBasic(false);
      loadData();
    } catch (err) {
      alert("Failed to update profile.");
    }
  };

  const handleAddEdu = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient("/candidate/education", {
        method: "POST",
        body: JSON.stringify({
          institution: eduInst,
          degree: eduDegree,
          field_of_study: eduField,
          provenance: "USER_PROVIDED",
        }),
      });
      setShowEduModal(false);
      setEduInst("");
      setEduDegree("");
      setEduField("");
      loadData();
    } catch (err) {
      alert("Failed to add education.");
    }
  };

  const handleDeleteEdu = async (id: string) => {
    if (!confirm("Delete this education entry?")) return;
    try {
      await apiClient(`/candidate/education/${id}`, { method: "DELETE" });
      loadData();
    } catch (err) {
      alert("Failed to delete entry.");
    }
  };

  const handleAddExp = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient("/candidate/experience", {
        method: "POST",
        body: JSON.stringify({
          company: expCompany,
          role: expRole,
          description: expDesc,
          start_date: expStart || undefined,
          end_date: expEnd || undefined,
          provenance: "USER_PROVIDED",
        }),
      });
      setShowExpModal(false);
      setExpCompany("");
      setExpRole("");
      setExpDesc("");
      loadData();
    } catch (err) {
      alert("Failed to add experience.");
    }
  };

  const handleDeleteExp = async (id: string) => {
    if (!confirm("Delete this experience entry?")) return;
    try {
      await apiClient(`/candidate/experience/${id}`, { method: "DELETE" });
      loadData();
    } catch (err) {
      alert("Failed to delete experience.");
    }
  };

  const handleAddSkill = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient("/candidate/skills", {
        method: "POST",
        body: JSON.stringify({
          skill_name: skillName,
          proficiency: skillProf,
          provenance: "USER_PROVIDED",
        }),
      });
      setShowSkillModal(false);
      setSkillName("");
      loadData();
    } catch (err) {
      alert("Failed to add skill.");
    }
  };

  const handleDeleteSkill = async (id: string) => {
    try {
      await apiClient(`/candidate/skills/${id}`, { method: "DELETE" });
      loadData();
    } catch (err) {
      alert("Failed to delete skill.");
    }
  };

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto py-16 px-4 text-center text-slate-700 font-bold">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto mb-3"></div>
        Loading candidate profile...
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto py-8 px-4 sm:px-6 lg:px-8 space-y-6 animate-fade-in">
      {/* Page Header with Auto-Sync action */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-4 border-b border-slate-300/80 gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
            Candidate Profile
          </h1>
          <p className="mt-1 text-xs sm:text-sm text-slate-600 font-semibold">
            Your canonical verified identity, career summary, portfolio links, and synchronized skill competencies.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            type="button"
            disabled={syncingResume}
            onClick={handleSyncFromLatestResume}
            className="px-4 py-2.5 rounded-xl neo-pill text-xs font-black text-indigo-900 hover:text-indigo-600 border border-white/90 shadow-sm flex items-center gap-1.5 transition-all disabled:opacity-50"
          >
            <span>{syncingResume ? "⏳" : "🔄"}</span>
            <span>{syncingResume ? "Syncing from Resume..." : "Auto-Sync from Resume"}</span>
          </button>
          <Link
            href="/resumes"
            className="neo-btn-primary px-4 py-2.5 rounded-xl text-xs font-bold transition-all shadow-md flex items-center gap-1.5 shrink-0"
          >
            <span>📄</span>
            <span>Manage Resumes →</span>
          </Link>
        </div>
      </div>

      {/* Sync Notice Alert */}
      {syncNotice && (
        <div className="p-4 rounded-2xl bg-emerald-100 border border-emerald-300 text-emerald-950 text-xs font-bold flex items-center gap-2 shadow-sm animate-fade-in">
          <span>✨</span>
          <span>{syncNotice}</span>
        </div>
      )}

      {/* Completeness Banner & Section Impact Unlocks */}
      {completeness && (
        <div className="neo-card p-6 rounded-2xl border border-white/90 shadow-sm space-y-4">
          <div className="flex justify-between items-center">
            <div>
              <span className="text-xs font-black tracking-wide text-indigo-700 uppercase">
                Profile Completeness &amp; Matching Power
              </span>
              <p className="text-xs text-slate-600 font-semibold mt-0.5">
                Complete each section to activate high-precision semantic matching and compensation calibration.
              </p>
            </div>
            <div className="text-right">
              <span className="text-2xl font-black text-indigo-700 font-mono">
                {completeness.score_percentage}%
              </span>
            </div>
          </div>
          <div className="w-full neo-inset rounded-full h-2.5 overflow-hidden">
            <div
              className="bg-indigo-600 h-2.5 rounded-full transition-all duration-500"
              style={{ width: `${completeness.score_percentage}%` }}
            />
          </div>

          {completeness.section_breakdown && completeness.section_breakdown.length > 0 && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 pt-2">
              {completeness.section_breakdown.map((sec) => (
                <div
                  key={sec.section_key}
                  className={`p-3 rounded-xl border text-xs transition-all ${
                    sec.is_completed
                      ? "neo-box border-emerald-300 text-slate-800"
                      : "neo-inset border-amber-300/70 text-slate-700"
                  }`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="font-black text-slate-900 flex items-center gap-1.5">
                      {sec.is_completed ? (
                        <span className="text-emerald-700 font-bold">✓</span>
                      ) : (
                        <span className="text-amber-700 font-bold">○</span>
                      )}
                      {sec.section_name}
                    </span>
                    <span className="text-[10px] px-1.5 py-0.5 rounded-md neo-pill font-mono font-bold text-slate-700">
                      {sec.weight_percentage}% wt
                    </span>
                  </div>
                  <div className="text-[11px] text-slate-600 font-medium">
                    <span className="text-indigo-700 font-bold">Unlocks: </span>
                    {sec.unlocks}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Basic Personal Information & Social Links */}
      <section className="neo-box p-6 rounded-2xl border border-white/95 shadow-sm space-y-4">
        <div className="flex justify-between items-center pb-3 border-b border-slate-300/80">
          <div>
            <h2 className="text-lg font-black text-slate-900">Personal &amp; Contact Details</h2>
            <p className="text-xs text-slate-600 font-semibold mt-0.5">
              Auto-synced from your uploaded resume or manually editable.
            </p>
          </div>
          <button
            onClick={() => setEditingBasic(!editingBasic)}
            className="text-xs font-bold px-3.5 py-1.5 rounded-xl neo-pill text-indigo-900 hover:text-indigo-600 transition-all border border-white/90"
          >
            {editingBasic ? "Cancel" : "Edit Details"}
          </button>
        </div>

        {editingBasic ? (
          <form onSubmit={handleSaveBasic} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-black uppercase text-slate-700 mb-1">Headline / Role Title</label>
                <input
                  type="text"
                  value={headline}
                  onChange={(e) => setHeadline(e.target.value)}
                  placeholder="e.g. Senior Full-Stack Engineer"
                  className="w-full px-3 py-2 neo-inset rounded-xl text-xs sm:text-sm text-slate-900 font-semibold border border-slate-300/80"
                />
              </div>
              <div>
                <label className="block text-xs font-black uppercase text-slate-700 mb-1">Contact Phone</label>
                <input
                  type="text"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="e.g. +1 (555) 123-4567"
                  className="w-full px-3 py-2 neo-inset rounded-xl text-xs sm:text-sm text-slate-900 font-semibold border border-slate-300/80"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-black uppercase text-slate-700 mb-1">Executive Summary / Bio</label>
              <textarea
                value={summary}
                onChange={(e) => setSummary(e.target.value)}
                rows={3}
                placeholder="2-3 sentence overview of your domain focus and technical leadership."
                className="w-full px-3 py-2 neo-inset rounded-xl text-xs sm:text-sm text-slate-900 font-semibold border border-slate-300/80"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-black uppercase text-slate-700 mb-1">City</label>
                <input
                  type="text"
                  value={city}
                  onChange={(e) => setCity(e.target.value)}
                  placeholder="e.g. San Francisco, CA"
                  className="w-full px-3 py-2 neo-inset rounded-xl text-xs sm:text-sm text-slate-900 font-semibold border border-slate-300/80"
                />
              </div>
              <div>
                <label className="block text-xs font-black uppercase text-slate-700 mb-1">Country</label>
                <input
                  type="text"
                  value={country}
                  onChange={(e) => setCountry(e.target.value)}
                  placeholder="e.g. United States"
                  className="w-full px-3 py-2 neo-inset rounded-xl text-xs sm:text-sm text-slate-900 font-semibold border border-slate-300/80"
                />
              </div>
            </div>

            <div className="pt-2 border-t border-slate-200 space-y-3">
              <span className="text-xs font-black uppercase text-indigo-700 block">Portfolio &amp; Social Links</span>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Portfolio URL</label>
                  <input
                    type="url"
                    value={portfolioUrl}
                    onChange={(e) => setPortfolioUrl(e.target.value)}
                    placeholder="https://myportfolio.dev"
                    className="w-full px-3 py-2 neo-inset rounded-xl text-xs text-slate-900 font-semibold border border-slate-300/80"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">LinkedIn Profile</label>
                  <input
                    type="url"
                    value={linkedinUrl}
                    onChange={(e) => setLinkedinUrl(e.target.value)}
                    placeholder="https://linkedin.com/in/username"
                    className="w-full px-3 py-2 neo-inset rounded-xl text-xs text-slate-900 font-semibold border border-slate-300/80"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">GitHub Profile</label>
                  <input
                    type="url"
                    value={githubUrl}
                    onChange={(e) => setGithubUrl(e.target.value)}
                    placeholder="https://github.com/username"
                    className="w-full px-3 py-2 neo-inset rounded-xl text-xs text-slate-900 font-semibold border border-slate-300/80"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Personal Website</label>
                  <input
                    type="url"
                    value={websiteUrl}
                    onChange={(e) => setWebsiteUrl(e.target.value)}
                    placeholder="https://mywebsite.com"
                    className="w-full px-3 py-2 neo-inset rounded-xl text-xs text-slate-900 font-semibold border border-slate-300/80"
                  />
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setEditingBasic(false)}
                className="px-4 py-2 neo-pill rounded-xl text-xs font-bold text-slate-700"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="neo-btn-primary px-5 py-2 rounded-xl text-xs font-bold shadow-md"
              >
                Save Changes
              </button>
            </div>
          </form>
        ) : (
          <div className="space-y-4">
            <div>
              <div className="text-xl font-black text-slate-900">{profile?.headline || "Candidate"}</div>
              <p className="text-xs sm:text-sm text-slate-700 font-semibold leading-relaxed mt-1">
                {profile?.summary || "Add a career summary to highlight your strengths."}
              </p>
              <div className="flex flex-wrap items-center gap-3 text-xs text-slate-600 font-bold mt-2">
                <span>📍 {profile?.city || "Remote"}, {profile?.country || "Global"}</span>
                {profile?.phone && <span>📞 {profile.phone}</span>}
              </div>
            </div>

            {/* Links Badges */}
            <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-300/70">
              {profile?.portfolio_url && (
                <a
                  href={profile.portfolio_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-3 py-1 rounded-xl neo-pill text-xs font-bold text-indigo-700 hover:text-indigo-900 flex items-center gap-1.5 border border-white/90 shadow-sm"
                >
                  <span>🌐</span>
                  <span>Portfolio</span>
                </a>
              )}
              {profile?.linkedin_url && (
                <a
                  href={profile.linkedin_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-3 py-1 rounded-xl neo-pill text-xs font-bold text-blue-700 hover:text-blue-900 flex items-center gap-1.5 border border-white/90 shadow-sm"
                >
                  <span>💼</span>
                  <span>LinkedIn</span>
                </a>
              )}
              {profile?.github_url && (
                <a
                  href={profile.github_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-3 py-1 rounded-xl neo-pill text-xs font-bold text-slate-900 hover:text-indigo-600 flex items-center gap-1.5 border border-white/90 shadow-sm"
                >
                  <span>🐙</span>
                  <span>GitHub</span>
                </a>
              )}
              {profile?.website_url && profile.website_url !== profile.portfolio_url && (
                <a
                  href={profile.website_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-3 py-1 rounded-xl neo-pill text-xs font-bold text-purple-700 hover:text-purple-900 flex items-center gap-1.5 border border-white/90 shadow-sm"
                >
                  <span>🔗</span>
                  <span>Website</span>
                </a>
              )}
              {profile?.social_links && Object.entries(profile.social_links).map(([k, v]) => (
                <a
                  key={k}
                  href={v}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-3 py-1 rounded-xl neo-pill text-xs font-bold text-slate-800 hover:text-indigo-600 flex items-center gap-1.5 border border-white/90 shadow-sm capitalize"
                >
                  <span>⚡</span>
                  <span>{k}</span>
                </a>
              ))}
              {!profile?.portfolio_url && !profile?.linkedin_url && !profile?.github_url && (
                <span className="text-xs text-slate-500 italic font-semibold">
                  No portfolio or social links synced yet. Click &quot;Auto-Sync from Resume&quot; or &quot;Edit Details&quot; to add.
                </span>
              )}
            </div>
          </div>
        )}
      </section>

      {/* Skills Section */}
      <section className="neo-box p-6 rounded-2xl border border-white/95 shadow-sm space-y-4">
        <div className="flex justify-between items-center pb-3 border-b border-slate-300/80">
          <div>
            <h2 className="text-lg font-black text-slate-900">
              Verified Skills &amp; Competencies ({profile?.skills?.length || 0})
            </h2>
            <p className="text-xs text-slate-600 font-semibold mt-0.5">
              Synced from parsed resume evidence and verified technical skills.
            </p>
          </div>
          <button
            onClick={() => setShowSkillModal(true)}
            className="text-xs font-bold px-3 py-1.5 rounded-xl neo-pill text-indigo-900 hover:text-indigo-600 border border-white/90 shadow-sm"
          >
            + Add Skill
          </button>
        </div>

        <div className="flex flex-wrap gap-2">
          {profile?.skills && profile.skills.length > 0 ? (
            profile.skills.map((skill) => (
              <span
                key={skill.id}
                className="px-3 py-1.5 neo-pill rounded-xl text-xs font-bold text-slate-900 border border-white/90 shadow-sm flex items-center space-x-2"
              >
                <span>{skill.skill_name}</span>
                <span className="text-[10px] font-mono text-indigo-700 bg-indigo-50 px-1.5 py-0.5 rounded-md">
                  {skill.proficiency}
                </span>
                <button
                  type="button"
                  onClick={() => handleDeleteSkill(skill.id)}
                  className="text-slate-400 hover:text-rose-600 font-bold ml-1"
                >
                  ×
                </button>
              </span>
            ))
          ) : (
            <p className="text-xs text-slate-600 italic font-semibold">
              No skills synced yet. Upload a resume to automatically extract your full skill inventory.
            </p>
          )}
        </div>
      </section>

      {/* Experience Section */}
      <section className="neo-box p-6 rounded-2xl border border-white/95 shadow-sm space-y-4">
        <div className="flex justify-between items-center pb-3 border-b border-slate-300/80">
          <div>
            <h2 className="text-lg font-black text-slate-900">
              Work Experience ({profile?.experience?.length || 0})
            </h2>
            <p className="text-xs text-slate-600 font-semibold mt-0.5">
              Professional roles and verified engineering accomplishments.
            </p>
          </div>
          <button
            onClick={() => setShowExpModal(true)}
            className="text-xs font-bold px-3 py-1.5 rounded-xl neo-pill text-indigo-900 hover:text-indigo-600 border border-white/90 shadow-sm"
          >
            + Add Role
          </button>
        </div>

        <div className="space-y-4">
          {profile?.experience && profile.experience.length > 0 ? (
            profile.experience.map((exp) => (
              <div
                key={exp.id}
                className="p-4 rounded-xl neo-card border border-white/90 flex justify-between items-start"
              >
                <div className="space-y-1">
                  <h3 className="text-sm font-black text-slate-900">{exp.role}</h3>
                  <p className="text-xs font-bold text-indigo-700">
                    {exp.company} {exp.employment_type && `• ${exp.employment_type}`}
                  </p>
                  {(exp.start_date || exp.end_date) && (
                    <span className="text-[11px] text-slate-600 font-mono font-bold block">
                      {exp.start_date || ""} – {exp.is_current ? "Present" : exp.end_date || ""}
                    </span>
                  )}
                  {exp.description && (
                    <p className="text-xs text-slate-700 font-medium leading-relaxed pt-1">
                      {exp.description}
                    </p>
                  )}
                  {exp.skills && exp.skills.length > 0 && (
                    <div className="flex flex-wrap gap-1 pt-1.5">
                      {exp.skills.map((s, idx) => (
                        <span key={idx} className="text-[10px] px-2 py-0.5 rounded-md bg-indigo-50 text-indigo-900 border border-indigo-200 font-mono font-bold">
                          {s}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
                <button
                  onClick={() => handleDeleteExp(exp.id)}
                  className="text-xs text-rose-600 hover:text-rose-800 font-bold ml-3"
                >
                  Delete
                </button>
              </div>
            ))
          ) : (
            <p className="text-xs text-slate-600 italic font-semibold">
              No experience records yet. Auto-sync from your resume to populate roles automatically.
            </p>
          )}
        </div>
      </section>

      {/* Education Credentials */}
      <section className="neo-box p-6 rounded-2xl border border-white/95 shadow-sm space-y-4">
        <div className="flex justify-between items-center pb-3 border-b border-slate-300/80">
          <div>
            <h2 className="text-lg font-black text-slate-900">
              Education Credentials ({profile?.education?.length || 0})
            </h2>
            <p className="text-xs text-slate-600 font-semibold mt-0.5">
              Degrees, university credentials, and academic background.
            </p>
          </div>
          <button
            onClick={() => setShowEduModal(true)}
            className="text-xs font-bold px-3 py-1.5 rounded-xl neo-pill text-indigo-900 hover:text-indigo-600 border border-white/90 shadow-sm"
          >
            + Add Education
          </button>
        </div>

        <div className="space-y-3">
          {profile?.education && profile.education.length > 0 ? (
            profile.education.map((edu) => (
              <div
                key={edu.id}
                className="p-4 rounded-xl neo-card border border-white/90 flex justify-between items-start"
              >
                <div>
                  <h3 className="text-sm font-black text-slate-900">{edu.institution}</h3>
                  <p className="text-xs font-bold text-indigo-700">
                    {edu.degree} in {edu.field_of_study}
                  </p>
                  {(edu.start_date || edu.end_date) && (
                    <span className="text-[11px] text-slate-600 font-mono font-bold block mt-0.5">
                      {edu.start_date || ""} – {edu.end_date || ""}
                    </span>
                  )}
                </div>
                <button
                  onClick={() => handleDeleteEdu(edu.id)}
                  className="text-xs text-rose-600 hover:text-rose-800 font-bold"
                >
                  Delete
                </button>
              </div>
            ))
          ) : (
            <p className="text-xs text-slate-600 italic font-semibold">
              No education credentials added yet.
            </p>
          )}
        </div>
      </section>

      {/* Add Education Modal */}
      {showEduModal && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="neo-box max-w-md w-full p-6 rounded-2xl border border-white/95 shadow-xl space-y-4">
            <h3 className="text-base font-black text-slate-900">Add Education Credential</h3>
            <form onSubmit={handleAddEdu} className="space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase text-slate-700 mb-1">Institution</label>
                <input
                  type="text"
                  required
                  value={eduInst}
                  onChange={(e) => setEduInst(e.target.value)}
                  placeholder="e.g. Stanford University"
                  className="w-full px-3 py-2 neo-inset rounded-xl text-xs sm:text-sm text-slate-900 font-semibold border border-slate-300/80"
                />
              </div>
              <div>
                <label className="block text-xs font-bold uppercase text-slate-700 mb-1">Degree</label>
                <input
                  type="text"
                  required
                  value={eduDegree}
                  onChange={(e) => setEduDegree(e.target.value)}
                  placeholder="e.g. B.S. or M.S."
                  className="w-full px-3 py-2 neo-inset rounded-xl text-xs sm:text-sm text-slate-900 font-semibold border border-slate-300/80"
                />
              </div>
              <div>
                <label className="block text-xs font-bold uppercase text-slate-700 mb-1">Field of Study</label>
                <input
                  type="text"
                  required
                  value={eduField}
                  onChange={(e) => setEduField(e.target.value)}
                  placeholder="e.g. Computer Science"
                  className="w-full px-3 py-2 neo-inset rounded-xl text-xs sm:text-sm text-slate-900 font-semibold border border-slate-300/80"
                />
              </div>
              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowEduModal(false)}
                  className="px-4 py-2 neo-pill rounded-xl text-xs font-bold text-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="neo-btn-primary px-4 py-2 rounded-xl text-xs font-bold shadow-md"
                >
                  Save Credential
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add Experience Modal */}
      {showExpModal && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="neo-box max-w-md w-full p-6 rounded-2xl border border-white/95 shadow-xl space-y-4">
            <h3 className="text-base font-black text-slate-900">Add Professional Role</h3>
            <form onSubmit={handleAddExp} className="space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase text-slate-700 mb-1">Role Title</label>
                <input
                  type="text"
                  required
                  value={expRole}
                  onChange={(e) => setExpRole(e.target.value)}
                  placeholder="e.g. Senior Software Engineer"
                  className="w-full px-3 py-2 neo-inset rounded-xl text-xs sm:text-sm text-slate-900 font-semibold border border-slate-300/80"
                />
              </div>
              <div>
                <label className="block text-xs font-bold uppercase text-slate-700 mb-1">Company Name</label>
                <input
                  type="text"
                  required
                  value={expCompany}
                  onChange={(e) => setExpCompany(e.target.value)}
                  placeholder="e.g. Stripe, Google, Acme Inc."
                  className="w-full px-3 py-2 neo-inset rounded-xl text-xs sm:text-sm text-slate-900 font-semibold border border-slate-300/80"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold uppercase text-slate-700 mb-1">Start Date</label>
                  <input
                    type="text"
                    value={expStart}
                    onChange={(e) => setExpStart(e.target.value)}
                    placeholder="2021"
                    className="w-full px-3 py-2 neo-inset rounded-xl text-xs text-slate-900 font-semibold border border-slate-300/80"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase text-slate-700 mb-1">End Date</label>
                  <input
                    type="text"
                    value={expEnd}
                    onChange={(e) => setExpEnd(e.target.value)}
                    placeholder="Present"
                    className="w-full px-3 py-2 neo-inset rounded-xl text-xs text-slate-900 font-semibold border border-slate-300/80"
                  />
                </div>
              </div>
              <div>
                <label className="block text-xs font-bold uppercase text-slate-700 mb-1">Description</label>
                <textarea
                  rows={3}
                  value={expDesc}
                  onChange={(e) => setExpDesc(e.target.value)}
                  placeholder="Key contributions and systems built."
                  className="w-full px-3 py-2 neo-inset rounded-xl text-xs text-slate-900 font-semibold border border-slate-300/80"
                />
              </div>
              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowExpModal(false)}
                  className="px-4 py-2 neo-pill rounded-xl text-xs font-bold text-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="neo-btn-primary px-4 py-2 rounded-xl text-xs font-bold shadow-md"
                >
                  Save Role
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add Skill Modal */}
      {showSkillModal && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="neo-box max-w-sm w-full p-6 rounded-2xl border border-white/95 shadow-xl space-y-4">
            <h3 className="text-base font-black text-slate-900">Add Skill</h3>
            <form onSubmit={handleAddSkill} className="space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase text-slate-700 mb-1">Skill Name</label>
                <input
                  type="text"
                  required
                  value={skillName}
                  onChange={(e) => setSkillName(e.target.value)}
                  placeholder="e.g. Python, Docker, Next.js"
                  className="w-full px-3 py-2 neo-inset rounded-xl text-xs sm:text-sm text-slate-900 font-semibold border border-slate-300/80"
                />
              </div>
              <div>
                <label className="block text-xs font-bold uppercase text-slate-700 mb-1">Proficiency</label>
                <select
                  value={skillProf}
                  onChange={(e) => setSkillProf(e.target.value)}
                  className="w-full px-3 py-2 neo-inset rounded-xl text-xs sm:text-sm text-slate-900 font-semibold border border-slate-300/80"
                >
                  <option value="Beginner">Beginner</option>
                  <option value="Intermediate">Intermediate</option>
                  <option value="Expert">Expert</option>
                </select>
              </div>
              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowSkillModal(false)}
                  className="px-4 py-2 neo-pill rounded-xl text-xs font-bold text-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="neo-btn-primary px-4 py-2 rounded-xl text-xs font-bold shadow-md"
                >
                  Add Skill
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
