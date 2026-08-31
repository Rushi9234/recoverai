"use client";

import React, { useEffect, useState } from "react";
import { formatCurrency, fetchApi } from "@/lib/api";
import { TagBadge } from "@/components/TagBadge";
import { Play, Sliders, TrendingUp, ShieldCheck, RefreshCw } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

export default function RecoverySimulator() {
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const runSimulation = async () => {
    try {
      setLoading(true);
      const res = await fetchApi("/simulator/compare", {
        method: "POST",
        body: JSON.stringify({
          strategies: ["AI_RECOMMENDED", "CONSERVATIVE", "AGGRESSIVE", "CURRENT_POLICY"]
        })
      });
      setResults(res.data.results || []);
    } catch (e) {
      console.error("Simulator error", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runSimulation();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-gray-800">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-bold text-white tracking-tight">Recovery Policy Simulator</h1>
            <TagBadge tag="PROJECTED" />
          </div>
          <p className="text-xs text-gray-400 mt-1">Simulate strategy outcomes and policy boundaries without touching live customer payments.</p>
        </div>
        <button onClick={runSimulation} className="px-4 py-2 text-xs font-mono font-bold bg-purple-600 hover:bg-purple-500 text-white rounded-lg shadow-lg shadow-purple-600/30 flex items-center space-x-2 transition">
          <Play className="w-4 h-4" />
          <span>RUN STRATEGY SIMULATION</span>
        </button>
      </div>

      {/* Simulator Strategy Comparison Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {results.map((r) => (
          <div key={r.strategy} className="p-5 bg-[#111827] border border-gray-800 rounded-xl space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono font-bold text-blue-400">{r.strategy}</span>
              <TagBadge tag="PROJECTED" />
            </div>
            <div className="text-2xl font-bold font-mono text-emerald-400">
              {formatCurrency(r.projected_recovered_minor)}
            </div>
            <div className="space-y-1 font-mono text-xs text-gray-400">
              <div className="flex justify-between">
                <span>Recovery Rate:</span>
                <span className="text-gray-200 font-bold">{(r.recovery_rate * 100).toFixed(1)}%</span>
              </div>
              <div className="flex justify-between">
                <span>Actions Triggered:</span>
                <span className="text-gray-200">{r.projected_action_count}</span>
              </div>
              <div className="flex justify-between">
                <span>Contacts Sent:</span>
                <span className="text-gray-200">{r.projected_contact_count}</span>
              </div>
              <div className="flex justify-between text-red-400">
                <span>Policy Blocked:</span>
                <span>{r.projected_blocked_count}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Comparison Chart */}
      <div className="p-6 bg-[#111827] border border-gray-800 rounded-xl space-y-4">
        <h3 className="text-sm font-bold font-mono text-gray-200">STRATEGY RECOVERY PROJECTIONS</h3>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={results}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
              <XAxis dataKey="strategy" stroke="#6b7280" fontSize={11} />
              <YAxis stroke="#6b7280" fontSize={11} tickFormatter={(val) => `₹${val/1000}k`} />
              <Tooltip
                contentStyle={{ backgroundColor: "#1f2937", borderColor: "#374151", color: "#fff" }}
                formatter={(val: any) => [`₹${(Number(val)/100).toLocaleString()}`, "Projected Recovery"]}
              />
              <Bar dataKey="projected_recovered_minor" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
