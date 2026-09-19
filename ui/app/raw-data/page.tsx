"use client";

import { useEffect, useState, useMemo } from "react";

// Official Google Play 4-color SVG logo
const PlayStoreIcon = ({ className = "w-4 h-4" }: { className?: string }) => (
  <svg viewBox="0 0 24 24" className={className}>
    <path fill="#4285F4" d="M3.6 1.8C3.2 2.2 3 2.8 3 3.6v16.8c0 .8.2 1.4.6 1.8l.1.1 9.4-9.4v-.2L3.6 1.8z"/>
    <path fill="#FBBC04" d="M16.2 15.3l-3.1-3.1v-.4l3.1-3.1.1.1 3.7 2.1c1.1.6 1.1 1.6 0 2.2l-3.8 2.2z"/>
    <path fill="#EA4335" d="M16.3 15.2L13.1 12 3.6 22.3c.4.4 1 .4 1.7 0l11-6.3"/>
    <path fill="#34A853" d="M16.3 8.8L5.3 2.5C4.6 2.1 4 2.1 3.6 2.5L13.1 12l3.2-3.2z"/>
  </svg>
);

const AppStoreIcon = ({ className = "w-4 h-4" }: { className?: string }) => (
  <svg viewBox="0 0 512 512" className={className} fill="none">
    <rect width="512" height="512" rx="115" fill="#0D96F6"/>
    <path d="M288.7 326.6l-32.7-56.7-32.7 56.7h65.4z" fill="#FFFFFF"/>
    <path d="M381.8 410.8l-40.2-69.6h-34.9l40.2 69.6c4.6 8 13.1 13 22.3 13h46.2c-12.7 0-24.8-4.8-33.6-13z" fill="#FFFFFF" opacity="0.7"/>
    <path d="M393.7 377.2L282.4 184.4c-8.9-15.4-25.2-24.8-43-24.8s-34.1 9.4-43 24.8L85.1 377.2c-5.8 10-5.8 22.4 0 32.4 5.8 10 16.5 16.2 28.1 16.2h285.6c11.6 0 22.3-6.2 28.1-16.2 5.8-10 5.8-22.4 0-32.4zm-137.7-147l51.5 89.2H204.5l51.5-89.2z" fill="#FFFFFF"/>
  </svg>
);

const GooglePhotosCommunityIcon = ({ className = "w-4 h-4" }: { className?: string }) => (
  <svg viewBox="0 0 24 24" className={className} fill="none">
    <path d="M12 2C9.24 2 7 4.24 7 7c0 .41.05.81.14 1.19A4.996 4.996 0 0112 7h5c0-2.76-2.24-5-5-5z" fill="#EA4335"/>
    <path d="M22 12c0-2.76-2.24-5-5-5-.41 0-.81.05-1.19.14A4.996 4.996 0 0117 12v5c2.76 0 5-2.24 5-5z" fill="#FBBC04"/>
    <path d="M12 22c2.76 0 5-2.24 5-5 0-.41-.05-.81-.14-1.19A4.996 4.996 0 0112 17H7c0 2.76 2.24 5 5 5z" fill="#34A853"/>
    <path d="M2 12c0 2.76 2.24 5 5 5 .41 0 .81-.05 1.19-.14A4.996 4.996 0 017 12V7C4.24 7 2 9.24 2 12z" fill="#4285F4"/>
  </svg>
);

const PAGE_SIZE = 50;

