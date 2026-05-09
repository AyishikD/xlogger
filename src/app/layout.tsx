"use client";

import { usePathname } from "next/navigation";
import "./globals.css";
import Link from "next/link";
import { Brain, Activity, History, Search, LayoutDashboard, Rocket, Zap, ChevronRight } from "lucide-react";
import { motion } from "framer-motion";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const isLandingPage = pathname === "/";

  return (
    <html lang="en">
      <head>
        <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
        <title>ModelLogger | Autonomous AI Reliability</title>
      </head>
      <body className="antialiased">
        <div className={`flex h-screen overflow-hidden transition-colors duration-500 ${
          isLandingPage 
            ? 'bg-[#F8F5EF] text-[#1A1A1A]' 
            : 'bg-[#020617] text-[#f8fafc]'
        }`}>
          {!isLandingPage && (
            <aside className="w-72 bg-[#0a0f1e] border-r border-white/5 flex flex-col hidden md:flex shrink-0">
              <div className="p-8 border-b border-white/5">
                <Link href="/" className="flex items-center gap-3 font-black text-2xl tracking-tighter italic group">
                  <div className="p-2 bg-white/5 rounded-xl border border-white/10 group-hover:scale-110 transition-transform flex items-center justify-center">
                    <Brain className="w-6 h-6 text-primary" />
                  </div>
                  <span>ModelLogger</span>
                </Link>
              </div>
              
              <nav className="flex-1 p-6 space-y-3">
                <div className="text-[10px] font-black tracking-widest text-slate-500 uppercase mb-4 px-4">Research Modules</div>
                <NavLink href="/launchpad" icon={<Rocket className="w-5 h-5" />} label="Launchpad" active={pathname === "/launchpad"} />
                <NavLink href="/live" icon={<Activity className="w-5 h-5" />} label="Live Cognition" active={pathname === "/live"} />
                <NavLink href="/learnings" icon={<Brain className="w-5 h-5" />} label="Learnings" active={pathname === "/learnings"} />
                <NavLink href="/failures" icon={<Search className="w-5 h-5" />} label="Failure Explorer" active={pathname === "/failures"} />
                <NavLink href="/graph" icon={<LayoutDashboard className="w-5 h-5" />} label="Knowledge Graph" active={pathname === "/graph"} />
              </nav>
              
              <div className="p-6 border-t border-white/5">
                <div className="glass-card p-5 rounded-2xl border border-white/5 bg-white/5">
                  <div className="flex justify-between items-center mb-3">
                    <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">OS Core</p>
                    <div className="flex items-center gap-1">
                      <div className="w-1.5 h-1.5 bg-secondary rounded-full animate-pulse shadow-[0_0_8px_rgba(6,182,212,0.6)]" />
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-400">Node Cluster v4.2</span>
                    <ChevronRight className="w-3 h-3 text-slate-600" />
                  </div>
                </div>
              </div>
            </aside>
          )}

          {/* Main Content */}
          <main className="flex-1 overflow-y-auto">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}

function NavLink({ href, icon, label, active }: { href: string, icon: React.ReactNode, label: string, active?: boolean }) {
  return (
    <Link 
      href={href} 
      className={`flex items-center justify-between px-4 py-3.5 rounded-2xl transition-all group ${
        active 
          ? 'bg-primary/10 border border-primary/20 text-white' 
          : 'text-slate-400 hover:text-white hover:bg-white/5 border border-transparent'
      }`}
    >
      <div className="flex items-center gap-4">
        <div className={`${active ? 'text-primary' : 'group-hover:text-primary'} transition-colors`}>
          {icon}
        </div>
        <span className="text-sm font-bold tracking-tight">{label}</span>
      </div>
      {active && (
        <motion.div 
          layoutId="activeNav"
          className="w-1.5 h-1.5 bg-primary rounded-full shadow-[0_0_10px_rgba(139,92,246,0.8)]"
        />
      )}
    </Link>
  );
}
