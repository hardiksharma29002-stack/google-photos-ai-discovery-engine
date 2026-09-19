"use client";

import { useEffect, useState, Fragment } from "react";

export default function OpportunitiesPage() {
  const [dimensions, setDimensions] = useState<any>(null);
  const [rankings, setRankings] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState<"rankings" | "photos" | "memory" | "compare">("rankings");
  const [expandedCluster, setExpandedCluster] = useState<string | null>(null);
  const [showFormulaModal, setShowFormulaModal] = useState<boolean>(true);
  const [clusterA, setClusterA] = useState<string>("Vague Memory & Natural Language Breakdown");
  const [clusterB, setClusterB] = useState<string>("Document, Receipt & Text (OCR) Inaccuracies");

  useEffect(() => {
    fetch('/data/aggregates/retrieval_dimensions.json')
      .then(res => res.ok ? res.json() : null)
      .then(data => {
        if (data) {
          setDimensions(data);
          setRankings(data.opportunity_rankings || []);
        }
      })
      .catch(err => console.error("Failed to load dimensions:", err));
  }, []);

  const toggleCluster = (clusterName: string) => {
    setExpandedCluster(prev => (prev === clusterName ? null : clusterName));
  };

  return (
    <div className="space-y-8 pb-20">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold text-[#1F2937]">Opportunity Areas & Impact Rankings</h2>
          <p className="text-gray-500 mt-2 text-sm max-w-3xl leading-relaxed">
            Prioritizing retrieval problems using transparent, data-backed Opportunity Scoring grounded in 4,615 verified user reviews.
          </p>
        </div>

        {/* View Switcher */}
        <div className="flex bg-gray-100 p-1 rounded-xl text-xs font-bold shrink-0 overflow-x-auto max-w-full scrollbar-none">
          <button
            onClick={() => setActiveTab("rankings")}
            className={`px-3 py-1.5 rounded-lg whitespace-nowrap transition-all ${
              activeTab === "rankings" ? "bg-white text-blue-700 shadow-xs" : "text-gray-600 hover:text-gray-900"
            }`}
          >
            Opportunity Rankings
          </button>
          <button
            onClick={() => setActiveTab("photos")}
            className={`px-3 py-1.5 rounded-lg whitespace-nowrap transition-all ${
              activeTab === "photos" ? "bg-white text-blue-700 shadow-xs" : "text-gray-600 hover:text-gray-900"
            }`}
          >
            Photo Types
          </button>
          <button
            onClick={() => setActiveTab("memory")}
            className={`px-3 py-1.5 rounded-lg whitespace-nowrap transition-all ${
              activeTab === "memory" ? "bg-white text-blue-700 shadow-xs" : "text-gray-600 hover:text-gray-900"
            }`}
          >
            Memory & Formulation
          </button>
          <button
            onClick={() => setActiveTab("compare")}
            className={`px-3 py-1.5 rounded-lg whitespace-nowrap transition-all ${
              activeTab === "compare" ? "bg-white text-blue-700 shadow-xs" : "text-gray-600 hover:text-gray-900"
            }`}
          >
            Compare Problems
          </button>
        </div>
      </div>

      {/* TAB 1: RANKED OPPORTUNITY AREAS TABLE WITH FORMULA (i) INFO */}
      {activeTab === "rankings" && (
        <div className="space-y-6">
          {/* FORMULA & METHODOLOGY (i) EXPLANATION CARD */}
          <div className="bg-blue-50/60 border border-blue-200/80 rounded-2xl p-5 text-xs text-gray-800 shadow-xs">
            <div className="flex items-center justify-between cursor-pointer" onClick={() => setShowFormulaModal(!showFormulaModal)}>
              <div className="flex items-center gap-2.5">
                <span className="w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-xs shrink-0">
                  i
                </span>
                <span className="font-bold text-sm text-blue-950">
                  How Opportunity Score is Calculated
                </span>
              </div>
              <button className="text-xs font-bold text-blue-700 hover:underline">
                {showFormulaModal ? "Collapse Details" : "Show Calculation Formula"}
              </button>
            </div>

            {showFormulaModal && (
              <div className="mt-4 pt-4 border-t border-blue-200/60 space-y-3.5">
                <div className="bg-white p-3 rounded-xl border border-blue-100 font-mono text-xs text-blue-900 font-bold overflow-x-auto">
                  Opportunity Score = Frequency Share × (Avg Severity / 3) × Unresolved Factor × Recency Weight (0.95) × 400
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 pt-1">
                  <div className="bg-white/80 p-3 rounded-xl border border-blue-100">
                    <div className="font-bold text-blue-900">1. Frequency Share</div>
                    <p className="text-[11px] text-gray-600 mt-1 leading-normal">
                      Percentage of the 4,615 public reviews belonging to this cluster. Higher share = wider user impact.
                    </p>
                  </div>
                  <div className="bg-white/80 p-3 rounded-xl border border-blue-100">
                    <div className="font-bold text-blue-900">2. Average Severity</div>
                    <p className="text-[11px] text-gray-600 mt-1 leading-normal">
                      Scaled 1.0 to 3.0 (1 = Minor Friction, 2 = High Friction, 3 = Critical Blocker / Abandoned).
                    </p>
                  </div>
                  <div className="bg-white/80 p-3 rounded-xl border border-blue-100">
                    <div className="font-bold text-blue-900">3. Unresolved Factor</div>
                    <p className="text-[11px] text-gray-600 mt-1 leading-normal">
                      Proportion of users who could not find their photos even after attempting workarounds (1.0 vs 0.6).
                    </p>
                  </div>
                  <div className="bg-white/80 p-3 rounded-xl border border-blue-100">
                    <div className="font-bold text-blue-900">4. Recency Weight</div>
                    <p className="text-[11px] text-gray-600 mt-1 leading-normal">
                      Fixed at 0.95 to prioritize active regressions and recent 24-month feedback.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* TABLE OF ALL 14 CLUSTERS */}
          <div className="bg-white border border-gray-200 rounded-2xl shadow-xs overflow-hidden">
            <div className="p-5 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
              <div>
                <h3 className="font-bold text-gray-800 text-sm">All 14 Retrieval Problems Ranked by Opportunity Score</h3>
                <p className="text-xs text-gray-500 mt-0.5">
                  Click any row to inspect authentic user feedback quotes and intent breakdown
                </p>
              </div>
              <span className="text-xs font-bold text-blue-700 bg-blue-50 px-3 py-1 rounded-full">
                4,615 reviews analyzed
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-sm">
                <thead>
                  <tr className="bg-gray-50/80 border-b border-gray-200 text-xs uppercase tracking-wider text-gray-500 font-bold">
                    <th className="p-4 w-16 text-center">Rank</th>
                    <th className="p-4 min-w-[280px]">Retrieval Problem Cluster</th>
                    <th className="p-4 text-center">Opportunity Score</th>
                    <th className="p-4 text-center">Reviews</th>
                    <th className="p-4 text-center">Share</th>
                    <th className="p-4 text-center">Avg Severity</th>
                    <th className="p-4 text-center">Unresolved</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {rankings.map((r, idx) => {
                    const isExpanded = expandedCluster === r.cluster;

                    return (
                      <Fragment key={r.cluster}>
                        <tr
                          onClick={() => toggleCluster(r.cluster)}
                          className={`cursor-pointer transition-colors ${
                            isExpanded ? "bg-blue-50/40" : "hover:bg-gray-50/80"
                          }`}
                        >
                          <td className="p-4 text-center font-bold text-gray-400">{idx + 1}</td>
                          <td className="p-4 font-semibold text-gray-900 flex items-center gap-2">
                            <span>{r.cluster}</span>
                            <span className="text-[10px] text-blue-600 bg-blue-50 px-1.5 py-0.5 rounded font-mono">
                              {isExpanded ? "▲ close" : "▼ quotes"}
                            </span>
                          </td>
                          <td className="p-4 text-center">
                            <span className="inline-block bg-blue-50 text-blue-700 font-black px-2.5 py-1 rounded-lg text-xs border border-blue-100">
                              {r.opportunity_score}
                            </span>
                          </td>
                          <td className="p-4 text-center font-bold text-gray-700">{r.total_reviews}</td>
                          <td className="p-4 text-center text-gray-500">{r.frequency_share_pct}%</td>
                          <td className="p-4 text-center font-medium text-amber-700">{r.avg_severity} / 3</td>
                          <td className="p-4 text-center">
                            <span className="text-red-600 font-bold text-xs">{r.unresolved_rate_pct}%</span>
                          </td>
                        </tr>

                        {isExpanded && (
                          <tr key={`${r.cluster}-expanded`} className="bg-slate-50/70 border-b border-gray-200">
                            <td colSpan={7} className="p-5">
                              <div className="space-y-3">
                                <div className="flex items-center justify-between">
                                  <div className="text-xs font-bold uppercase tracking-wider text-gray-600">
                                    Real User Evidence Quotes for "{r.cluster}"
                                  </div>
                                  <span className="text-xs text-gray-400">
                                    {r.sample_quotes?.length || 0} sample quotes
                                  </span>
                                </div>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                  {r.sample_quotes?.map((q: any, qIdx: number) => (
                                    <div
                                      key={qIdx}
                                      className="bg-white p-3.5 rounded-xl border border-gray-200 shadow-2xs text-xs text-gray-700 leading-relaxed flex flex-col justify-between gap-2"
                                    >
                                      <div className="italic">
                                        "{q.text}"
                                      </div>
                                      <div className="flex items-center gap-2 pt-1 border-t border-gray-100 not-italic text-[10px]">
                                        <span className="font-semibold text-gray-600 bg-gray-100 px-2 py-0.5 rounded">
                                          {q.source}
                                        </span>
                                        {q.intent && (
                                          <span className="text-blue-600 bg-blue-50 px-2 py-0.5 rounded">
                                            Intent: {q.intent}
                                          </span>
                                        )}
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            </td>
                          </tr>
                        )}
                      </Fragment>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: PHOTO TYPES BREAKDOWN */}
      {activeTab === "photos" && dimensions && (
        <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-xs space-y-6">
          <div>
            <h3 className="text-lg font-bold text-gray-900">What Kinds of Old Photos Do Users Struggle to Retrieve?</h3>
            <p className="text-xs text-gray-500 mt-1">
              Distribution of user photo subjects and categories across the 4,615 retrieval complaints.
            </p>
          </div>

          <div className="space-y-3.5">
            {dimensions.photo_types?.map((pt: any) => (
              <div key={pt.type} className="p-4 bg-gray-50/80 rounded-xl border border-gray-100 flex flex-col gap-2">
                <div className="flex justify-between items-center text-sm font-semibold text-gray-800">
                  <span>{pt.type}</span>
                  <div className="flex items-center gap-3">
                    <span className="text-xs text-gray-500">{pt.count} reviews</span>
                    <span className="font-bold text-blue-600">{pt.percentage}%</span>
                  </div>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                  <div className="bg-[#1A73E8] h-2 rounded-full transition-all" style={{ width: `${pt.percentage}%` }}></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 3: MEMORY & SEARCH FORMULATION */}
      {activeTab === "memory" && dimensions && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Remembered vs Forgotten */}
          <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-xs space-y-5">
            <div>
              <h3 className="text-base font-bold text-gray-900">What People Remember</h3>
              <p className="text-xs text-gray-500 mt-1">Mental cues users recall when initiating search</p>
            </div>
            <div className="space-y-3">
              {dimensions.clues_remembered?.map((c: any) => (
                <div key={c.clue} className="p-3 bg-emerald-50/60 rounded-xl border border-emerald-100 flex justify-between items-center text-xs">
                  <span className="font-semibold text-emerald-900">{c.clue}</span>
                  <span className="font-bold text-emerald-700">{c.percentage}% ({c.count})</span>
                </div>
              ))}
            </div>

            <div className="pt-4 border-t border-gray-100">
              <h3 className="text-base font-bold text-gray-900">What People Have Forgotten</h3>
              <p className="text-xs text-gray-500 mt-1">Missing information causing query formulation failure</p>
            </div>
            <div className="space-y-3">
              {dimensions.clues_forgotten?.map((c: any) => (
                <div key={c.clue} className="p-3 bg-red-50/60 rounded-xl border border-red-100 flex justify-between items-center text-xs">
                  <span className="font-semibold text-red-900">{c.clue}</span>
                  <span className="font-bold text-red-700">{c.percentage}% ({c.count})</span>
                </div>
              ))}
            </div>
          </div>

          {/* Search Formulation Behaviors */}
          <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-xs space-y-5">
            <div>
              <h3 className="text-base font-bold text-gray-900">How Users Formulate Searches</h3>
              <p className="text-xs text-gray-500 mt-1">
                Observable user tactics when attempting retrieval with incomplete memory
              </p>
            </div>

            <div className="space-y-3.5">
              {dimensions.search_behaviors?.map((b: any) => (
                <div key={b.behavior} className="p-4 bg-gray-50/80 rounded-xl border border-gray-100 flex flex-col gap-2">
                  <div className="flex justify-between items-center text-xs font-semibold text-gray-800">
                    <span>{b.behavior}</span>
                    <span className="font-bold text-blue-600">{b.percentage}% ({b.count})</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                    <div className="bg-blue-600 h-2 rounded-full" style={{ width: `${b.percentage}%` }}></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* TAB 4: COMPARE PROBLEM AREAS SIDE-BY-SIDE */}
      {activeTab === "compare" && rankings.length > 0 && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-xs">
            <h3 className="text-lg font-bold text-gray-900 mb-1">
              Side-by-Side Opportunity & Problem Comparison
            </h3>
            <p className="text-xs text-gray-500 mb-6">
              Directly compare two distinct retrieval breakdown patterns to evaluate reach, friction severity, and product ROI.
            </p>

            {/* Selectors */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-4 bg-gray-50 rounded-xl border border-gray-200 mb-6">
              <div>
                <label className="block text-xs font-bold text-blue-900 uppercase tracking-wider mb-2">
                  Select Problem Area A:
                </label>
                <select
                  value={clusterA}
                  onChange={(e) => setClusterA(e.target.value)}
                  className="w-full bg-white border border-gray-300 rounded-lg p-2.5 text-xs font-semibold text-gray-800 shadow-2xs focus:ring-2 focus:ring-blue-500 outline-none"
                >
                  {rankings.map((r) => (
                    <option key={`a-${r.cluster}`} value={r.cluster}>
                      {r.cluster} (Score: {r.opportunity_score})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-purple-900 uppercase tracking-wider mb-2">
                  Select Problem Area B:
                </label>
                <select
                  value={clusterB}
                  onChange={(e) => setClusterB(e.target.value)}
                  className="w-full bg-white border border-gray-300 rounded-lg p-2.5 text-xs font-semibold text-gray-800 shadow-2xs focus:ring-2 focus:ring-purple-500 outline-none"
                >
                  {rankings.map((r) => (
                    <option key={`b-${r.cluster}`} value={r.cluster}>
                      {r.cluster} (Score: {r.opportunity_score})
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {(() => {
              const dataA = rankings.find((r) => r.cluster === clusterA) || rankings[0];
              const dataB = rankings.find((r) => r.cluster === clusterB) || rankings[1] || rankings[0];

              const scoreA = dataA.opportunity_score || 0;
              const scoreB = dataB.opportunity_score || 0;

              return (
                <div className="space-y-6">
                  {/* Metric Comparison Cards */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Column A */}
                    <div className="border border-blue-200 rounded-xl p-5 bg-blue-50/30 space-y-4">
                      <div className="flex justify-between items-start">
                        <div>
                          <span className="text-[10px] font-bold uppercase tracking-wider text-blue-600 bg-blue-100 px-2 py-0.5 rounded">
                            Problem A
                          </span>
                          <h4 className="font-bold text-gray-900 text-base mt-2">{dataA.cluster}</h4>
                        </div>
                        <div className="text-right">
                          <div className="text-2xl font-black text-blue-700">{dataA.opportunity_score}</div>
                          <div className="text-[10px] text-gray-500 uppercase font-bold">Opp. Score</div>
                        </div>
                      </div>

                      <div className="grid grid-cols-3 gap-2 text-center pt-2 border-t border-blue-100 text-xs">
                        <div className="bg-white p-2.5 rounded-lg border border-blue-100">
                          <span className="text-gray-500 text-[11px] block">Volume</span>
                          <strong className="text-gray-900 text-sm">{dataA.total_reviews}</strong>
                          <span className="text-[10px] text-gray-400 block">({dataA.frequency_share_pct}%)</span>
                        </div>
                        <div className="bg-white p-2.5 rounded-lg border border-blue-100">
                          <span className="text-gray-500 text-[11px] block">Avg Severity</span>
                          <strong className="text-amber-700 text-sm">{dataA.avg_severity} / 3</strong>
                        </div>
                        <div className="bg-white p-2.5 rounded-lg border border-blue-100">
                          <span className="text-gray-500 text-[11px] block">Unresolved</span>
                          <strong className="text-red-600 text-sm">{dataA.unresolved_rate_pct}%</strong>
                        </div>
                      </div>

                      {/* Sample Quotes */}
                      <div className="space-y-2 pt-2">
                        <div className="text-[11px] font-bold text-gray-600 uppercase tracking-wider">
                          Real User Quotes ({dataA.sample_quotes?.length || 0})
                        </div>
                        {dataA.sample_quotes?.slice(0, 2).map((q: any, i: number) => (
                          <div key={i} className="bg-white p-3 rounded-lg border border-gray-200 text-xs text-gray-700 italic">
                            "{q.text}"
                            <div className="text-[10px] text-gray-400 not-italic mt-1">Source: {q.source}</div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Column B */}
                    <div className="border border-purple-200 rounded-xl p-5 bg-purple-50/30 space-y-4">
                      <div className="flex justify-between items-start">
                        <div>
                          <span className="text-[10px] font-bold uppercase tracking-wider text-purple-600 bg-purple-100 px-2 py-0.5 rounded">
                            Problem B
                          </span>
                          <h4 className="font-bold text-gray-900 text-base mt-2">{dataB.cluster}</h4>
                        </div>
                        <div className="text-right">
                          <div className="text-2xl font-black text-purple-700">{dataB.opportunity_score}</div>
                          <div className="text-[10px] text-gray-500 uppercase font-bold">Opp. Score</div>
                        </div>
                      </div>

                      <div className="grid grid-cols-3 gap-2 text-center pt-2 border-t border-purple-100 text-xs">
                        <div className="bg-white p-2.5 rounded-lg border border-purple-100">
                          <span className="text-gray-500 text-[11px] block">Volume</span>
                          <strong className="text-gray-900 text-sm">{dataB.total_reviews}</strong>
                          <span className="text-[10px] text-gray-400 block">({dataB.frequency_share_pct}%)</span>
                        </div>
                        <div className="bg-white p-2.5 rounded-lg border border-purple-100">
                          <span className="text-gray-500 text-[11px] block">Avg Severity</span>
                          <strong className="text-amber-700 text-sm">{dataB.avg_severity} / 3</strong>
                        </div>
                        <div className="bg-white p-2.5 rounded-lg border border-purple-100">
                          <span className="text-gray-500 text-[11px] block">Unresolved</span>
                          <strong className="text-red-600 text-sm">{dataB.unresolved_rate_pct}%</strong>
                        </div>
                      </div>

                      {/* Sample Quotes */}
                      <div className="space-y-2 pt-2">
                        <div className="text-[11px] font-bold text-gray-600 uppercase tracking-wider">
                          Real User Quotes ({dataB.sample_quotes?.length || 0})
                        </div>
                        {dataB.sample_quotes?.slice(0, 2).map((q: any, i: number) => (
                          <div key={i} className="bg-white p-3 rounded-lg border border-gray-200 text-xs text-gray-700 italic">
                            "{q.text}"
                            <div className="text-[10px] text-gray-400 not-italic mt-1">Source: {q.source}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Strategic Comparison Summary */}
                  <div className="bg-gray-50 p-4 rounded-xl border border-gray-200 text-xs text-gray-700 space-y-2">
                    <div className="font-bold text-gray-900 flex items-center gap-2 text-sm">
                      <span>⚖️</span> PM Trade-Off Analysis:
                    </div>
                    <p className="leading-relaxed">
                      {scoreA >= scoreB
                        ? `"${dataA.cluster}" represents a higher strategic opportunity (Score: ${scoreA}) than "${dataB.cluster}" (Score: ${scoreB}). It affects ${(dataA.total_reviews / (dataB.total_reviews || 1)).toFixed(1)}x more users in the corpus with an unresolved failure rate of ${dataA.unresolved_rate_pct}%. Prioritizing this area directly impacts core search abandonment.`
                        : `"${dataB.cluster}" represents a higher strategic opportunity (Score: ${scoreB}) than "${dataA.cluster}" (Score: ${scoreA}). It affects ${(dataB.total_reviews / (dataA.total_reviews || 1)).toFixed(1)}x more users in the corpus with an unresolved failure rate of ${dataB.unresolved_rate_pct}%. Prioritizing this area directly impacts core search abandonment.`}
                    </p>
                  </div>
                </div>
              );
            })()}
          </div>
        </div>
      )}
    </div>
  );
}
