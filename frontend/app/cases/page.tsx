"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { formatCurrency, fetchApi } from "@/lib/api";
import { StatusBadge } from "@/components/StatusBadge";
import { Search, Filter, ArrowUpRight, ShieldAlert, RefreshCw } from "lucide-react";

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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-gray-800">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">Revenue Risk Queue</h1>
          <p className="text-xs text-gray-400 mt-1">Prioritized cases of recurring payment revenue slipping away.</p>
        </div>
        <button onClick={loadCases} className="px-3.5 py-1.5 text-xs font-mono font-semibold bg-gray-800 hover:bg-gray-700 text-gray-200 rounded-lg border border-gray-700 flex items-center space-x-1.5 self-start sm:self-auto">
          <RefreshCw className="w-3.5 h-3.5" />
          <span>REFRESH</span>
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
          </select>
        </div>
      </div>

      {/* Cases Table */}
      <div className="bg-[#111827] border border-gray-800 rounded-xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-gray-900/80 border-b border-gray-800 font-mono text-gray-400 uppercase text-[11px]">
              <tr>
                <th className="py-3 px-4">Case / Customer</th>
                <th className="py-3 px-4">Amount</th>
                <th className="py-3 px-4">Priority</th>
                <th className="py-3 px-4">Risk Score</th>
                <th className="py-3 px-4">Failure Code</th>
                <th className="py-3 px-4">Recommended Action</th>
                <th className="py-3 px-4">State</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/60 font-mono">
              {loading ? (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-gray-400">Loading cases...</td>
                </tr>
              ) : cases.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-gray-400">No matching cases found.</td>
                </tr>
              ) : (
                cases.map((c) => (
                  <tr key={c.case_id} className="hover:bg-gray-800/40 transition">
                    <td className="py-3 px-4">
                      <div className="font-bold text-gray-200">{c.customer_name}</div>
                      <div className="text-[10px] text-gray-400">{c.case_id.substring(0, 18)}...</div>
                    </td>
                    <td className="py-3 px-4 font-bold text-amber-400">
                      {formatCurrency(c.amount_minor, c.currency)}
                    </td>
                    <td className="py-3 px-4">
                      <StatusBadge status={c.priority} type="priority" />
                    </td>
                    <td className="py-3 px-4 font-bold text-gray-200">
                      {c.risk_score} / 100
                    </td>
                    <td className="py-3 px-4 text-gray-300">
                      {c.failure_code || "gateway_timeout"}
                    </td>
                    <td className="py-3 px-4 text-blue-400 font-semibold">
                      {c.recommended_action || "RETRY_LATER"}
                    </td>
                    <td className="py-3 px-4">
                      <StatusBadge status={c.case_state} type="state" />
                    </td>
                    <td className="py-3 px-4 text-right">
                      <Link
                        href={`/cases/${c.case_id}`}
                        className="inline-flex items-center space-x-1 px-3 py-1 bg-blue-950 hover:bg-blue-900 text-blue-400 border border-blue-800 rounded font-semibold text-[11px] transition"
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
