"use client";

import { useEffect, useState } from "react";
import { Brain, TrendingUp, ShieldCheck, Clock, Users } from "lucide-react";

export default function LearningsPage() {
  const [learnings, setLearnings] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedLearning, setSelectedLearning] = useState<any>(null);

  useEffect(() => {
    const fetchLearnings = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/api/v1/learning/all");
        const data = await res.json();
        setLearnings(data || []);
      } catch (err) {
        console.error("Failed to fetch learnings:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchLearnings();
  }, []);

  return (
    <div className="min-h-screen bg-[#020617] p-8">
      <div className="max-w-6xl mx-auto">
        <header className="mb-12 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2 flex items-center gap-3">
              <Brain className="w-8 h-8 text-primary" />
              Organizational Learning
            </h1>
            <p className="text-slate-400">Synthesized knowledge from across all research activity.</p>
          </div>
          <div className="flex gap-4">
            <StatBox icon={<TrendingUp className="w-4 h-4 text-secondary" />} label="New Insights" value={`+${learnings.length}`} />
            <StatBox icon={<Users className="w-4 h-4 text-primary" />} label="Contributors" value="AI Engine" />
          </div>
        </header>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Recurring Patterns */}
          <section className="space-y-6">
            <h3 className="text-xl font-bold border-b border-slate-800 pb-4">Synthesized Insights</h3>
            {loading ? (
              <div className="text-slate-500 py-10">Evolving research memory...</div>
            ) : learnings.length > 0 ? (
              learnings.map((learning, i) => (
                <LearningCard
                  key={i}
                  type={learning.metadata_json?.type || "INSIGHT"}
                  title={learning.title}
                  confidence={learning.metadata_json?.confidence || 0.85}
                  description={learning.content}
                  actions={learning.metadata_json?.recommendations || []}
                  onShowActions={() => setSelectedLearning(learning)}
                />
              ))
            ) : (
              <div className="glass p-10 rounded-2xl text-slate-500 italic text-center">
                No synthesized learnings yet. Run more experiments to generate insights.
              </div>
            )}
          </section>

          {/* Stability Trends */}
          <section className="space-y-6">
            <h3 className="text-xl font-bold border-b border-slate-800 pb-4">Knowledge Evolution</h3>
            <div className="glass p-8 rounded-2xl h-64 flex items-center justify-center italic text-slate-500 overflow-hidden relative">
              <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-transparent pointer-events-none" />
              Learning graph visualization available after 5+ experiments.
            </div>

            <div className="glass p-6 rounded-2xl">
              <h4 className="font-bold mb-4 flex items-center gap-2">
                <Clock className="w-5 h-5 text-accent" /> Recent Updates
              </h4>
              <div className="space-y-4 text-sm">
                {learnings.slice(0, 3).map((l, i) => (
                  <UpdateItem key={i} text={`New learning generated: '${l.title}'`} time="Just now" />
                ))}
                {learnings.length === 0 && <div className="text-slate-600">Monitoring experiment stream...</div>}
              </div>
            </div>
          </section>
        </div>
      </div>

      {/* Modal */}
      {selectedLearning && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-6">
          <div className="glass max-w-lg w-full p-8 rounded-3xl border-primary/20 animate-in fade-in zoom-in duration-200">
            <div className="flex items-center gap-3 mb-6">
              <ShieldCheck className="w-8 h-8 text-secondary" />
              <div>
                <h2 className="text-xl font-bold">Strategic Recommendations</h2>
                <p className="text-xs text-slate-500">{selectedLearning.title}</p>
              </div>
            </div>

            <div className="space-y-4 mb-8">
              {(selectedLearning.metadata_json?.recommendations || []).map((action: string, i: number) => (
                <div key={i} className="flex gap-4 p-4 bg-slate-900/50 rounded-xl border border-slate-800">
                  <div className="w-6 h-6 rounded-full bg-secondary/10 text-secondary flex items-center justify-center text-xs font-bold shrink-0">
                    {i + 1}
                  </div>
                  <p className="text-slate-300 text-sm leading-relaxed">{action}</p>
                </div>
              ))}
            </div>

            <button
              onClick={() => setSelectedLearning(null)}
              className="w-full py-3 bg-primary text-white font-bold rounded-xl hover:bg-primary-dark transition-colors"
            >
              Acknowledge & Implement
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

function StatBox({ icon, label, value }: { icon: React.ReactNode, label: string, value: string }) {
  return (
    <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl text-center min-w-[120px]">
      <div className="flex items-center justify-center mb-1">{icon}</div>
      <div className="text-2xl font-bold">{value}</div>
      <div className="text-[10px] uppercase font-bold text-slate-500">{label}</div>
    </div>
  );
}

function LearningCard({ type, title, confidence, description, actions, onShowActions }: any) {
  return (
    <div className="glass p-6 rounded-2xl relative overflow-hidden group">
      <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity pointer-events-none">
        <Brain className="w-16 h-16" />
      </div>

      <div className="flex items-center gap-3 mb-4">
        <span className="text-[10px] font-bold px-2 py-0.5 bg-primary/10 text-primary rounded border border-primary/20">
          {type}
        </span>
        <span className="text-[10px] font-bold text-slate-500">Confidence: {(confidence * 100).toFixed(0)}%</span>
      </div>

      <h4 className="text-lg font-bold mb-3">{title}</h4>
      <p className="text-sm text-slate-400 mb-6">{description}</p>

      <button
        onClick={onShowActions}
        className="flex items-center gap-2 text-xs font-bold text-secondary hover:text-secondary-light transition-colors group/btn"
      >
        <ShieldCheck className="w-4 h-4" />
        Recommended Actions
        <TrendingUp className="w-3 h-3 translate-x-0 group-hover/btn:translate-x-1 transition-transform" />
      </button>
    </div>
  );
}

function UpdateItem({ text, time }: { text: string, time: string }) {
  return (
    <div className="flex justify-between items-start gap-4">
      <p className="text-slate-300">{text}</p>
      <span className="text-slate-600 shrink-0">{time}</span>
    </div>
  );
}
