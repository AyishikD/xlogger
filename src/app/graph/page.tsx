"use client";

import ReactFlow, { Background, Controls, MiniMap, useNodesState, useEdgesState } from "reactflow";
import "reactflow/dist/style.css";
import { Brain } from "lucide-react";
import { useEffect } from "react";

export default function GraphPage() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  useEffect(() => {
    const fetchGraph = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/api/v1/memory/graph");
        const data = await res.json();
        setNodes(data.nodes || []);
        setEdges(data.edges || []);
      } catch (err) {
        console.error("Failed to fetch graph:", err);
      }
    };
    fetchGraph();
  }, [setNodes, setEdges]);

  return (
    <div className="h-screen bg-[#020617] flex flex-col">
      <header className="p-6 border-b border-slate-800 bg-slate-900/50 backdrop-blur-md flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-3">
            <Brain className="w-6 h-6 text-primary" />
            Research Knowledge Graph
          </h1>
          <p className="text-xs text-slate-500">Visualizing causal links and learning evolution across experiments.</p>
        </div>
      </header>

      <div className="flex-1 relative">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          fitView
        >
          <Background color="#1e293b" gap={20} />
          <Controls />
          <MiniMap nodeColor={(n) => {
            if (n.className?.includes('error')) return '#ef4444';
            if (n.className?.includes('learning')) return '#10b981';
            return '#3b82f6';
          }} />
        </ReactFlow>

        <style jsx global>{`
          .glass-node {
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: white;
            padding: 10px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 600;
            text-align: center;
          }
          .error-node { border-color: rgba(239, 68, 68, 0.5); }
          .learning-node { border-color: rgba(16, 185, 129, 0.5); }
          .react-flow__edge-path { stroke: #64748b; stroke-width: 2; }
          .react-flow__edge-text { 
            fill: #f8fafc !important; 
            font-size: 11px !important; 
            font-weight: 700 !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
          }
          .react-flow__edge-textbg { 
            fill: #0f172a !important; 
            fill-opacity: 0.8 !important;
            rx: 4;
            ry: 4;
          }
        `}</style>
      </div>
    </div>
  );
}
