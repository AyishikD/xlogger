"use client";

import { useState, useEffect, useRef } from "react";
import { Rocket, Play, Terminal, ExternalLink, CheckCircle, AlertCircle, Loader2 } from "lucide-react";
import Link from "next/link";

export default function LaunchpadPage() {
  const [scripts, setScripts] = useState<any[]>([]);
  const [runningScript, setRunningScript] = useState<string | null>(null);
  const [logs, setLogs] = useState<any[]>([]);
  const [detectedExperimentId, setDetectedExperimentId] = useState<string | null>(null);
  const logEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/v1/launchpad/scripts")
      .then(res => res.json())
      .then(data => setScripts(data));
  }, []);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  const runScript = (scriptName: string) => {
    setRunningScript(scriptName);
    setLogs([]);
    setDetectedExperimentId(null);
    
    const ws = new WebSocket(`ws://127.0.0.1:8000/api/v1/launchpad/run/${scriptName}`);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "log") {
        setLogs(prev => [...prev, data]);
        
        // Auto-detect experiment ID from logs
        const match = data.content.match(/Experiment ID: ([a-f0-9-]+)/);
        if (match) {
          setDetectedExperimentId(match[1]);
        }
      } else if (data.type === "status") {
        setRunningScript(null);
      }
    };

    ws.onclose = () => setRunningScript(null);
  };

  return (
    <div className="min-h-screen bg-[#020617] text-slate-100 p-8">
      <div className="max-w-6xl mx-auto">
        <header className="mb-12">
          <h1 className="text-4xl font-bold mb-4 flex items-center gap-4">
            <Rocket className="w-10 h-10 text-primary" />
            Model Launchpad
          </h1>
          <p className="text-slate-400 text-lg">Discover and execute research scripts dynamically from your workspace.</p>
        </header>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Script List */}
          <div className="space-y-4">
            <h2 className="text-xs font-bold uppercase tracking-widest text-slate-500 mb-4">Available Scripts</h2>
            {scripts.map(script => (
              <div 
                key={script.name}
                className={`p-5 rounded-2xl border transition-all ${
                  runningScript === script.name 
                    ? 'bg-primary/10 border-primary shadow-[0_0_20px_rgba(59,130,246,0.2)]' 
                    : 'bg-slate-900/50 border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-bold text-lg">{script.name}</h3>
                  {runningScript === script.name ? (
                    <Loader2 className="w-5 h-5 text-primary animate-spin" />
                  ) : (
                    <button 
                      onClick={() => runScript(script.name)}
                      className="p-2 bg-primary/20 text-primary rounded-lg hover:bg-primary/30 transition-colors"
                    >
                      <Play className="w-4 h-4 fill-current" />
                    </button>
                  )}
                </div>
                <p className="text-sm text-slate-400 line-clamp-2">{script.description}</p>
              </div>
            ))}
          </div>

          {/* Terminal Output */}
          <div className="lg:col-span-2 flex flex-col">
            <div className="bg-black/80 rounded-2xl border border-slate-800 overflow-hidden flex-1 flex flex-col min-h-[500px]">
              <div className="p-4 bg-slate-900/80 border-b border-slate-800 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Terminal className="w-4 h-4 text-slate-400" />
                  <span className="text-xs font-mono text-slate-400">RESEARCH_CONSOLE</span>
                </div>
                {runningScript && (
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 bg-primary rounded-full animate-pulse" />
                    <span className="text-[10px] font-bold uppercase text-primary">Live Streaming</span>
                  </div>
                )}
              </div>
              
              <div className="p-6 font-mono text-sm overflow-y-auto max-h-[600px] space-y-1">
                {logs.length === 0 && !runningScript && (
                  <div className="h-full flex items-center justify-center text-slate-600 italic">
                    Select a script to begin execution stream...
                  </div>
                )}
                {logs.map((log, i) => (
                  <div key={i} className={log.stream === "stderr" ? "text-danger/80" : "text-slate-300"}>
                    <span className="text-slate-600 mr-3 select-none">[{new Date().toLocaleTimeString()}]</span>
                    {log.content}
                  </div>
                ))}
                <div ref={logEndRef} />
              </div>
            </div>

            {/* Contextual Action Notification */}
            {detectedExperimentId && (
              <div className="mt-6 p-6 bg-secondary/10 border border-secondary/30 rounded-2xl flex items-center justify-between animate-in slide-in-from-bottom-4">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-full bg-secondary/20 flex items-center justify-center text-secondary">
                    <CheckCircle className="w-6 h-6" />
                  </div>
                  <div>
                    <h4 className="font-bold text-secondary">New Experiment Detected!</h4>
                    <p className="text-sm text-slate-400">Active monitoring established for <span className="font-mono text-xs">{detectedExperimentId}</span></p>
                  </div>
                </div>
                <div className="flex gap-3">
                  <Link 
                    href="/live"
                    className="px-6 py-2 bg-secondary text-[#020617] font-bold rounded-xl hover:scale-105 transition-transform flex items-center gap-2"
                  >
                    Go to Live Feed <ExternalLink className="w-4 h-4" />
                  </Link>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
