"use client";

import { motion } from "framer-motion";
import {
  ShieldCheck,
  Zap,
  ArrowRight,
  Github,
  Terminal as TerminalIcon,
  ChevronRight,
  Activity,
  Layers,
  Brain,
  AlertCircle,
  Copy,
  Check
} from "lucide-react";
import Link from "next/link";
import { useState, useEffect } from "react";

export default function LandingPage() {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(`from modellogger import train_safe\n\ntrain_safe(\n  model="gpt2",\n  dataset="data.jsonl"\n)`);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="min-h-screen bg-[#F8F5EF] text-[#1A1A1A] selection:bg-[#A68966]/20 font-sans overflow-x-hidden relative">
      {/* Background Grid */}
      <div className="absolute inset-0 grid-light-bg opacity-30 pointer-events-none" />

      {/* Navigation */}
      <nav className="relative z-50 flex justify-between items-center px-8 md:px-20 py-8 max-w-7xl mx-auto">
        <div className="flex items-center gap-2 group cursor-pointer text-[#1A1A1A]">
          <div className="w-8 h-8 bg-[#333333] rounded-lg flex items-center justify-center text-white shadow-lg">
            <Brain className="w-5 h-5" />
          </div>
          <span className="text-xl font-bold tracking-tight">ModelLogger</span>
        </div>
        <div className="hidden md:flex items-center gap-10 text-sm font-medium text-[#717171]">
          <Link href="#features" className="hover:text-[#1A1A1A] transition-colors">Features</Link>
          <Link href="#how-it-works" className="hover:text-[#1A1A1A] transition-colors">Infrastructure</Link>
          <Link href="#vision" className="hover:text-[#1A1A1A] transition-colors">Vision</Link>
        </div>
        <div className="flex items-center gap-4">
          <Link href="/live" className="px-5 py-2.5 bg-[#333333] text-white font-semibold rounded-full hover:bg-black transition-all text-xs uppercase tracking-widest shadow-xl">
            View Product
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <header className="relative z-10 max-w-7xl mx-auto px-8 md:px-20 pt-20 pb-32">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
          >
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#F3EFE7] border border-[#E8E2D9] text-[11px] font-bold text-[#A68966] mb-8 tracking-wide uppercase">
              Now in Private Beta
            </div>
            <h1 className="text-6xl md:text-8xl font-bold tracking-tight leading-[0.95] mb-8 text-[#333333]">
              Self-healing <br />
              <span className="text-[#A68966] italic font-medium">AI training.</span>
            </h1>
            <p className="text-xl text-[#717171] font-medium max-w-lg mb-12 leading-relaxed">
              Automatically detect divergence, rollback unstable updates, and recover training runs without manual intervention.
            </p>
            <div className="flex flex-wrap gap-5">
              <Link href="https://github.com" className="px-8 py-4 bg-white border border-[#E8E2D9] text-[#1A1A1A] font-bold rounded-2xl flex items-center gap-3 hover:bg-[#F3EFE7] transition-all shadow-sm">
                <Github className="w-5 h-5 text-[#333333]" />
                View GitHub
              </Link>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 40 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 1, delay: 0.2 }}
            className="relative"
          >
            <div className="absolute inset-0 bg-[#A68966]/5 blur-[120px] rounded-full" />
            <div className="relative bg-[#FFFDF9] rounded-3xl border border-[#E8E2D9] shadow-2xl overflow-hidden">
              <div className="flex items-center justify-between px-6 py-4 border-b border-[#E8E2D9] bg-[#F3EFE7]/50">
                <div className="flex gap-2">
                  <div className="w-2.5 h-2.5 rounded-full bg-[#E57373]/20 border border-[#E57373]/40" />
                  <div className="w-2.5 h-2.5 rounded-full bg-[#FFB74D]/20 border border-[#FFB74D]/40" />
                  <div className="w-2.5 h-2.5 rounded-full bg-[#81C784]/20 border border-[#81C784]/40" />
                </div>
                <div className="text-[10px] font-bold text-[#717171] tracking-widest uppercase">original tested on gpt 2</div>
              </div>
              <div className="p-8 font-mono text-[13px] leading-relaxed bg-[#FFFDF9]">
                <TerminalContent />
              </div>
            </div>
          </motion.div>
        </div>
      </header>

      {/* Trust Strip */}
      <section className="border-y border-[#E8E2D9] bg-[#F3EFE7]/30 py-12 relative z-10">
        <div className="max-w-7xl mx-auto px-8 md:px-20">
          <p className="text-center text-[10px] font-black uppercase tracking-[0.2em] text-[#717171] mb-10">Built for modern fine-tuning pipelines</p>
          <div className="flex flex-wrap justify-center items-center gap-12 md:gap-24 opacity-60 grayscale hover:grayscale-0 transition-all duration-700 text-[#333333]">
            <div className="text-2xl font-black italic tracking-tighter">HuggingFace</div>
            <div className="text-2xl font-black italic tracking-tighter">PyTorch</div>
            <div className="text-2xl font-black italic tracking-tighter">LoRA</div>
            <div className="text-2xl font-black italic tracking-tighter">CUDA</div>
          </div>
        </div>
      </section>

      {/* Problem Section */}
      <section id="features" className="max-w-7xl mx-auto px-8 md:px-20 py-40 relative z-10">
        <div className="text-center mb-24">
          <h2 className="text-5xl font-bold tracking-tight text-[#333333] mb-6">Training runs fail constantly.</h2>
          <p className="text-[#717171] font-medium max-w-xl mx-auto">Stop losing sleep over crashed experiments and corrupted weights.</p>
        </div>
        <div className="grid md:grid-cols-3 gap-8">
          <FeatureCard title="Exploding Gradients" desc="Automatically detect spikes before they propagate and corrupt weights." />
          <FeatureCard title="NaN Detection" desc="Instant detection of numerical instabilities with zero overhead on throughput." />
          <FeatureCard title="Unstable LR" desc="Heuristic-driven adjustment when training dynamics begin to diverge." />
          <FeatureCard title="Overnight Crashes" desc="Self-healing mechanisms that restore from the last stable checkpoint." />
          <FeatureCard title="Corrupted Batches" desc="Identify and isolate outlier data points that poison the optimization surface." />
          <FeatureCard title="Compute Efficiency" desc="Stop paying for GPU time on dead training runs. Recover or terminate instantly." />
        </div>
      </section>

      {/* How it Works */}
      <section id="how-it-works" className="bg-[#F3EFE7]/50 py-40 border-y border-[#E8E2D9] relative z-10">
        <div className="max-w-7xl mx-auto px-8 md:px-20">
          <div className="grid lg:grid-cols-2 gap-20 items-center">
            <div>
              <h2 className="text-5xl font-bold tracking-tight text-[#333333] mb-12 italic">Autonomous stability loop.</h2>
              <div className="space-y-12">
                <StepItem number="01" title="Detect Anomalies" desc="Real-time monitoring of gradient norms, loss behavior, and weight distributions." />
                <StepItem number="02" title="Intervene Automatically" desc="Trigger rollbacks to stable states and apply corrective hyperparameter patches." />
                <StepItem number="03" title="Continue Training" desc="Resume optimization with stabilized parameters without manual supervision." />
              </div>
            </div>
            <div className="bg-[#FFFDF9] p-10 rounded-[40px] shadow-2xl border border-[#E8E2D9] relative overflow-hidden">
              <div className="h-64 flex flex-col justify-end gap-4 p-4 border-l border-b border-[#E8E2D9] relative">
                <motion.div
                  initial={{ height: "40%" }}
                  animate={{ height: ["40%", "80%", "20%", "30%", "25%"] }}
                  transition={{ repeat: Infinity, duration: 4 }}
                  className="w-full bg-[#A68966]/20 border-t-2 border-[#A68966]"
                />
                <div className="text-[10px] font-bold text-[#717171] text-center">STABILIZED LOSS CURVE (LIVE)</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Before vs After */}
      <section className="max-w-7xl mx-auto px-8 md:px-20 py-40 relative z-10">
        <div className="grid md:grid-cols-2 gap-16">
          <div className="space-y-8">
            <h3 className="text-xs font-black uppercase tracking-[0.2em] text-red-500">Without ModelLogger</h3>
            <div className="bg-[#FFFDF9] p-8 rounded-3xl border border-red-100">
              <div className="space-y-4">
                <div className="flex justify-between items-center text-sm font-bold text-[#333333]">
                  <span>Current Loss</span>
                  <span className="text-red-500 font-mono">NaN</span>
                </div>
                <div className="h-2 bg-red-50 rounded-full w-full" />
                <div className="p-4 bg-red-50 rounded-xl border border-red-100 text-xs text-red-600 font-medium italic">
                  RuntimeError: Gradient overflow. Run crashed. 8 hours of GPU time wasted.
                </div>
              </div>
            </div>
          </div>
          <div className="space-y-8">
            <h3 className="text-xs font-black uppercase tracking-[0.2em] text-emerald-600">With ModelLogger</h3>
            <div className="bg-[#FFFDF9] p-8 rounded-3xl border border-emerald-100 shadow-lg">
              <div className="space-y-4">
                <div className="flex justify-between items-center text-sm font-bold text-[#333333]">
                  <span>Current Loss</span>
                  <span className="text-emerald-600 font-mono">0.042</span>
                </div>
                <div className="h-2 bg-emerald-50 rounded-full w-full overflow-hidden">
                  <motion.div initial={{ width: 0 }} animate={{ width: "70%" }} className="h-full bg-emerald-500" />
                </div>
                <div className="p-4 bg-emerald-50 rounded-xl border border-emerald-100 text-xs text-emerald-600 font-medium italic">
                  Anomaly detected at step 4,200. Rollback successful. Training resumed with 0.5x LR.
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Vision Section */}
      <section id="vision" className="pb-40 px-8 relative z-10 text-[#1A1A1A]">
        <div className="max-w-5xl mx-auto bg-[#F3EFE7] rounded-[48px] p-20 text-center border border-[#E8E2D9] relative overflow-hidden shadow-sm">
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-[#A68966]/30 to-transparent" />
          <h2 className="text-xs font-black uppercase tracking-[0.3em] text-[#A68966] mb-12">Vision</h2>
          <h3 className="text-4xl md:text-5xl font-bold tracking-tight text-[#333333] mb-12 leading-[1.1] max-w-4xl mx-auto">
            AI agents are becoming capable enough to run real workflows, <br />
            <span className="italic font-medium text-[#717171]">but they are still too unreliable to trust in production.</span>
          </h3>
          <p className="text-xl text-[#717171] mb-12 max-w-2xl mx-auto font-medium leading-relaxed">
            We are building the infrastructure that allows autonomous AI systems to detect failures, recover automatically, and improve from intervention history.
            <br /><br />
            <span className="text-[#333333] font-bold">Our long-term goal is to become the operational backbone for reliable AI systems.</span>
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-[#E8E2D9] py-20 bg-[#FFFDF9] relative z-10 text-[#1A1A1A]">
        <div className="max-w-7xl mx-auto px-8 md:px-20 flex flex-col md:flex-row justify-between items-start gap-12">
          <div>
            <div className="flex items-center gap-2 mb-6">
              <div className="w-6 h-6 bg-[#333333] rounded flex items-center justify-center text-white text-[10px] font-bold">M</div>
              <span className="text-lg font-bold tracking-tight text-[#1A1A1A]">ModelLogger</span>
            </div>
            <p className="text-sm text-[#717171] font-medium">The autonomous reliability platform <br /> for machine learning.</p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-20 text-sm font-medium">
            <div className="space-y-4">
              <p className="text-[#1A1A1A] uppercase tracking-widest text-[10px] font-black">Product</p>
              <p className="text-[#717171] hover:text-[#1A1A1A] cursor-pointer transition-colors">Infrastructure</p>
              <p className="text-[#717171] hover:text-[#1A1A1A] cursor-pointer transition-colors">Security</p>
            </div>
            <div className="space-y-4">
              <p className="text-[#1A1A1A] uppercase tracking-widest text-[10px] font-black">Company</p>
              <p className="text-[#717171] hover:text-[#1A1A1A] cursor-pointer transition-colors">Vision</p>
              <p className="text-[#717171] hover:text-[#1A1A1A] cursor-pointer transition-colors">Careers</p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

function FeatureCard({ title, desc }: { title: string, desc: string }) {
  return (
    <div className="bg-[#FFFDF9] p-10 rounded-3xl border border-[#E8E2D9] hover:shadow-xl transition-all group hover:-translate-y-1 text-[#1A1A1A]">
      <h4 className="text-xl font-bold tracking-tight mb-4 group-hover:text-[#A68966] transition-colors italic text-[#333333]">{title}</h4>
      <p className="text-[#717171] text-sm font-medium leading-relaxed">{desc}</p>
    </div>
  );
}

function StepItem({ number, title, desc }: { number: string, title: string, desc: string }) {
  return (
    <div className="flex gap-8 group text-[#1A1A1A]">
      <div className="text-2xl font-black text-[#E8E2D9] group-hover:text-[#A68966] transition-colors font-mono">{number}</div>
      <div>
        <h4 className="text-xl font-bold mb-2 text-[#333333]">{title}</h4>
        <p className="text-[#717171] text-sm font-medium leading-relaxed">{desc}</p>
      </div>
    </div>
  );
}

const REAL_LOGS = [
  { type: "info", content: "Loading wikitext-2 dataset..." },
  { type: "info", content: "Initial LR: 0.1 (UNSTABLE BY DESIGN)" },
  { type: "info", content: "🚀 STARTING BOUNDED RELIABILITY RUN..." },
  { type: "info", content: "step=0 loss=13.2409 lr=1.00e-01 [Intv:0/3]" },
  { type: "info", content: "step=5 loss=92.0286 lr=1.00e-01 [Intv:0/3]" },
  { type: "warn", content: "[Step 6] 🛡️ RELIABILITY CHECK: Natural divergence (199.3994) detected." },
  { type: "info", content: "   💡 AI OS Suggestion: REDUCE_LR" },
  { type: "info", content: "   Reason: Experimental confidence based on 0% success rate." },
  { type: "info", content: "step=10 loss=67.8071 lr=5.00e-02 [Intv:1/3]" },
  { type: "info", content: "[Step 15] 🔼 LR RECOVERY: 6.50e-02" },
  { type: "info", content: "step=15 loss=63.5758 lr=6.50e-02 [Intv:1/3]" },
  { type: "success", content: "📈 OBJECTIVE EVALUATION: REDUCE_LR at step 6 → SUCCESS" },
  { type: "success", content: "Loss: 199.40 → 72.72" },
  { type: "info", content: "💾 CHECKPOINT: Healthy state captured at step 20" },
  { type: "warn", content: "[Step 21] 🛡️ RELIABILITY CHECK: Natural divergence (54.7406) detected." },
  { type: "info", content: "⚡ HIGH CONFIDENCE PATH: Executing immediate state rollback." },
  { type: "info", content: "🔄 SCRIPT: Weights rolled back to Step 11" },
  { type: "warn", content: "[Step 30] 🧪 HERO CASE: Injecting real corrupted data batch..." },
  { type: "success", content: "🔥 RESULT: Transient corruption did NOT affect training trajectory." },
  { type: "success", content: "📈 OBJECTIVE EVALUATION: ROLLBACK_AND_STABILIZE → SUCCESS" },
  { type: "success", content: "Loss: 54.74 → 27.37" },
  { type: "success", content: "✅ TRAINING COMPLETE" },
];

function TerminalContent() {
  const [step, setStep] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setStep(s => (s + 1) % (REAL_LOGS.length + 5));
    }, 1200);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="space-y-1.5 text-[#1A1A1A]">
      {REAL_LOGS.slice(0, step + 1).map((log, i) => (
        <div key={i} className="flex gap-3 leading-relaxed">
          <span className={`font-bold ${log.type === 'error' ? 'text-red-500' :
              log.type === 'warn' ? 'text-amber-600' :
                log.type === 'success' ? 'text-emerald-600' :
                  log.content.includes('ModelLogger') ? 'text-[#A68966]' : 'text-[#333333]'
            }`}>
            {log.content}
          </span>
        </div>
      ))}
      <div className="inline-block w-2 h-4 bg-[#A68966]/40 animate-pulse ml-1" />
    </div>
  );
}
