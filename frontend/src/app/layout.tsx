import type { Metadata } from "next";
import "./globals.css";
import Link from "next/link";
import { Brain, Activity, History, Search, LayoutDashboard, Rocket, Zap } from "lucide-react";

export const metadata: Metadata = {
  title: "ModelLogger | Research Memory OS",
  description: "Persistent research memory for ML teams.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        <div className="flex h-screen overflow-hidden">
          {/* Sidebar */}
          <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col hidden md:flex">
            <div className="p-6 border-b border-slate-800">
              <Link href="/" className="flex items-center gap-2 font-bold text-xl tracking-tight">
                <Brain className="w-6 h-6 text-primary" />
                ModelLogger
              </Link>
            </div>
            
            <nav className="flex-1 p-4 space-y-2">
              <NavLink href="/launchpad" icon={<Rocket className="w-5 h-5" />} label="Launchpad" />
              <NavLink href="/live" icon={<Activity className="w-5 h-5" />} label="Live Cognition" />
              <NavLink href="/learnings" icon={<Brain className="w-5 h-5" />} label="Learnings" />
              <NavLink href="/failures" icon={<Search className="w-5 h-5" />} label="Failure Explorer" />
              <NavLink href="/graph" icon={<LayoutDashboard className="w-5 h-5" />} label="Knowledge Graph" />
            </nav>
            
            <div className="p-4 border-t border-slate-800">
              <div className="bg-slate-800/50 p-4 rounded-xl">
                <p className="text-[10px] font-bold text-slate-500 uppercase mb-2">System Status</p>
                <div className="flex items-center gap-2 text-xs">
                  <div className="w-2 h-2 bg-secondary rounded-full" />
                  Backend Online
                </div>
              </div>
            </div>
          </aside>

          {/* Main Content */}
          <main className="flex-1 overflow-y-auto bg-[#020617]">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}

function NavLink({ href, icon, label }: { href: string, icon: React.ReactNode, label: string }) {
  return (
    <Link 
      href={href} 
      className="flex items-center gap-3 px-4 py-3 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-all group"
    >
      <div className="group-hover:text-primary transition-colors">{icon}</div>
      <span className="font-medium">{label}</span>
    </Link>
  );
}