export default function RawDataPage() {
  const [reviews, setReviews] = useState<any[]>([]);
  const [filter, setFilter] = useState("All");
  const [searchTerm, setSearchTerm] = useState("");
  const [stageFilter, setStageFilter] = useState("All");
  const [severityFilter, setSeverityFilter] = useState("All");
  const [page, setPage] = useState(1);

  useEffect(() => {
    fetch('/data/aggregates/all_reviews.json')
      .then(res => res.ok ? res.json() : [])
      .then(data => setReviews(data))
      .catch(() => setReviews([]));
  }, []);

  const severityCounts = useMemo(() => {
    const counts: Record<string, number> = { Critical: 0, High: 0, Medium: 0, Low: 0 };
    reviews.forEach(r => {
      if (r.severity && counts[r.severity] !== undefined) {
        counts[r.severity]++;
      }
    });
    return counts;
  }, [reviews]);

  const uniqueStages = useMemo(() => {
    const s = new Set<string>();
    reviews.forEach(r => { 
      const st = r.failure_stage || r.stage;
      if (st) s.add(st); 
    });
    return Array.from(s).sort();
  }, [reviews]);

  const filteredReviews = useMemo(() => {
    return reviews.filter(r => {
      // Source filter
      if (filter !== "All" && r.source !== filter) return false;
      // Severity filter
      if (severityFilter !== "All" && r.severity !== severityFilter) return false;
      // Stage filter
      const currentStage = r.failure_stage || r.stage;
      if (stageFilter !== "All" && currentStage !== stageFilter) return false;
      // Search keyword filter
      if (searchTerm.trim()) {
        const query = searchTerm.toLowerCase();
        const matchesText = r.text?.toLowerCase().includes(query);
        const matchesIntent = r.intent?.toLowerCase().includes(query);
        const matchesStage = currentStage?.toLowerCase().includes(query);
        const matchesId = r.id?.toLowerCase().includes(query);
        const matchesSeverity = r.severity?.toLowerCase().includes(query);
        if (!matchesText && !matchesIntent && !matchesStage && !matchesId && !matchesSeverity) return false;
      }
      return true;
    });
  }, [reviews, filter, severityFilter, stageFilter, searchTerm]);

  const visibleReviews = filteredReviews.slice(0, page * PAGE_SIZE);
  const hasMore = visibleReviews.length < filteredReviews.length;

  return (
    <div className="max-w-6xl mx-auto pt-8 pb-20 space-y-6">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold text-[#1F2937]">Raw Data Repository</h2>
          <p className="text-gray-500 mt-2 text-sm max-w-2xl leading-relaxed">
            Browse {reviews.length.toLocaleString()} authentic, non-template public reviews collected from Google Play, Apple App Store, and Google Photos Community.
            Each entry contains genuine user phrasing, identified intent, and categorized failure taxonomy.
          </p>
        </div>

        <div className="bg-blue-50 text-blue-700 px-4 py-2 rounded-lg font-bold text-sm h-[40px] flex items-center shadow-xs self-start md:self-end">
          {visibleReviews.length.toLocaleString()} / {filteredReviews.length.toLocaleString()} Displayed
        </div>
      </div>

      {/* SEARCH AND FILTERS BAR */}
      <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-xs flex flex-col gap-3">
        {/* ROW 1: Search & Sources */}
        <div className="flex flex-col md:flex-row gap-3 items-center justify-between">
          {/* Keyword Search */}
          <div className="relative w-full md:w-96">
            <input
              type="text"
              placeholder="Search reviews by keyword (e.g., 'dog', 'gemini', 'date')..."
              value={searchTerm}
              onChange={(e) => { setSearchTerm(e.target.value); setPage(1); }}
              className="w-full pl-9 pr-4 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <svg className="w-4 h-4 text-gray-400 absolute left-3 top-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
            </svg>
            {searchTerm && (
              <button
                onClick={() => { setSearchTerm(""); setPage(1); }}
                className="absolute right-3 top-2.5 text-xs text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            )}
          </div>

          {/* Source Toggle */}
          <div className="flex items-center gap-2 w-full md:w-auto justify-between md:justify-end">
            <div className="flex bg-gray-100 rounded-lg p-1 text-xs font-bold">
              <button
                onClick={() => { setFilter("All"); setPage(1); }}
                className={`px-3 py-1.5 rounded-md transition-all ${filter === "All" ? "bg-white text-gray-900 shadow-xs" : "text-gray-600 hover:text-gray-900"}`}
              >
                All Sources
              </button>
              <button
                onClick={() => { setFilter("Play Store"); setPage(1); }}
                className={`px-3 py-1.5 rounded-md flex items-center gap-1.5 transition-all ${filter === "Play Store" ? "bg-white text-emerald-700 shadow-xs" : "text-gray-600 hover:text-gray-900"}`}
              >
                <PlayStoreIcon className="w-3.5 h-3.5" />
                Play Store
              </button>
              <button
                onClick={() => { setFilter("App Store"); setPage(1); }}
                className={`px-3 py-1.5 rounded-md flex items-center gap-1.5 transition-all ${filter === "App Store" ? "bg-white text-blue-700 shadow-xs" : "text-gray-600 hover:text-gray-900"}`}
              >
                <AppStoreIcon className="w-3.5 h-3.5" />
                App Store
              </button>
              <button
                onClick={() => { setFilter("Google Photos Community"); setPage(1); }}
                className={`px-3 py-1.5 rounded-md flex items-center gap-1.5 transition-all ${filter === "Google Photos Community" ? "bg-white text-amber-700 shadow-xs" : "text-gray-600 hover:text-gray-900"}`}
              >
                <GooglePhotosCommunityIcon className="w-3.5 h-3.5" />
                Community
              </button>
            </div>
          </div>
        </div>

        {/* ROW 2: Severity Filters & Cluster Dropdown */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-gray-100">
          {/* Severity Filter Pills */}
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs font-bold text-gray-500 uppercase tracking-wider mr-1">Severity:</span>
            <div className="flex bg-gray-100 rounded-lg p-1 text-xs font-bold">
              <button
                onClick={() => { setSeverityFilter("All"); setPage(1); }}
                className={`px-2.5 py-1 rounded-md transition-all ${severityFilter === "All" ? "bg-white text-gray-900 shadow-xs font-black" : "text-gray-600 hover:text-gray-900"}`}
              >
                All
              </button>
              <button
                onClick={() => { setSeverityFilter("Critical"); setPage(1); }}
                className={`px-2.5 py-1 rounded-md flex items-center gap-1.5 transition-all ${
                  severityFilter === "Critical"
                    ? "bg-red-600 text-white shadow-xs font-black"
                    : "text-red-700 hover:bg-red-50"
                }`}
              >
                <span className={`w-2 h-2 rounded-full ${severityFilter === "Critical" ? "bg-white" : "bg-red-500"}`}></span>
                Critical ({severityCounts.Critical.toLocaleString()})
              </button>
              <button
                onClick={() => { setSeverityFilter("High"); setPage(1); }}
                className={`px-2.5 py-1 rounded-md flex items-center gap-1.5 transition-all ${
                  severityFilter === "High"
                    ? "bg-orange-600 text-white shadow-xs font-black"
                    : "text-orange-700 hover:bg-orange-50"
                }`}
              >
                <span className={`w-2 h-2 rounded-full ${severityFilter === "High" ? "bg-white" : "bg-orange-500"}`}></span>
                High ({severityCounts.High.toLocaleString()})
              </button>
              <button
                onClick={() => { setSeverityFilter("Medium"); setPage(1); }}
                className={`px-2.5 py-1 rounded-md flex items-center gap-1.5 transition-all ${
                  severityFilter === "Medium"
                    ? "bg-yellow-600 text-white shadow-xs font-black"
                    : "text-yellow-700 hover:bg-yellow-50"
                }`}
              >
                <span className={`w-2 h-2 rounded-full ${severityFilter === "Medium" ? "bg-white" : "bg-yellow-500"}`}></span>
                Medium ({severityCounts.Medium.toLocaleString()})
              </button>
              <button
                onClick={() => { setSeverityFilter("Low"); setPage(1); }}
                className={`px-2.5 py-1 rounded-md flex items-center gap-1.5 transition-all ${
                  severityFilter === "Low"
                    ? "bg-emerald-600 text-white shadow-xs font-black"
                    : "text-emerald-700 hover:bg-emerald-50"
                }`}
              >
                <span className={`w-2 h-2 rounded-full ${severityFilter === "Low" ? "bg-white" : "bg-emerald-500"}`}></span>
                Low ({severityCounts.Low.toLocaleString()})
              </button>
            </div>
          </div>

          {/* Cluster Dropdown & Clear Filters */}
          <div className="flex items-center gap-2">
            <select
              value={stageFilter}
              onChange={(e) => { setStageFilter(e.target.value); setPage(1); }}
              className="text-xs font-medium border border-gray-200 rounded-lg px-3 py-1.5 bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-2xs"
            >
              <option value="All">All 14 Clusters</option>
              {uniqueStages.map(s => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>

            {(filter !== "All" || stageFilter !== "All" || severityFilter !== "All" || searchTerm) && (
              <button
                onClick={() => {
                  setFilter("All");
                  setStageFilter("All");
                  setSeverityFilter("All");
                  setSearchTerm("");
                  setPage(1);
                }}
                className="text-xs font-bold text-gray-500 hover:text-red-600 bg-gray-100 hover:bg-red-50 px-2.5 py-1.5 rounded-lg transition-colors"
                title="Clear all active filters"
              >
                Reset Filters
              </button>
            )}
          </div>
        </div>
      </div>

      {/* REVIEWS TABLE */}
      <div className="bg-white border border-gray-200 rounded-xl shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-50/80 border-b border-gray-200 text-xs uppercase tracking-wider text-gray-500 font-bold">
                <th className="p-4 w-24">ID</th>
                <th className="p-4 w-36">Source</th>
                <th className="p-4 w-28">Date</th>
                <th className="p-4 min-w-[340px]">Authentic User Feedback</th>
                <th className="p-4 w-48">AI Intent</th>
                <th className="p-4 w-48">Failure Cluster</th>
                <th className="p-4 w-24">Severity</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {visibleReviews.map((r, i) => (
                <tr key={r.id || i} className="hover:bg-blue-50/20 transition-colors">
                  <td className="p-4 text-xs font-mono text-gray-400">{r.id}</td>
                  <td className="p-4 text-sm font-bold text-gray-700">
                    {r.source === "Play Store" ? (
                      <span className="text-emerald-700 flex items-center gap-1.5">
                        <PlayStoreIcon className="w-4 h-4 shrink-0" />
                        Play Store
                      </span>
                    ) : r.source === "App Store" ? (
                      <span className="text-blue-600 flex items-center gap-1.5">
                        <AppStoreIcon className="w-4 h-4 shrink-0" />
                        App Store
                      </span>
                    ) : (
                      <span className="text-amber-700 flex items-center gap-1.5">
                        <GooglePhotosCommunityIcon className="w-4 h-4 shrink-0" />
                        Community
                      </span>
                    )}
                  </td>
                  <td className="p-4 text-xs text-gray-500 font-mono">{r.date}</td>
                  <td className="p-4 text-sm text-gray-800 leading-relaxed font-sans">
                    &ldquo;{r.text}&rdquo;
                  </td>
                  <td className="p-4 text-xs font-medium text-blue-700 bg-blue-50/40 rounded">
                    {r.intent}
                  </td>
                  <td className="p-4 text-xs font-bold text-gray-700">
                    {r.failure_stage || r.stage}
                  </td>
                  <td className="p-4">
                    <button
                      onClick={() => { setSeverityFilter(r.severity); setPage(1); }}
                      title={`Click to filter by ${r.severity} severity`}
                      className={`px-2.5 py-0.5 text-[11px] font-bold rounded-full cursor-pointer hover:ring-2 hover:ring-offset-1 transition-all ${
                        r.severity === "Critical" ? "bg-red-100 text-red-700 border border-red-200 hover:ring-red-400" :
                        r.severity === "High"     ? "bg-orange-100 text-orange-700 border border-orange-200 hover:ring-orange-400" :
                        r.severity === "Medium"   ? "bg-yellow-100 text-yellow-700 border border-yellow-200 hover:ring-yellow-400" :
                        "bg-emerald-100 text-emerald-700 border border-emerald-200 hover:ring-emerald-400"
                      }`}
                    >
                      {r.severity}
                    </button>
                  </td>
                </tr>
              ))}
              {visibleReviews.length === 0 && (
                <tr>
                  <td colSpan={7} className="p-12 text-center text-gray-500">
                    No matching reviews found for &ldquo;{searchTerm}&rdquo;.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer */}
        {hasMore && (
          <div className="border-t border-gray-200 p-5 flex flex-col items-center gap-2 bg-gray-50/70">
            <p className="text-xs text-gray-500 font-medium">
              Showing <span className="font-bold text-gray-800">{visibleReviews.length}</span> of <span className="font-bold text-gray-800">{filteredReviews.length}</span> unique reviews
            </p>
            <button
              onClick={() => setPage(p => p + 1)}
              className="px-6 py-2 bg-gray-900 text-white font-bold rounded-full text-xs hover:bg-black transition-all shadow-sm cursor-pointer"
            >
              Load Next {Math.min(PAGE_SIZE, filteredReviews.length - visibleReviews.length)} Reviews
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
