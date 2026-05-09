"use client";

import { useState, useEffect } from "react";
import { useWebSocket } from "@/hooks/useWebSocket";
import { Activity, ShieldAlert, Zap, AlertTriangle, CheckCircle2, Trash2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export default function LiveFeedPage() {
  const { messages, isConnected } = useWebSocket("ws://127.0.0.1:8000/ws/cognition");
  const [historicalAlerts, setHistoricalAlerts] = useState<any[]>([]);
  const [dismissedIds, setDismissedIds] = useState<Set<string>>(new Set());
  const [livePredictions, setLivePredictions] = useState<any[]>([]);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/v1/monitor/live_alerts?count=20")
      .then(res => res.json())
      .then(data => setHistoricalAlerts(data));
  }, []);

  useEffect(() => {
    // Extract predictions from incoming messages
    const latestPreds = messages.find(m => m.channel === "live_predictions");
    if (latestPreds) {
      setLivePredictions(latestPreds.data);
    }
  }, [messages]);

  const liveAlerts = messages.filter(m => m.channel === "live_cognition").map(m => m.data);
  const allMessages = [...liveAlerts, ...historicalAlerts];
  const uniqueMessages = allMessages.filter((v, i, a) => {
    const id = v.id || `${v.timestamp}-${v.type}`;
    if (dismissedIds.has(id)) return false;
    
    return a.findIndex(t => (
      (t.id && t.id === v.id) || 
      (t.timestamp === v.timestamp && t.type === v.type)
    )) === i;
  }).sort((a, b) => new Date(b.timestamp || 0).getTime() - new Date(a.timestamp || 0).getTime());

  const handleDelete = (alert: any) => {
    const id = alert.id || `${alert.timestamp}-${alert.type}`;
    setDismissedIds(prev => new Set(prev).add(id));
  };

  return (
    <div className="min-h-screen bg-[#020617] p-8">
      <div className="max-w-6xl mx-auto">
        <header className="flex items-center justify-between mb-12">
          <div>
            <h1 className="text-3xl font-bold mb-2 flex items-center gap-3">
              <Activity className="w-8 h-8 text-primary animate-pulse" />
              Live Cognition Stream
            </h1>
            <p className="text-slate-400">Real-time research alerts and anomaly detection.</p>
          </div>
          <div className={`px-4 py-1 rounded-full text-xs font-mono border ${isConnected ? 'border-secondary/50 text-secondary bg-secondary/10' : 'border-danger/50 text-danger bg-danger/10'}`}>
            {isConnected ? "CONNECTED" : "DISCONNECTED"}
          </div>
        </header>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Feed */}
          <div className="lg:col-span-2 space-y-4">
            <AnimatePresence initial={false}>
              {uniqueMessages.length === 0 ? (
                <div className="text-center py-20 text-slate-500 border border-dashed border-slate-800 rounded-xl">
                  Waiting for active training streams...
                </div>
              ) : (
                uniqueMessages.map((msg, i) => (
                  <AlertCard key={i} alert={msg} onDelete={() => handleDelete(msg)} />
                ))
              )}
            </AnimatePresence>
          </div>

          {/* Sidebar / Stats */}
          <div className="space-y-6">
            <div className="glass p-6 rounded-xl">
              <h3 className="font-bold mb-4 flex items-center gap-2">
                <Zap className="w-5 h-5 text-accent" /> Active Predictions
              </h3>
               <div className="space-y-4">
                {livePredictions.length > 0 ? (
                  livePredictions.map((pred, i) => (
                    <PredictionItem 
                      key={i}
                      title={pred.title} 
                      confidence={pred.confidence} 
                      status={pred.status}
                    />
                  ))
                ) : (
                  <div className="text-xs text-slate-500 italic">No active risk predictions.</div>
                )}
              </div>
            </div>

            <div className="glass p-6 rounded-xl">
              <h3 className="font-bold mb-4">Intervention Queue</h3>
              <div className="text-sm text-slate-400 italic">
                No pending interventions.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function AlertCard({ alert, onDelete }: { alert: any, onDelete: () => void }) {
  const getIcon = () => {
    const sev = (alert.severity || 'info').toLowerCase();
    switch(sev) {
      case 'critical': return <ShieldAlert className="w-6 h-6 text-danger" />;
      case 'medium': return <AlertTriangle className="w-6 h-6 text-accent" />;
      default: return <Activity className="w-6 h-6 text-primary" />;
    }
  };

    const sev = (alert.severity || 'info').toLowerCase();
    return (
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className={`glass p-6 rounded-xl border-l-4 ${sev === 'critical' ? 'border-l-danger' : 'border-l-primary'}`}
      >
      <div className="flex gap-4">
        <div className="mt-1">{getIcon()}</div>
        <div className="flex-1">
          <div className="flex items-center justify-between mb-1">
            <h4 className="font-bold text-lg">{alert.type}</h4>
            <div className="flex items-center gap-3">
              <span className="text-xs font-mono text-slate-500">Exp: {alert.experiment_id.slice(0,8)}</span>
              <button 
                onClick={onDelete}
                className="p-1 hover:bg-danger/20 rounded text-slate-500 hover:text-danger transition-colors"
                title="Dismiss Alert"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
          <p className="text-slate-300 mb-3">{alert.data?.description || alert.description}</p>
          {alert.data?.affected_metrics && (
            <div className="flex gap-2">
              {alert.data.affected_metrics.map((m: string) => (
                <span key={m} className="px-2 py-0.5 bg-slate-800 rounded text-[10px] uppercase font-bold text-slate-400">
                  {m}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}

function PredictionItem({ title, confidence, status }: { title: string, confidence: number, status: string }) {
  return (
    <div className="p-3 bg-black/30 rounded-lg">
      <div className="flex justify-between items-center mb-2">
        <span className="text-sm font-medium">{title}</span>
        <span className={`text-[10px] font-bold uppercase ${status === 'Critical' ? 'text-danger' : 'text-slate-500'}`}>{status}</span>
      </div>
      <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
        <div 
          className={`h-full ${status === 'Critical' ? 'bg-danger' : 'bg-primary'}`} 
          style={{ width: `${confidence * 100}%` }}
        />
      </div>
    </div>
  );
}
