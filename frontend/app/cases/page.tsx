"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { formatCurrency, fetchApi } from "@/lib/api";
import { StatusBadge } from "@/components/StatusBadge";
import { Search, Filter, ArrowUpRight, ShieldAlert, RefreshCw, Info } from "lucide-react";

export default function RiskQueue() {
  const [cases, setCases] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [priorityFilter, setPriorityFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [search, setSearch] = useState("");

  const loadCases = async () => {
    try {
      setLoading(true);
      let query = "/cases?page_size=50";
      if (priorityFilter) query += `&priority=${priorityFilter}`;
      if (statusFilter) query += `&status=${statusFilter}`;
      if (search) query += `&search=${encodeURIComponent(search)}`;

      const res = await fetchApi(query);
      setCases(res.data.items || []);
    } catch (e) {
      console.error("Error loading cases", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCases();
  }, [priorityFilter, statusFilter, search]);

  const getCaseSubtext = (c: any) => {
    const custName = (c.customer_name || "").toLowerCase();
    const state = (c.case_state || "").toUpperCase();

    if (custName.includes("priya") || state === "RECOVERED") {
      return "Recovery outcome recorded in simulation mode.";
    }
    if (custName.includes("vikram") || state === "ESCALATED") {
      return "High-value review required before autonomous action.";
    }
    if (custName.includes("ananya") || state === "WAIT") {
      return "Retry budget exhausted — waiting for the configured recovery window / human resolution.";
    }
    return "Prioritized recurring failure case.";
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-gray-800">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">Revenue Risk Queue</h1>
          <p className="text-xs text-gray-400 mt-1">Prioritized cases of recurring payment failure revenue exposure.</p>
        </div>
        <button onClick={loadCases} className="px-3.5 py-1.5 text-xs font-mono font-semibold bg-gray-800 hover:bg-gray-700 text-gray-200 rounded-lg border border-gray-700 flex items-center space-x-1.5 self-start sm:self-auto">
          <RefreshCw className="w-3.5 h-3.5" />
          <span>REFRESH QUEUE</span>
        </button>
      </div>

      {/* Filters Bar */}
      <div className="flex flex-col sm:flex-row items-center gap-3 p-3 bg-[#111827] border border-gray-800 rounded-xl">
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-gray-400" />
          <input
            type="text"
            placeholder="Search by failure code..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-gray-900 border border-gray-700 text-xs text-gray-200 rounded-lg pl-9 pr-3 py-2 focus:outline-none focus:border-blue-500 font-mono"
          />
        </div>

        <div className="flex items-center space-x-3 w-full sm:w-auto">
          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="bg-gray-900 border border-gray-700 text-xs text-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:border-blue-500 font-mono"
          >
            <option value="">All Priorities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-gray-900 border border-gray-700 text-xs text-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:border-blue-500 font-mono"
          >
            <option value="">All States</option>
            <option value="NEW">New</option>
            <option value="RISK_DETECTED">Risk Detected</option>
            <option value="POLICY_CHECK">Policy Check</option>
            <option value="EXECUTING">Executing</option>
            <option value="RECOVERED">Recovered</option>
            <option value="BLOCKED">Blocked</option>
            <option value="ESCALATED">Escalated</option>
            <option value="WAIT">Wait</option>
          </select>
        </div>
      </div>

      {/* Cases Table */}
      <div className="bg-[#111827] border border-gray-800 rounded-xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-gray-900/80 border-b border-gray-800 font-mono text-gray-400 uppercase text-[11px]">
              <tr>
                <th className="py-3 px-4">Customer & Case</th>
                <th className="py-3 px-4">Amount</th>
                <th className="py-3 px-4">Priority</th>
                <th className="py-3 px-4">Risk Score</th>
                <th className="py-3 px-4">Failure Code</th>
                <th className="py-3 px-4">AI Recommended Action</th>
                <th className="py-3 px-4">Current State & Subtext</th>
                <th className="py-3 px-4 text-right">Next Best Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/60 font-mono">
              {loading ? (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-gray-400">Loading risk queue...</td>
                </tr>
              ) : cases.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-gray-400">No matching cases found.</td>
                </tr>
              ) : (
                cases.map((c) => (
                  <tr key={c.case_id} className="hover:bg-gray-800/40 transition">
                    <td className="py-3.5 px-4">
                      <div className="font-bold text-gray-200">{c.customer_name}</div>
                      <div className="text-[10px] text-gray-400">{c.case_id.substring(0, 18)}...</div>
                    </td>
                    <td className="py-3.5 px-4 font-bold text-amber-400">
                      {formatCurrency(c.amount_minor, c.currency)}
                    </td>
                    <td className="py-3.5 px-4">
                      <StatusBadge status={c.priority} type="priority" />
                    </td>
                    <td className="py-3.5 px-4 font-bold text-gray-200">
                      {c.risk_score} / 100
                    </td>
                    <td className="py-3.5 px-4 text-gray-300">
                      {c.failure_code || "gateway_timeout"}
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="text-[10px] text-gray-400 font-sans uppercase mb-0.5">AI PROPOSED</div>
                      <span className="text-blue-400 font-bold px-2 py-0.5 bg-blue-950 border border-blue-800/80 rounded text-[11px] inline-block">
                        {c.recommended_action || "RETRY_LATER"}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 space-y-1">
                      <div className="text-[10px] text-gray-400 font-sans uppercase mb-0.5">CONTROL STATE</div>
                      <div><StatusBadge status={c.case_state} type="state" /></div>
                      <div className="text-[10px] text-gray-400 font-sans italic max-w-xs">{getCaseSubtext(c)}</div>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <Link
                        href={`/cases/${c.case_id}`}
                        className="inline-flex items-center space-x-1 px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded text-[11px] shadow-sm shadow-blue-600/30 transition"
                      >
                        <span>Trace Case</span>
                        <ArrowUpRight className="w-3.5 h-3.5" />
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
