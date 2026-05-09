"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { History, Zap, AlertCircle, CheckCircle2, ChevronDown } from "lucide-react";
import { format } from "date-fns";

export default function TimelinePage() {
  const { id } = useParams();
  const [timeline, setTimeline] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTimeline = async () => {
      try {
        const res = await fetch(`http://localhost:8000/api/v1/learning/timeline/${id}`);
        const data = await res.json();
        setTimeline(data.timeline || []);
      } catch (err) {
        console.error("Failed to fetch timeline", err);
      } finally {
        setLoading(false);
      }
    };
    fetchTimeline();
  }, [id]);

  if (loading) return <div className="p-20 text-center animate-pulse">Reconstructing memory timeline...</div>;

  return (
    <div className="min-h-screen bg-[#020617] p-8">
      <div className="max-w-4xl mx-auto">
        <header className="mb-12">
          <h1 className="text-3xl font-bold mb-2">Experiment Timeline</h1>
          <p className="text-slate-400 font-mono text-sm">ID: {id}</p>
        </header>

        <div className="relative border-l-2 border-slate-800 ml-4 pl-10 space-y-12">
          {timeline.map((event, i) => (
            <TimelineItem key={i} event={event} />
          ))}
          
          {timeline.length === 0 && (
            <div className="text-slate-500 italic">No events recorded for this timeline.</div>
          )}
        </div>
      </div>
    </div>
  );
}

function TimelineItem({ event }: { event: any }) {
  const isError = event.severity === "ERROR" || event.severity === "CRITICAL";

  return (
    <div className="relative">
      {/* Connector Dot */}
      <div className={`absolute -left-[51px] top-0 w-5 h-5 rounded-full border-4 border-[#020617] ${isError ? 'bg-danger' : 'bg-primary'}`} />
      
      <div className="glass p-6 rounded-xl hover:bg-slate-800/40 transition-colors">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <span className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase ${isError ? 'bg-danger/20 text-danger' : 'bg-primary/20 text-primary'}`}>
              {event.type}
            </span>
            <span className="text-xs text-slate-500 font-mono">
              {format(new Date(event.timestamp), "HH:mm:ss.SSS")}
            </span>
          </div>
          {event.relationships && (
            <div className="flex items-center gap-1 text-[10px] text-accent font-bold uppercase">
              <Zap className="w-3 h-3" /> Related to History
            </div>
          )}
        </div>

        <h4 className="text-lg font-semibold mb-2">{event.summary}</h4>
        
        {event.meta && Object.keys(event.meta).length > 0 && (
          <div className="mt-4 p-4 bg-black/40 rounded-lg text-xs font-mono text-slate-400">
            <pre>{JSON.stringify(event.meta, null, 2)}</pre>
          </div>
        )}
      </div>
    </div>
  );
}
