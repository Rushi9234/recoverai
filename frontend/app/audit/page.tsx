"use client";

import React, { useEffect, useState } from "react";
import { fetchApi } from "@/lib/api";
import { Activity, ShieldCheck, RefreshCw, Search } from "lucide-react";

export default function AuditTrailScreen() {
  const [events, setEvents] = useState<any[]>([]);
  const [chainValid, setChainValid] = useState(true);
  const [loading, setLoading] = useState(true);

  const loadAudit = async () => {
    try {
      setLoading(true);
      const res = await fetchApi("/audit?page_size=50");
      setEvents(res.data.items || []);
      setChainValid(res.data.audit_chain_valid);
    } catch (e) {
      console.error("Audit load error", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAudit();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-gray-800">
        <div>
          <div className="flex items-center space-x-3">
            <h1 className="text-xl font-bold text-white tracking-tight">Append-Only Audit Trail</h1>
            <span className={`px-2.5 py-0.5 text-xs font-mono font-bold rounded border ${chainValid ? "bg-emerald-950 text-emerald-400 border-emerald-800" : "bg-red-950 text-red-400 border-red-800"}`}>
              {chainValid ? "AUDIT CHAIN: VALID (SHA-256 Verified)" : "AUDIT CHAIN: INVALID"}
            </span>
          </div>
          <p className="text-xs text-gray-400 mt-1">Cryptographically bound tamper-evident log of all system decisions and actions.</p>
        </div>
        <button onClick={loadAudit} className="px-3.5 py-1.5 text-xs font-mono font-semibold bg-gray-800 hover:bg-gray-700 text-gray-200 rounded-lg border border-gray-700 flex items-center space-x-1.5">
          <RefreshCw className="w-3.5 h-3.5" />
          <span>VERIFY & REFRESH</span>
        </button>
      </div>

      {/* Audit Log Table */}
      <div className="bg-[#111827] border border-gray-800 rounded-xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-gray-900/80 border-b border-gray-800 text-gray-400 uppercase text-[11px]">
              <tr>
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-4">Event Type</th>
                <th className="py-3 px-4">Actor</th>
                <th className="py-3 px-4">Case ID</th>
                <th className="py-3 px-4">Transition</th>
                <th className="py-3 px-4">SHA-256 Integrity Hash</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/60">
              {loading ? (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-gray-400">Loading audit log...</td>
                </tr>
              ) : events.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-gray-400">No audit events recorded yet.</td>
                </tr>
              ) : (
                events.map((evt) => (
                  <tr key={evt.id} className="hover:bg-gray-800/40 transition">
                    <td className="py-3 px-4 text-gray-400 text-[11px]">{evt.timestamp}</td>
                    <td className="py-3 px-4 font-bold text-blue-400">{evt.event_type}</td>
                    <td className="py-3 px-4 text-gray-300">{evt.actor}</td>
                    <td className="py-3 px-4 text-amber-400">{evt.case_id || "System"}</td>
                    <td className="py-3 px-4 text-gray-400">
                      {evt.before_state} → <span className="text-gray-200 font-bold">{evt.after_state}</span>
                    </td>
                    <td className="py-3 px-4 text-emerald-400 font-mono text-[10px]">
                      {evt.integrity_hash}
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
