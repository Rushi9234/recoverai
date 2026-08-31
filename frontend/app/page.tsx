"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { formatCurrency, fetchApi } from "@/lib/api";
import { StatusBadge } from "@/components/StatusBadge";
import { TagBadge } from "@/components/TagBadge";
import { AlertCircle, ArrowUpRight, CheckCircle2, ShieldAlert, Zap, TrendingUp, RefreshCw } from "lucide-react";
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, BarChart, Bar, CartesianGrid } from "recharts";

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
        <div className="flex items-center space-x-3 text-gray-400 font-mono text-sm">
          <RefreshCw className="w-5 h-5 animate-spin text-blue-500" />
          <span>Loading Executive Dashboard...</span>
        </div>
      </div>
    );
  }

  const s = summary || {};

  return (
    <div className="space-y-8">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 pb-6 border-b border-gray-800">
        <div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight">Executive Revenue Control Plane</h1>
          <p className="text-sm text-gray-400 mt-1">Real-time revenue risk detection, evidence-backed AI diagnosis, and policy-gated recovery.</p>
        </div>
        <div className="flex items-center space-x-3">
          <button onClick={loadData} className="px-3.5 py-2 text-xs font-mono font-semibold bg-gray-800 hover:bg-gray-700 text-gray-200 rounded-lg border border-gray-700 flex items-center space-x-1.5 transition">
            <RefreshCw className="w-3.5 h-3.5" />
            <span>REFRESH</span>
          </button>
          <Link href="/cases" className="px-4 py-2 text-xs font-bold bg-blue-600 hover:bg-blue-500 text-white rounded-lg shadow-lg shadow-blue-600/30 flex items-center space-x-1.5 transition">
            <span>View Highest-Risk Cases</span>
            <ArrowUpRight className="w-4 h-4" />
          </Link>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 bg-[#111827] border border-gray-800 rounded-xl space-y-2">
          <div className="flex items-center justify-between text-xs font-mono text-gray-400">
            <span>REVENUE AT RISK</span>
            <AlertCircle className="w-4 h-4 text-amber-500" />
          </div>
          <div className="text-2xl font-bold font-mono text-amber-400">{formatCurrency(s.revenue_at_risk_minor || 0)}</div>
          <div className="text-[11px] text-gray-400">{s.active_cases || 0} active recovery cases</div>
        </div>

        <div className="p-5 bg-[#111827] border border-gray-800 rounded-xl space-y-2">
          <div className="flex items-center justify-between text-xs font-mono text-gray-400">
            <span>OBSERVED RECOVERED</span>
            <TagBadge tag="OBSERVED" />
          </div>
          <div className="text-2xl font-bold font-mono text-emerald-400">{formatCurrency(s.observed_recovered_minor || 0)}</div>
          <div className="text-[11px] text-gray-400">Confirmed live payment outcomes</div>
        </div>

        <div className="p-5 bg-[#111827] border border-gray-800 rounded-xl space-y-2">
          <div className="flex items-center justify-between text-xs font-mono text-gray-400">
            <span>SIMULATED RECOVERED</span>
            <TagBadge tag="SIMULATED" />
          </div>
          <div className="text-2xl font-bold font-mono text-purple-400">{formatCurrency(s.simulated_recovered_minor || 0)}</div>
          <div className="text-[11px] text-gray-400">Bounded simulation test execution</div>
        </div>

        <div className="p-5 bg-[#111827] border border-gray-800 rounded-xl space-y-2">
          <div className="flex items-center justify-between text-xs font-mono text-gray-400">
            <span>RECOVERY RATE</span>
            <TrendingUp className="w-4 h-4 text-emerald-500" />
          </div>
          <div className="text-2xl font-bold font-mono text-white">{((s.recovery_rate || 0) * 100).toFixed(1)}%</div>
          <div className="text-[11px] text-gray-400">{s.successful_recoveries || 0} successful recoveries</div>
        </div>
      </div>

      {/* Secondary KPI Strip */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4 bg-[#0d1322] border border-gray-800 rounded-xl text-center">
        <div>
          <div className="text-xs font-mono text-gray-400">ACTIVE CASES</div>
          <div className="text-lg font-bold font-mono text-blue-400 mt-0.5">{s.active_cases || 0}</div>
        </div>
        <div>
          <div className="text-xs font-mono text-gray-400">SUCCESSFUL RECOVERIES</div>
          <div className="text-lg font-bold font-mono text-emerald-400 mt-0.5">{s.successful_recoveries || 0}</div>
        </div>
        <div>
          <div className="text-xs font-mono text-gray-400">HUMAN ESCALATED</div>
          <div className="text-lg font-bold font-mono text-amber-400 mt-0.5">{s.escalated_cases || 0}</div>
        </div>
        <div>
          <div className="text-xs font-mono text-gray-400">POLICY BLOCKED</div>
          <div className="text-lg font-bold font-mono text-red-400 mt-0.5">{s.blocked_actions || 0}</div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 p-6 bg-[#111827] border border-gray-800 rounded-xl space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold font-mono text-gray-200">7-DAY RECOVERY PERFORMANCE</h3>
            <span className="text-xs text-gray-400 font-mono">Simulated vs Risk Exposure</span>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trends}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                <XAxis dataKey="date" stroke="#6b7280" fontSize={11} />
                <YAxis stroke="#6b7280" fontSize={11} tickFormatter={(val) => `₹${val/1000}k`} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#1f2937", borderColor: "#374151", color: "#fff" }}
                  formatter={(val: any) => [`₹${(Number(val)/100).toLocaleString()}`, "Amount"]}
                />
                <Area type="monotone" dataKey="risk_minor" stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.15} name="Risk" />
                <Area type="monotone" dataKey="simulated_recovered_minor" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.25} name="Simulated Recovered" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Activity Feed */}
        <div className="p-6 bg-[#111827] border border-gray-800 rounded-xl space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold font-mono text-gray-200">AGENT ACTIVITY FEED</h3>
            <span className="text-[10px] font-mono px-2 py-0.5 bg-emerald-950 text-emerald-400 border border-emerald-800 rounded">LIVE AUDIT</span>
          </div>
          <div className="space-y-3 overflow-y-auto max-h-64 pr-1">
            {activity.length === 0 ? (
              <div className="text-xs text-gray-400 text-center py-8">No recent events logged.</div>
            ) : (
              activity.map((evt) => (
                <div key={evt.id} className="p-2.5 bg-gray-900/60 border border-gray-800 rounded-lg text-xs space-y-1">
                  <div className="flex items-center justify-between font-mono">
                    <span className="text-blue-400 font-semibold">{evt.event_type}</span>
                    <span className="text-[10px] text-gray-400">{evt.actor}</span>
                  </div>
                  <div className="text-[11px] text-gray-400 font-mono truncate">Case: {evt.case_id || "System"}</div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
