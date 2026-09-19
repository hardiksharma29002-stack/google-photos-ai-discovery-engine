"use client";

import { useState } from "react";

export default function PlaygroundPage() {
  const [input, setInput] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!input.trim()) return;
    setIsAnalyzing(true);
    setResult(null);
    setError(null);
    
    try {
      const response = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: input })
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || "Failed to analyze");
      }
      
      setResult(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const sampleReview = "I know I took a picture of my dog at the beach last summer but no matter what I search, Google Photos won't show it to me. I've tried 'dog beach', 'summer 2023 dog', nothing works. I had to manually scroll back a whole year to find it.";

  const handleSample = () => {
    setInput(sampleReview);
  };

  return (
    <div className="max-w-3xl mx-auto flex flex-col gap-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-[#1F2937] mb-2">Live Test</h1>
        <p className="text-[#6B7280] text-lg">
          Paste real user feedback below to see exactly how our AI categorises search failures.
        </p>
      </div>

      <div className="card shadow-sm">
        <textarea
          className="input-field min-h-[150px] mb-4 resize-y"
          placeholder="e.g. 'I know I took a picture of my dog at the beach last summer but no matter what I search, Google Photos won't show it to me...'"
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        
        <div className="flex justify-between items-center mb-6">
          <button 
            onClick={handleSample} 
            className="text-sm text-blue-500 hover:underline font-medium"
          >
            Try a sample review
          </button>
          <span className="text-sm text-[#9CA3AF]">
            Privacy Note: Nothing you paste here is saved or stored.
          </span>
        </div>

        <div className="flex justify-end">
          <button
            className="btn-primary px-8"
            onClick={handleAnalyze}
            disabled={!input.trim() || isAnalyzing}
          >
            {isAnalyzing ? "Analyzing..." : "Analyze Feedback"}
          </button>
        </div>
      </div>

      {/* Results Section */}
      <div className="mt-4">
        <h3 className="text-lg font-bold text-[#1F2937] mb-4">Analysis Results</h3>
        
        {isAnalyzing ? (
          <div className="card flex items-center justify-center min-h-[120px]">
            <div className="text-[#6B7280] flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></div>
              Processing through Gemini...
            </div>
          </div>
        ) : error ? (
           <div className="card border-red-200 bg-red-50 text-red-600 min-h-[120px] flex items-center justify-center">
             Error: {error}
           </div>
        ) : result ? (
          <div className="card border-0 shadow-lg bg-white/80 backdrop-blur overflow-hidden">
            <div className="border-b border-gray-100 bg-gray-50/50 p-6 flex justify-between items-start">
              <div>
                <div className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-1">Categorized Stage</div>
                <div className="text-2xl font-black text-gray-900">{result.failure_stage || "Unknown"}</div>
              </div>
              <div className="text-right">
                <div className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-1">Severity Rating</div>
                <div className="flex items-center gap-1 justify-end">
                  <span className="text-2xl font-black text-red-500">{result.severity || "?"}</span>
                  <span className="text-gray-400 font-medium">/ 5</span>
                </div>
              </div>
            </div>

            <div className="p-6 space-y-6">
              <div>
                 <div className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Deduced User Intent</div>
                 <div className="text-gray-800 text-lg leading-relaxed">{result.user_intent || "—"}</div>
              </div>
              
              <div className="bg-blue-50/50 border border-blue-100 rounded-xl p-5 relative">
                 <div className="absolute -left-3 -top-3 text-4xl opacity-20">"</div>
                 <div className="text-xs font-bold text-blue-400 uppercase tracking-widest mb-2">Supporting Evidence</div>
                 <div className="text-blue-900 italic font-medium">"{result.evidence_quote || "—"}"</div>
              </div>

              <div className="flex flex-wrap gap-3 pt-2">
                 <div className={`px-4 py-2 rounded-full text-sm font-bold flex items-center gap-2 ${result.workaround_attempted ? 'bg-amber-100 text-amber-700' : 'bg-gray-100 text-gray-500'}`}>
                    <div className={`w-2 h-2 rounded-full ${result.workaround_attempted ? 'bg-amber-500' : 'bg-gray-400'}`}></div>
                    {result.workaround_attempted ? "Attempted Workaround" : "No Workaround Tried"}
                 </div>
                 
                 <div className={`px-4 py-2 rounded-full text-sm font-bold flex items-center gap-2 ${result.resolved ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                    <div className={`w-2 h-2 rounded-full ${result.resolved ? 'bg-green-500' : 'bg-red-500'}`}></div>
                    {result.resolved ? "Issue Eventually Resolved" : "Abandoned / Unresolved"}
                 </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="card min-h-[120px] flex flex-col justify-center text-center border-dashed border-[#E5E7EB]">
            <p className="text-[#9CA3AF]">
              Awaiting input. Paste text above to see the extracted failure taxonomy.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
