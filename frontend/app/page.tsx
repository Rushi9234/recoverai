"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { formatCurrency, fetchApi } from "@/lib/api";
import { StatusBadge } from "@/components/StatusBadge";
import { TagBadge } from "@/components/TagBadge";
import { AlertCircle, ArrowUpRight, CheckCircle2, ShieldAlert, Zap, TrendingUp, RefreshCw, Info, Database, Layers } from "lucide-react";
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

export default function ExecutiveDashboard() {
  const [summary, setSummary] = useState<any>(null);
  const [trends, setTrends] = useState<any[]>([]);
  const [activity, setActivity] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      setLoading(true);
      const [sumRes, trendRes, actRes] = await Promise.all([
        fetchApi("/dashboard/summary"),
        fetchApi("/dashboard/trends?days=7"),
        fetchApi("/dashboard/activity?limit=10")
      ]);
      setSummary(sumRes.data);
      setTrends(trendRes.data);
      setActivity(actRes.data);
    } catch (e) {
      console.error("Dashboard load error", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading && !summary) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex items-center space-x-3 text-[#6e6d67] font-mono text-xs">
          <RefreshCw className="w-4 h-4 animate-spin text-[#d97706]" />
          <span>Loading Decision Monitoring Dashboard...</span>
        </div>
      </div>
    );
  }

  const s = summary || {};

  return (
    <div className="space-y-8">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 pb-6 border-b border-[#e5e1d5]">
        <div>
          <div className="flex items-center space-x-3">
            <h1 className="text-2xl font-bold font-serif text-[#111113] tracking-tight">RecoverAI</h1>
            <span className="px-2.5 py-0.5 text-xs font-mono font-bold bg-[#fffbeb] text-[#b45309] border border-[#fde68a] rounded">
              CONTROL PLANE
            </span>
            <span className="px-2.5 py-0.5 text-xs font-mono font-bold bg-[#f0fdfa] text-[#0f766e] border border-[#99f6e4] rounded flex items-center space-x-1">
              <span className="w-1.5 h-1.5 rounded-full bg-[#0d9488] animate-pulse"></span>
              <span>TEST MODE · SIMULATION ACTIVE</span>
            </span>
          </div>
          <p className="text-xs text-[#6e6d67] mt-1 font-sans">Autonomous Revenue Recovery Control Plane & Live Decision Monitoring for Razorpay Subscriptions.</p>
        </div>
        <div className="flex items-center space-x-3">
          <button onClick={loadData} className="px-3.5 py-2 text-xs font-mono font-semibold bg-white hover:bg-[#f4f2e9] text-[#33322e] rounded-lg border border-[#d6d2c4] flex items-center space-x-1.5 shadow-sm transition">
            <RefreshCw className="w-3.5 h-3.5" />
            <span>REFRESH</span>
          </button>
          <Link href="/cases" className="px-4 py-2 text-xs font-bold bg-[#b8860b] hover:bg-[#92400e] text-white rounded-lg shadow-sm flex items-center space-x-1.5 transition">
            <span>View Highest-Risk Cases</span>
            <ArrowUpRight className="w-4 h-4" />
          </Link>
        </div>
      </div>

      {/* SECTION A: DEMO / CURRENT STATE KPI CARDS */}
      <div className="space-y-3">
        <div className="flex items-center justify-between font-mono text-xs text-[#6e6d67]">
          <div className="flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-[#b8860b]"></span>
            <span className="font-bold text-[#111113] uppercase tracking-wider">DEMO / CURRENT STATE METRICS</span>
          </div>
          <span>Active Seeded Demo Exposure State</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Card 1: Revenue at Risk */}
          <div className="p-5 bg-white border border-[#e5e1d5] rounded-xl space-y-2 shadow-sm relative overflow-hidden">
            <div className="flex items-center justify-between text-xs font-mono text-[#6e6d67]">
              <span>REVENUE AT RISK</span>
              <AlertCircle className="w-4 h-4 text-[#d97706]" />
            </div>
            <div className="text-2xl font-bold font-mono text-[#b45309]">{formatCurrency(s.revenue_at_risk_minor || 0)}</div>
            <div className="text-[11px] text-[#6e6d67] font-mono">{s.active_cases || 0} active recovery exposure cases</div>
          </div>

          {/* Card 2: Observed Recovered */}
          <div className="p-5 bg-white border border-[#e5e1d5] rounded-xl space-y-2 shadow-sm">
            <div className="flex items-center justify-between text-xs font-mono text-[#6e6d67]">
              <span>OBSERVED RECOVERED</span>
              <TagBadge tag="OBSERVED" />
            </div>
            <div className="text-2xl font-bold font-mono text-[#047857]">{formatCurrency(s.observed_recovered_minor || 0)}</div>
            <div className="text-[11px] text-[#6e6d67] font-mono">Confirmed live payment outcomes</div>
          </div>

          {/* Card 3: Simulated Recovery */}
          <div className="p-5 bg-white border border-[#e5e1d5] rounded-xl space-y-2 shadow-sm">
            <div className="flex items-center justify-between text-xs font-mono text-[#6e6d67]">
              <span>SIMULATED RECOVERY</span>
              <TagBadge tag="SIMULATED" />
            </div>
            <div className="text-2xl font-bold font-mono text-[#6d28d9]">{formatCurrency(s.simulated_recovered_minor || 0)}</div>
            <div className="text-[11px] text-[#6e6d67] font-mono">Bounded simulation execution</div>
          </div>

          {/* Card 4: Demo Recovery Rate */}
          <div className="p-5 bg-white border border-[#e5e1d5] rounded-xl space-y-2 shadow-sm">
            <div className="flex items-center justify-between text-xs font-mono text-[#6e6d67]">
              <span>DEMO RECOVERY RATE</span>
              <TrendingUp className="w-4 h-4 text-[#047857]" />
            </div>
            <div className="text-2xl font-bold font-mono text-[#111113]">{((s.recovery_rate || 0) * 100).toFixed(1)}%</div>
            <div className="flex items-center space-x-1 text-[11px] text-[#6e6d67] font-mono">
              <Info className="w-3 h-3 text-[#0d9488] shrink-0" />
              <span title="Current demo recovery rate based on active demo recovery exposure.">Active demo risk exposure</span>
            </div>
          </div>
        </div>
      </div>

      {/* SECTION B: BENCHMARK / SYNTHETIC 50-CASE EVALUATION CARD */}
      <div className="p-5 bg-[#fffdfa] border border-[#d97706]/40 rounded-xl space-y-3 shadow-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Database className="w-4 h-4 text-[#b8860b]" />
            <h3 className="text-xs font-mono font-bold text-[#111113] uppercase tracking-wider">BENCHMARK / SYNTHETIC 50-CASE EVALUATION</h3>
            <span className="px-2 py-0.5 text-[10px] font-mono font-bold bg-[#fffbeb] text-[#b45309] border border-[#fde68a] rounded">
              BATCH EVALUATION
            </span>
          </div>
          <span className="text-[11px] text-[#6e6d67] font-mono">Evaluated on synthetic dataset (`data/synthetic_50.json`)</span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 p-3 bg-[#f8f6f0] border border-[#e5e1d5] rounded-lg text-center font-mono">
          <div>
            <div className="text-[10px] text-[#6e6d67] uppercase">Total Risk Evaluated</div>
            <div className="text-sm font-bold text-[#b45309] mt-0.5">₹2,23,950</div>
          </div>
          <div>
            <div className="text-[10px] text-[#6e6d67] uppercase">Simulated Recovery</div>
            <div className="text-sm font-bold text-[#6d28d9] mt-0.5">₹94,469</div>
          </div>
          <div>
            <div className="text-[10px] text-[#6e6d67] uppercase">Simulated Recovery Rate</div>
            <div className="text-sm font-bold text-[#047857] mt-0.5">42.2%</div>
          </div>
          <div>
            <div className="text-[10px] text-[#6e6d67] uppercase">Unsafe Actions</div>
            <div className="text-sm font-bold text-[#047857] mt-0.5">0.0%</div>
          </div>
          <div>
            <div className="text-[10px] text-[#6e6d67] uppercase">Stop-Rule Violations</div>
            <div className="text-sm font-bold text-[#047857] mt-0.5">0.0%</div>
          </div>
        </div>

        <div className="text-[11px] text-[#6e6d67] font-sans italic flex items-center space-x-1 pt-1 border-t border-[#e5e1d5]">
          <Info className="w-3.5 h-3.5 text-[#0d9488] shrink-0" />
          <span>Benchmark results are from the synthetic evaluation dataset and are not live payment results.</span>
        </div>
      </div>

      {/* Secondary KPI Strip & Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 p-6 bg-white border border-[#e5e1d5] rounded-xl space-y-4 shadow-sm">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold font-mono text-[#111113] uppercase tracking-wider">7-DAY RECOVERY EXPOSURE TRENDS</h3>
            <span className="text-xs text-[#6e6d67] font-mono">Simulated vs Exposure</span>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trends}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e1d5" />
                <XAxis dataKey="date" stroke="#6e6d67" fontSize={11} />
                <YAxis stroke="#6e6d67" fontSize={11} tickFormatter={(val) => `₹${val/1000}k`} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#ffffff", borderColor: "#e5e1d5", color: "#111113" }}
                  formatter={(val: any) => [`₹${(Number(val)/100).toLocaleString()}`, "Amount"]}
                />
                <Area type="monotone" dataKey="risk_minor" stroke="#b45309" fill="#fde68a" fillOpacity={0.3} name="Risk Exposure" />
                <Area type="monotone" dataKey="simulated_recovered_minor" stroke="#6d28d9" fill="#ddd6fe" fillOpacity={0.4} name="Simulated Recovered" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Activity Feed */}
        <div className="p-6 bg-white border border-[#e5e1d5] rounded-xl space-y-4 shadow-sm">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold font-mono text-[#111113] uppercase tracking-wider">DECISION MONITORING FEED</h3>
            <span className="text-[10px] font-mono px-2 py-0.5 bg-[#ecfdf5] text-[#047857] border border-[#a7f3d0] rounded font-bold">LIVE LOG</span>
          </div>
          <div className="space-y-2.5 overflow-y-auto max-h-64 pr-1">
            {activity.length === 0 ? (
              <div className="text-xs text-[#6e6d67] text-center py-8">No recent events logged.</div>
            ) : (
              activity.map((evt) => (
                <div key={evt.id} className="p-2.5 bg-[#fcfbf7] border border-[#e5e1d5] rounded-lg text-xs space-y-1">
                  <div className="flex items-center justify-between font-mono">
                    <span className="text-[#b45309] font-bold">{evt.event_type}</span>
                    <span className="text-[10px] text-[#6e6d67]">{evt.actor}</span>
                  </div>
                  <div className="text-[11px] text-[#6e6d67] font-mono truncate">Case: {evt.case_id || "System"}</div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
