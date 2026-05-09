"use client";

import { motion } from "framer-motion";
import { Brain, Cpu, History, Zap, Activity, ShieldAlert } from "lucide-react";
import Link from "next/link";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#020617] overflow-hidden">
      {/* Hero Section */}
      <section className="relative pt-24 pb-32 px-6">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[600px] bg-primary/10 rounded-full blur-[120px] -z-10" />
        
        <div className="max-w-6xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h1 className="text-6xl md:text-7xl font-bold tracking-tight mb-8 bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
              Your AI team forgets every <br /> failed experiment. <br />
              <span className="text-primary">ModelLogger remembers them all.</span>
            </h1>
            <p className="text-xl text-slate-400 max-w-3xl mx-auto mb-10 text-balance">
              Persistent research memory for ML teams. Detect failures early, 
              retrieve historical fixes, and accumulate organizational learning automatically.
            </p>
            
            <div className="flex items-center justify-center gap-4">
              <Link href="/live" className="px-8 py-4 bg-primary rounded-lg font-semibold hover:bg-blue-600 transition-colors">
                Live Demo
              </Link>
              <Link href="/learnings" className="px-8 py-4 bg-slate-800 rounded-lg font-semibold hover:bg-slate-700 transition-colors">
                Explore Memory
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-24 px-6 bg-slate-900/50">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-3 gap-8">
            <FeatureCard 
              icon={<Brain className="w-8 h-8 text-primary" />}
              title="Autonomous Learning"
              description="Automatically clusters failed training runs into reusable organizational insights."
            />
            <FeatureCard 
              icon={<Zap className="w-8 h-8 text-secondary" />}
              title="Live Cognition"
              description="Real-time monitoring that predicts failures and recommends interventions instantly."
            />
            <FeatureCard 
              icon={<History className="w-8 h-8 text-accent" />}
              title="Temporal Memory"
              description="Track how instabilities evolve across model versions and dataset revisions."
            />
          </div>
        </div>
      </section>

      {/* Code Section */}
      <section className="py-24 px-6">
        <div className="max-w-4xl mx-auto">
          <div className="glass p-8 rounded-2xl">
            <h3 className="text-2xl font-bold mb-6 flex items-center gap-2">
              <Cpu className="w-6 h-6 text-primary" /> Integrate in seconds
            </h3>
            <pre className="bg-black/50 p-6 rounded-xl overflow-x-auto text-sm text-blue-300">
              <code>{`from modellogger import ModelLogger
from modellogger.integrations.huggingface import ModelLoggerCallback

# Attach to any HuggingFace Trainer
trainer = Trainer(
    model=model,
    callbacks=[ModelLoggerCallback()]
)

# Or use native PyTorch hooks
ModelLogger.attach(model)`}</code>
            </pre>
          </div>
        </div>
      </section>
    </div>
  );
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) {
  return (
    <div className="p-8 rounded-2xl glass hover:border-primary/50 transition-all group">
      <div className="mb-6 group-hover:scale-110 transition-transform">{icon}</div>
      <h3 className="text-xl font-bold mb-3">{title}</h3>
      <p className="text-slate-400">{description}</p>
    </div>
  );
}
