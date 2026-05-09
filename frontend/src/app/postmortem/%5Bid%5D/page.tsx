"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { FileText, Clock, ShieldAlert, Target, ListChecks, ArrowLeft } from "lucide-react";
import Link from "next/link";

export default function PostmortemPage() {
  const { id } = useParams();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch(`http://localhost:8000/api/v1/monitor/postmortem/${id}`);
        const json = await res.json();
        setData(json);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id]);

  if (loading) return <div className="p-20 text-center animate-pulse text-slate-500">Generating automated research postmortem...</div>;
  if (!data) return <div className="p-20 text-center text-danger">Postmortem not found.</div>;

  return (
    <div className="min-h-screen bg-[#020617] p-8">
      <div className="max-w-4xl mx-auto">
        <Link href="/live" className="text-sm text-slate-500 hover:text-white flex items-center gap-1 mb-8">
          <ArrowLeft className="w-4 h-4" /> Back to live feed
        </Link>

        <header className="mb-12">
          <div className="flex items-center gap-3 mb-4">
            <span className="px-3 py-1 bg-danger/10 text-danger border border-danger/20 rounded-full text-xs font-bold uppercase tracking-wider">
              Research Postmortem
            </span>
            <span className="text-slate-600 text-sm">{data.generated_at}</span>
          </div>
          <h1 className="text-4xl font-bold mb-4">{data.experiment_name}</h1>
          <p className="text-xl text-slate-400 italic">"{data.summary}"</p>
        </header>

        <div className="grid md:grid-cols-3 gap-12">
          <div className="md:col-span-2 space-y-12">
            {/* Root Cause Section */}
            <section>
              <h3 className="text-xl font-bold mb-6 flex items-center gap-3 border-b border-slate-800 pb-2">
                <Target className="w-6 h-6 text-primary" /> Root Cause Analysis
              </h3>
              <div className="glass p-6 rounded-2xl">
                <div className="space-y-4">
                  {data.root_cause_analysis?.likely_causes?.map((cause: string, i: number) => (
                    <div key={i} className="text-lg text-slate-200 pl-4 border-l-2 border-primary">
                      {cause}
                    </div>
                  ))}
                  <div className="mt-6 flex items-center gap-2">
                    <span className="text-xs font-bold text-slate-500 uppercase">Analysis Confidence:</span>
                    <span className="text-sm font-bold text-primary">{(data.root_cause_analysis.confidence * 100).toFixed(0)}%</span>
                  </div>
                </div>
              </div>
            </section>

            {/* Timeline Section */}
            <section>
              <h3 className="text-xl font-bold mb-6 flex items-center gap-3 border-b border-slate-800 pb-2">
                <Clock className="w-6 h-6 text-accent" /> Critical Timeline
              </h3>
              <div className="space-y-4">
                {data.failure_timeline?.map((event: any, i: number) => (
                  <div key={i} className="flex gap-4 p-4 hover:bg-slate-900/50 rounded-xl transition-colors border border-transparent hover:border-slate-800">
                    <span className="text-xs font-mono text-slate-600 mt-1 whitespace-nowrap">{event.timestamp.split('T')[1].slice(0, 8)}</span>
                    <div>
                      <div className="text-[10px] font-bold text-danger uppercase mb-1">{event.type}</div>
                      <div className="text-sm text-slate-300 font-semibold">{event.summary}</div>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          </div>

          {/* Action Items Sidebar */}
          <aside className="space-y-8">
            <section className="glass p-6 rounded-2xl border-l-4 border-l-secondary">
              <h3 className="font-bold mb-6 flex items-center gap-2">
                <ListChecks className="w-5 h-5 text-secondary" /> Action Items
              </h3>
              <ul className="space-y-4">
                {data.action_items?.map((item: string, i: number) => (
                  <li key={i} className="flex gap-3 items-start text-sm text-slate-300">
                    <div className="w-5 h-5 rounded-full bg-secondary/10 flex items-center justify-center shrink-0 mt-0.5">
                      <div className="w-2 h-2 bg-secondary rounded-full" />
                    </div>
                    {item}
                  </li>
                ))}
              </ul>
            </section>

            <section className="glass p-6 rounded-2xl">
              <h3 className="font-bold mb-4 text-sm uppercase text-slate-500">Impact Assessment</h3>
              <div className="text-2xl font-bold text-danger mb-1">{data.organizational_impact.toUpperCase()}</div>
              <p className="text-xs text-slate-500">Based on historical recurrence of similar failure patterns.</p>
            </section>
          </aside>
        </div>
      </div>
    </div>
  );
}
