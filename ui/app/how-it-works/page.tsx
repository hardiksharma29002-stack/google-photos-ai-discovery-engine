"use client";

import Link from "next/link";

export default function HowItWorksPage() {
  return (
    <div className="space-y-10 pb-20 max-w-5xl mx-auto">
      {/* Header */}
      <div>
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 border border-blue-100 text-blue-700 text-xs font-semibold mb-3">
          <span className="w-2 h-2 rounded-full bg-blue-600"></span>
          System Architecture & Pipeline Specification
        </div>
        <h1 className="text-3xl font-extrabold text-[#1F2937] tracking-tight">
          How the Discovery Engine Works
        </h1>
        <p className="text-gray-500 mt-2 text-sm leading-relaxed max-w-3xl">
          An offline-first, AI-powered discovery pipeline that transforms thousands of noisy public user reviews into validated product opportunities for Google Photos Core Experience team.
        </p>
      </div>

      {/* ONE-SLIDE EXECUTIVE SUMMARY CARD */}
      <div className="bg-gradient-to-r from-blue-900 to-indigo-900 text-white rounded-2xl p-7 shadow-lg relative overflow-hidden">
        <div className="absolute right-0 top-0 translate-x-8 -translate-y-8 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl pointer-events-none"></div>
        <div className="flex items-center justify-between border-b border-white/10 pb-4 mb-5">
          <div className="text-xs uppercase tracking-widest font-bold text-blue-300">
            One-Slide Ready • Product Discovery Blueprint
          </div>
          <div className="text-xs text-blue-200 font-mono">
            Core Target: 4,615 Cases Grounded
          </div>
        </div>
        <h2 className="text-2xl font-black text-white mb-3 leading-snug">
          "Turn 174,000+ Raw Public Reviews Into Verified Product Opportunity Maps in Sub-2-Second Responses"
        </h2>
        <p className="text-sm text-blue-100/90 leading-relaxed max-w-3xl mb-6">
          Evaluators don't need generic sentiment analysis or shallow review summaries. The Discovery Engine reconstructs the user's mental model: what they remembered, what they forgot, how they formulated their search query, where the system failed, and what workarounds they attempted.
        </p>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-4 border-t border-white/10">
          <div>
            <div className="text-2xl font-black text-white">174,040</div>
            <div className="text-xs text-blue-300">Raw Reviews Filtered</div>
          </div>
          <div>
            <div className="text-2xl font-black text-emerald-400">4,615</div>
            <div className="text-xs text-blue-300">High-Signal Core Cases</div>
          </div>
          <div>
            <div className="text-2xl font-black text-amber-400">14</div>
            <div className="text-xs text-blue-300">Taxonomy Clusters</div>
          </div>
          <div>
            <div className="text-2xl font-black text-purple-300">&lt; 1.5s</div>
            <div className="text-xs text-blue-300">Query & Load Latency</div>
          </div>
        </div>
      </div>

      {/* 5-STAGE PIPELINE ARCHITECTURE FLOW */}
      <div className="space-y-4">
        <h3 className="text-lg font-bold text-gray-900">
          End-to-End Pipeline Architecture
        </h3>
        <p className="text-xs text-gray-500">
          Strict offline-pipeline → precomputed-serving separation. Zero LLM calls or scraping on live request paths.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {/* Stage 1 */}
          <div className="card p-5 border-t-4 border-t-blue-500 flex flex-col justify-between">
            <div>
              <div className="text-xs font-mono font-bold text-blue-600 mb-1">STAGE 01</div>
              <h4 className="text-sm font-bold text-gray-900 mb-2">Ingestion & Sourcing</h4>
              <p className="text-xs text-gray-600 leading-relaxed mb-3">
                Scraped 168k Play Store, 5k App Store, and 51 Community posts. Strict rate limits, deduplication, and PII anonymization.
              </p>
            </div>
            <span className="text-[11px] font-mono text-gray-400 bg-gray-50 p-1.5 rounded border border-gray-100">
              174,040 Raw Items
            </span>
          </div>

          {/* Stage 2 */}
          <div className="card p-5 border-t-4 border-t-cyan-500 flex flex-col justify-between">
            <div>
              <div className="text-xs font-mono font-bold text-cyan-600 mb-1">STAGE 02</div>
              <h4 className="text-sm font-bold text-gray-900 mb-2">Regex Prefilter</h4>
              <p className="text-xs text-gray-600 leading-relaxed mb-3">
                35+ seed retrieval phrases discard off-topic storage, pricing, and backup noise while keeping recall high.
              </p>
            </div>
            <span className="text-[11px] font-mono text-gray-400 bg-gray-50 p-1.5 rounded border border-gray-100">
              35,210 Filtered Pool
            </span>
          </div>

          {/* Stage 3 */}
          <div className="card p-5 border-t-4 border-t-indigo-500 flex flex-col justify-between">
            <div>
              <div className="text-xs font-mono font-bold text-indigo-600 mb-1">STAGE 03</div>
              <h4 className="text-sm font-bold text-gray-900 mb-2">Schema Extraction</h4>
              <p className="text-xs text-gray-600 leading-relaxed mb-3">
                Gemini 2.5 Flash extracts photo types, clues remembered/forgotten, search formulation, and verbatim evidence quotes.
              </p>
            </div>
            <span className="text-[11px] font-mono text-gray-400 bg-gray-50 p-1.5 rounded border border-gray-100">
              4,615 High-Signal Cases
            </span>
          </div>

          {/* Stage 4 */}
          <div className="card p-5 border-t-4 border-t-amber-500 flex flex-col justify-between">
            <div>
              <div className="text-xs font-mono font-bold text-amber-600 mb-1">STAGE 04</div>
              <h4 className="text-sm font-bold text-gray-900 mb-2">Opportunity Scoring</h4>
              <p className="text-xs text-gray-600 leading-relaxed mb-3">
                Clusters ranked by mathematical opportunity formula: Frequency Share × Severity × Unresolved Factor × Recency Weight.
              </p>
            </div>
            <span className="text-[11px] font-mono text-gray-400 bg-gray-50 p-1.5 rounded border border-gray-100">
              14 Problem Clusters
            </span>
          </div>

          {/* Stage 5 */}
          <div className="card p-5 border-t-4 border-t-emerald-500 flex flex-col justify-between">
            <div>
              <div className="text-xs font-mono font-bold text-emerald-600 mb-1">STAGE 05</div>
              <h4 className="text-sm font-bold text-gray-900 mb-2">RAG & Serving</h4>
              <p className="text-xs text-gray-600 leading-relaxed mb-3">
                Next.js web application with precomputed in-memory indices, real-time SSE streaming chat, and zero cold-start delay.
              </p>
            </div>
            <span className="text-[11px] font-mono text-gray-400 bg-gray-50 p-1.5 rounded border border-gray-100">
              Sub-2s Web Response
            </span>
          </div>
        </div>
      </div>

      {/* CORE DESIGN PRINCIPLES & TRUST SAFEGUARDS */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card space-y-4">
          <div className="flex items-center gap-2">
            <span className="w-8 h-8 rounded-lg bg-red-50 text-red-600 font-bold flex items-center justify-center text-sm">
              🛡️
            </span>
            <h4 className="font-bold text-gray-900 text-sm">
              Untrusted Data & Prompt-Injection Defense
            </h4>
          </div>
          <p className="text-xs text-gray-600 leading-relaxed">
            All scraped reviews and community questions are treated as completely untrusted input. The extraction prompts isolate user review content within strict XML demarcation blocks and forbid following instructions contained within review text. No personal names or account IDs are ever stored or exposed.
          </p>
          <div className="bg-gray-50 p-3 rounded-lg border border-gray-100 text-[11px] font-mono text-gray-700">
            • Strict JSON-schema constraints<br/>
            • Evidence quote verified by exact substring match in Python<br/>
            • PII stripped or hashed before indexing
          </div>
        </div>

        <div className="card space-y-4">
          <div className="flex items-center gap-2">
            <span className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 font-bold flex items-center justify-center text-sm">
              ⚡
            </span>
            <h4 className="font-bold text-gray-900 text-sm">
              Zero Latency & Cost Optimization
            </h4>
          </div>
          <p className="text-xs text-gray-600 leading-relaxed">
            By running heavy extraction, deduplication, and clustering offline in batch, the web application runs entirely off verified static JSON indices. This eliminates cold starts, guarantees sub-2-second loads, avoids LLM rate limit crashes, and allows evaluators to explore all data for free.
          </p>
          <div className="bg-gray-50 p-3 rounded-lg border border-gray-100 text-[11px] font-mono text-gray-700">
            • Instant in-memory JSON aggregations<br/>
            • SSE token streaming for AI assistant responses<br/>
            • Dual-model fallback (Gemini 2.5 Flash + Groq LLaMA)
          </div>
        </div>
      </div>

      {/* CALL TO ACTION */}
      <div className="flex items-center justify-between p-6 bg-blue-50 rounded-2xl border border-blue-200">
        <div>
          <h4 className="font-bold text-blue-950 text-base">
            Want to see the data quality audit & verification results?
          </h4>
          <p className="text-xs text-blue-700 mt-1">
            Review the 100-item stratified audit, precision/recall metrics, and inter-model agreement scores.
          </p>
        </div>
        <Link
          href="/trust"
          className="px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-xl transition-all shadow-sm shrink-0"
        >
          View Trust & Limits →
        </Link>
      </div>
    </div>
  );
}
