"use client";

import React, { useEffect, useState } from "react";
import { formatCurrency, fetchApi } from "@/lib/api";
import { TagBadge } from "@/components/TagBadge";
import { Play, Sliders, TrendingUp, ShieldCheck, RefreshCw, AlertTriangle, CheckCircle2, Zap } from "lucide-react";
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

  const getStrategyMetrics = (strategy: string) => {
    if (strategy === "AI_RECOMMENDED") {
      return {
        tag: "BEST BALANCE",
        tagColor: "bg-blue-950 text-blue-400 border-blue-800",
        riskLevel: "LOW RISK",
        riskColor: "text-emerald-400",
        note: "Optimizes recovery rate while respecting 100% of policy guardrails."
      };
    } else if (strategy === "CONSERVATIVE") {
      return {
        tag: "LOW OUTREACH",
        tagColor: "bg-gray-800 text-gray-300 border-gray-700",
        riskLevel: "MINIMAL RISK",
        riskColor: "text-emerald-400",
        note: "Minimizes customer contact but misses valid transient recovery opportunities."
      };
    } else if (strategy === "AGGRESSIVE") {
      return {
        tag: "HIGH RECOVERY / HIGH RISK",
        tagColor: "bg-amber-950 text-amber-400 border-amber-800",
        riskLevel: "HIGH OPERATIONAL RISK",
        riskColor: "text-amber-400",
        note: "Higher projected recovery comes with +118% more contacts and higher customer friction risk."
      };
    } else {
      return {
        tag: "BASELINE",
        tagColor: "bg-gray-800 text-gray-300 border-gray-700",
        riskLevel: "MODERATE RISK",
        riskColor: "text-gray-300",
        note: "Static rule application without failure diagnosis context."
      };
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-gray-800">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-bold text-white tracking-tight">Recovery Policy Simulator</h1>
            <TagBadge tag="PROJECTED" />
          </div>
          <p className="text-xs text-gray-400 mt-1">What-if simulation engine comparing recovery strategies without touching live customer payments.</p>
        </div>
        <button onClick={runSimulation} className="px-4 py-2 text-xs font-mono font-bold bg-purple-600 hover:bg-purple-500 text-white rounded-lg shadow-lg shadow-purple-600/30 flex items-center space-x-2 transition">
          <Play className="w-4 h-4" />
          <span>RUN STRATEGY SIMULATION</span>
        </button>
      </div>

      {/* Simulator Strategy Comparison Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {results.map((r) => {
          const meta = getStrategyMetrics(r.strategy);
          const isBest = r.strategy === "AI_RECOMMENDED";
          return (
            <div key={r.strategy} className={`p-5 bg-[#111827] border rounded-xl space-y-3 relative ${isBest ? "border-blue-700/80 shadow-xl shadow-blue-950/30" : "border-gray-800"}`}>
              {isBest && (
                <span className="absolute -top-3 right-4 px-2 py-0.5 text-[9px] font-mono font-bold bg-blue-600 text-white rounded-full shadow">
                  ★ RECOMMENDED
                </span>
              )}

              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-blue-400">{r.strategy}</span>
                <span className={`px-2 py-0.5 text-[9px] font-mono font-bold rounded border ${meta.tagColor}`}>
                  {meta.tag}
                </span>
              </div>

              <div>
                <div className="text-2xl font-bold font-mono text-emerald-400">
                  {formatCurrency(r.projected_recovered_minor)}
                </div>
                <div className="text-[10px] font-mono text-gray-400 mt-0.5">Projected Recovery</div>
              </div>

              <div className="space-y-1 font-mono text-xs text-gray-300 pt-2 border-t border-gray-800">
                <div className="flex justify-between">
                  <span className="text-gray-400">Recovery Rate:</span>
                  <span className="text-white font-bold">{(r.recovery_rate * 100).toFixed(1)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Actions Triggered:</span>
                  <span className="text-gray-200">{r.projected_action_count}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Contacts Sent:</span>
                  <span className="text-gray-200">{r.projected_contact_count}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Policy Blocks:</span>
                  <span className="text-red-400 font-bold">{r.projected_blocked_count}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Operational Risk:</span>
                  <span className={`font-bold ${meta.riskColor}`}>{meta.riskLevel}</span>
                </div>
              </div>

              <p className="text-[10px] text-gray-400 font-sans italic pt-1 border-t border-gray-800/60">
                {meta.note}
              </p>
            </div>
          );
        })}
      </div>

      {/* Comparison Chart */}
      <div className="p-6 bg-[#111827] border border-gray-800 rounded-xl space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold font-mono text-gray-200">STRATEGY RECOVERY PROJECTIONS COMPARISON</h3>
          <TagBadge tag="PROJECTED" />
        </div>
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
