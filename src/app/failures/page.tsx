"use client";

import { useState, useEffect } from "react";
import { Search, Filter, AlertCircle, ExternalLink, Zap, Shield, XCircle } from "lucide-react";

export default function FailureExplorer() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedRCA, setSelectedRCA] = useState<any>(null);
  const [selectedExp, setSelectedExp] = useState<any>(null);

  useEffect(() => {
    const fetchRecent = async () => {
      setLoading(true);
      try {
        const res = await fetch("http://127.0.0.1:8000/api/v1/memory/all");
        const data = await res.json();
        setResults(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchRecent();
  }, []);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/v1/memory/find_similar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ summary: query, limit: 10 })
      });
      const data = await res.json();
      setResults(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchRCA = async (result: any) => {
    setLoading(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/v1/monitor/recommend_intervention", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          experiment_id: result.experiment_id,
          failure_type: result.event_type,
          current_state: result.metadata_json
        })
      });
      const data = await res.json();
      setSelectedRCA({ ...result, recommendations: data.recommendations });
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const applyIntervention = async (action: string) => {
    try {
      await fetch(`http://127.0.0.1:8000/api/v1/monitor/send_command/${selectedRCA.experiment_id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action, payload: { source: "UI_MANUAL" } })
      });
      alert(`Sent ${action} command to training script!`);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchExperiment = async (result: any) => {
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/v1/experiments/${result.experiment_id}`);
      const data = await res.json();
      setSelectedExp({ ...result, experiment: data });
    } catch (err) {
      console.error(err);
      setSelectedExp(result); // Fallback to raw result
    } finally {
      setLoading(false);
    }
  };

  const sendFeedback = async (action: string, successful: boolean) => {
    if (!selectedRCA) return;
    try {
      await fetch("http://localhost:8000/api/v1/learning/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          experiment_id: selectedRCA.experiment_id,
          action_taken: action.split(":")[0], // Extract the action key
          was_successful: successful,
          metrics_delta: {}
        })
      });
      // Refresh the RCA to show updated intelligence
      await fetchRCA(selectedRCA);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen bg-[#020617] p-8">
      <div className="max-w-6xl mx-auto">
        <header className="mb-12">
          <h1 className="text-3xl font-bold mb-4">Failure Explorer</h1>
          <form onSubmit={handleSearch} className="relative max-w-2xl">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
            <input
              type="text"
              placeholder="Search historical failures semantically... (e.g. 'gradient overflow during bf16')"
              className="w-full bg-slate-900 border border-slate-800 rounded-xl py-4 pl-12 pr-4 focus:outline-none focus:border-primary transition-colors"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </form>
        </header>

        <div className="space-y-6">
          {loading && !results.length ? (
            <div className="text-center py-20 text-slate-500">Searching organizational memory...</div>
          ) : (
            results.map((res, i) => (
              <FailureResultCard
                key={i}
                result={res}
                onRCA={() => fetchRCA(res)}
                onView={() => fetchExperiment(res)}
              />
            ))
          )}

          {!loading && results.length === 0 && (
            <div className="text-center py-20 text-slate-500 glass rounded-2xl border-dashed border-slate-800">
              Enter a query to retrieve related failures from memory.
            </div>
          )}
        </div>
      </div>

      {/* RCA Modal */}
      {selectedRCA && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-6">
          <div className="glass max-w-2xl w-full p-8 rounded-3xl border-primary/20">
            <div className="flex items-center gap-3 mb-6">
              <Zap className="w-8 h-8 text-primary" />
              <div>
                <h2 className="text-xl font-bold">Root Cause Analysis</h2>
                <p className="text-xs text-slate-500">{selectedRCA.event_type} in Experiment {selectedRCA.experiment_id.slice(0, 8)}</p>
              </div>
            </div>

            <div className="bg-black/30 p-4 rounded-xl mb-6 border border-slate-800">
              <p className="text-sm text-slate-300 italic">"{selectedRCA.summary}"</p>
            </div>

            <div className="space-y-4 mb-8">
              <h3 className="text-xs font-bold uppercase text-slate-500 tracking-widest">Recommended Corrective Actions</h3>
              {(selectedRCA.recommendations || []).map((rec: any, i: number) => (
                <div key={i} className="flex items-center justify-between p-4 bg-slate-900/50 rounded-xl border border-slate-800 group/item">
                  <div className="flex gap-4 items-start">
                    <div className="w-6 h-6 rounded-full bg-primary/10 text-primary flex items-center justify-center text-xs font-bold shrink-0">
                      {i + 1}
                    </div>
                    <div>
                      <p className="text-slate-100 font-bold text-sm">{rec.action || "Recommendation"}</p>
                      <p className="text-slate-400 text-xs mt-1">{rec.description || (typeof rec === 'string' ? rec : "Stabilize training")}</p>
                    </div>
                  </div>

                  <div className="flex gap-2 opacity-0 group-hover/item:opacity-100 transition-opacity">
                    <button 
                      onClick={() => applyIntervention(rec.action || rec)}
                      className="p-2 hover:bg-accent/20 rounded text-accent transition-colors"
                      title="Apply this fix NOW"
                    >
                      <Zap className="w-4 h-4" />
                    </button>
                    <button 
                      onClick={() => sendFeedback(rec.action || rec, true)}
                      className="p-2 hover:bg-secondary/20 rounded text-secondary transition-colors"
                      title="This worked!"
                    >
                      <Shield className="w-4 h-4" />
                    </button>
                    <button 
                      onClick={() => sendFeedback(rec.action || rec, false)}
                      className="p-2 hover:bg-danger/20 rounded text-danger transition-colors"
                      title="This didn't work"
                    >
                      <XCircle className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>

            <button
              onClick={() => setSelectedRCA(null)}
              className="w-full py-3 bg-slate-800 text-white font-bold rounded-xl hover:bg-slate-700 transition-colors"
            >
              Dismiss
            </button>
          </div>
        </div>
      )}

      {/* Experiment Details Modal */}
      {selectedExp && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-6">
          <div className="glass max-w-3xl w-full p-8 rounded-3xl border-primary/20 overflow-y-auto max-h-[90vh]">
            <div className="flex items-center gap-3 mb-6">
              <ExternalLink className="w-8 h-8 text-secondary" />
              <div>
                <h2 className="text-2xl font-bold">{selectedExp.experiment?.name || "Experiment Context"}</h2>
                <p className="text-xs text-slate-500">ID: {selectedExp.experiment_id}</p>
              </div>
            </div>

            <p className="text-slate-400 mb-8 leading-relaxed">
              {selectedExp.experiment?.description || "Historical experiment context retrieved from memory."}
            </p>

            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-8">
              {Object.entries(selectedExp.experiment?.metadata_json || selectedExp.metadata_json || {}).map(([k, v]: any) => (
                <div key={k} className="p-4 bg-slate-900/50 rounded-xl border border-slate-800">
                  <div className="text-[10px] uppercase text-slate-500 font-bold mb-1">{k}</div>
                  <div className="text-sm font-mono text-slate-200 truncate" title={String(v)}>{String(v)}</div>
                </div>
              ))}
            </div>

            <div className="mb-8">
              <h3 className="text-xs font-bold uppercase text-slate-500 mb-2 tracking-widest">Event Snapshot</h3>
              <div className="bg-black/50 p-6 rounded-xl border border-slate-800">
                <div className="flex items-center gap-3 mb-4">
                  <span className="px-2 py-0.5 bg-danger/10 text-danger text-[10px] font-bold rounded uppercase">
                    {selectedExp.event_type}
                  </span>
                  <span className="text-xs text-slate-500">{new Date(selectedExp.created_at).toLocaleString()}</span>
                </div>
                <h4 className="text-lg font-bold mb-2">{selectedExp.summary}</h4>
                <div className="font-mono text-xs text-slate-400 whitespace-pre-wrap mt-4 p-4 bg-black/20 rounded-lg">
                  {selectedExp.content}
                </div>
              </div>
            </div>

            <button
              onClick={() => setSelectedExp(null)}
              className="w-full py-4 bg-primary text-white font-bold rounded-xl hover:shadow-[0_0_20px_rgba(var(--primary-rgb),0.4)] transition-all"
            >
              Close Research Context
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

function FailureResultCard({ result, onRCA, onView }: any) {
  return (
    <div className="glass p-6 rounded-xl hover:border-primary/30 transition-all group">
      <div className="flex items-start justify-between gap-6">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <span className="px-2 py-0.5 bg-danger/10 text-danger text-[10px] font-bold rounded uppercase">
              {result.event_type}
            </span>
            {result.similarity_score !== undefined && (
              <span className="text-xs text-slate-500 font-mono">
                Similarity: {(result.similarity_score * 100).toFixed(1)}%
              </span>
            )}
          </div>
          <h4 className="text-xl font-semibold mb-3 group-hover:text-primary transition-colors">{result.summary}</h4>
          <p className="text-slate-400 text-sm mb-6 line-clamp-2">{result.content}</p>

          <div className="flex gap-4">
            <button
              onClick={onRCA}
              className="text-xs font-bold flex items-center gap-1 text-primary hover:underline"
            >
              <Zap className="w-3 h-3" /> Root Cause Analysis
            </button>
            <button
              onClick={onView}
              className="text-xs font-bold flex items-center gap-1 text-slate-400 hover:underline"
            >
              <ExternalLink className="w-3 h-3" /> View Experiment
            </button>
          </div>
        </div>

        <div className="w-48 p-4 bg-black/20 rounded-lg hidden md:block">
          <div className="text-[10px] text-slate-500 font-bold uppercase mb-2">Metadata</div>
          <div className="space-y-1">
            {Object.entries(result.metadata_json || {}).slice(0, 3).map(([k, v]: any) => (
              <div key={k} className="flex justify-between text-[10px] font-mono">
                <span className="text-slate-500">{k}</span>
                <span className="text-slate-300 truncate ml-2" title={String(v)}>{String(v).slice(0, 10)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
