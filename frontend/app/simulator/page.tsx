"use client";

import React, { useEffect, useState } from "react";
import { formatCurrency, fetchApi } from "@/lib/api";
import { TagBadge } from "@/components/TagBadge";
import { Play, Sliders, TrendingUp, ShieldCheck, RefreshCw, AlertTriangle, CheckCircle2, Zap, Info } from "lucide-react";
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
        tag: "BEST RISK-ADJUSTED BALANCE",
        tagColor: "bg-[#fffbeb] text-[#b45309] border-[#fde68a] font-bold",
        riskLevel: "LOW RISK",
        riskColor: "text-[#047857] font-bold",
        explanation: "RecoverAI optimizes expected recovery within merchant-defined safety constraints rather than maximizing attempts.",
        frictionNote: "Balanced outreach & 0% policy violations."
      };
    } else if (strategy === "CONSERVATIVE") {
      return {
        tag: "LOW INTERVENTION",
        tagColor: "bg-gray-100 text-gray-700 border-gray-200",
        riskLevel: "MINIMAL RISK",
        riskColor: "text-[#047857] font-bold",
        explanation: "Lower intervention volume; may leave recoverable revenue untouched.",
        frictionNote: "Lowest customer contact frequency."
      };
    } else if (strategy === "AGGRESSIVE") {
      return {
        tag: "HIGHER PROJECTED RECOVERY",
        tagColor: "bg-[#fff1f2] text-[#be123c] border-[#fecdd3] font-bold",
        riskLevel: "HIGHER OPERATIONAL RISK",
        riskColor: "text-[#be123c] font-bold",
        explanation: "Higher projected recovery comes with +118% more contacts, higher action volume, and increased customer friction.",
        frictionNote: "+118% contacts, higher friction."
      };
    } else {
      return {
        tag: "BASELINE",
        tagColor: "bg-gray-100 text-gray-700 border-gray-200",
        riskLevel: "MODERATE RISK",
        riskColor: "text-gray-700",
        explanation: "Baseline policy without contextual AI strategy optimization.",
        frictionNote: "Static schedule without diagnosis."
      };
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-[#e5e1d5]">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-bold font-serif text-[#111113] tracking-tight">Recovery Policy Simulator</h1>
            <TagBadge tag="PROJECTED" />
          </div>
          <p className="text-xs text-[#6e6d67] mt-1">What-if simulation engine comparing recovery strategies without touching live customer payments.</p>
        </div>
        <button onClick={runSimulation} className="px-4 py-2 text-xs font-mono font-bold bg-[#6d28d9] hover:bg-[#5b21b6] text-white rounded-lg shadow-sm flex items-center space-x-2 transition">
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
            <div key={r.strategy} className={`p-5 bg-white border rounded-xl space-y-3 relative shadow-sm ${isBest ? "border-[#b8860b] shadow-md shadow-amber-900/10" : "border-[#e5e1d5]"}`}>
              {isBest && (
                <span className="absolute -top-3 right-4 px-2.5 py-0.5 text-[9px] font-mono font-bold bg-[#b8860b] text-white rounded-full shadow-sm">
                  ★ RECOMMENDED
                </span>
              )}

              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-[#b45309]">{r.strategy}</span>
                <span className={`px-2 py-0.5 text-[9px] font-mono rounded border ${meta.tagColor}`}>
                  {meta.tag}
                </span>
              </div>

              <div>
                <div className="text-2xl font-bold font-mono text-[#047857]">
                  {formatCurrency(r.projected_recovered_minor)}
                </div>
                <div className="text-[10px] font-mono text-[#6e6d67] mt-0.5">Projected Recovery</div>
              </div>

              <div className="space-y-1 font-mono text-xs text-[#33322e] pt-2 border-t border-[#e5e1d5]">
                <div className="flex justify-between">
                  <span className="text-[#6e6d67]">Recovery Rate:</span>
                  <span className="text-[#111113] font-bold">{(r.recovery_rate * 100).toFixed(1)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#6e6d67]">Actions Triggered:</span>
                  <span className="text-[#33322e]">{r.projected_action_count}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#6e6d67]">Contacts Sent:</span>
                  <span className="text-[#33322e]">{r.projected_contact_count}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#6e6d67]">Policy Blocks:</span>
                  <span className="text-[#be123c] font-bold">{r.projected_blocked_count}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#6e6d67]">Operational Risk:</span>
                  <span className={meta.riskColor}>{meta.riskLevel}</span>
                </div>
              </div>

              <p className="text-[10px] text-[#6e6d67] font-sans italic pt-2 border-t border-[#e5e1d5] leading-relaxed">
                {meta.explanation}
              </p>
            </div>
          );
        })}
      </div>

      {/* Comparison Chart */}
      <div className="p-6 bg-white border border-[#e5e1d5] rounded-xl space-y-4 shadow-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <h3 className="text-xs font-bold font-mono text-[#111113] uppercase tracking-wider">STRATEGY RECOVERY PROJECTIONS COMPARISON</h3>
            <TagBadge tag="PROJECTED" />
          </div>
          <span className="text-xs text-[#6e6d67] font-mono">RecoverAI optimizes recovery within safety constraints.</span>
        </div>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={results}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e1d5" />
              <XAxis dataKey="strategy" stroke="#6e6d67" fontSize={11} />
              <YAxis stroke="#6e6d67" fontSize={11} tickFormatter={(val) => `₹${val/1000}k`} />
              <Tooltip
                contentStyle={{ backgroundColor: "#ffffff", borderColor: "#e5e1d5", color: "#111113" }}
                formatter={(val: any) => [`₹${(Number(val)/100).toLocaleString()}`, "Projected Recovery"]}
              />
              <Bar dataKey="projected_recovered_minor" fill="#6d28d9" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
