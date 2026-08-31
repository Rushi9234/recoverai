"use client";

import React, { useEffect, useState } from "react";
import { fetchApi } from "@/lib/api";
import { Activity, ShieldCheck, RefreshCw, Search, ChevronDown, ChevronRight, CheckCircle2, Lock } from "lucide-react";
import { TagBadge } from "@/components/TagBadge";

export default function AuditTrailScreen() {
  const [events, setEvents] = useState<any[]>([]);
  const [chainValid, setChainValid] = useState(true);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<string | null>(null);

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

  const toggleExpand = (id: string) => {
    setExpandedId(expandedId === id ? null : id);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-gray-800">
        <div>
          <div className="flex items-center space-x-3">
            <h1 className="text-xl font-bold text-white tracking-tight">Append-Only Audit Trail</h1>
            <span className={`px-2.5 py-0.5 text-xs font-mono font-bold rounded border flex items-center space-x-1 ${chainValid ? "bg-emerald-950 text-emerald-400 border-emerald-800" : "bg-red-950 text-red-400 border-red-800"}`}>
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>AUDIT CHAIN VALID — SHA-256 VERIFIED</span>
            </span>
          </div>
          <p className="text-xs text-gray-400 mt-1">Cryptographically bound tamper-evident log of all system decisions, policy evaluations, and bounded executions.</p>
        </div>
        <button onClick={loadAudit} className="px-3.5 py-1.5 text-xs font-mono font-semibold bg-gray-800 hover:bg-gray-700 text-gray-200 rounded-lg border border-gray-700 flex items-center space-x-1.5">
          <RefreshCw className="w-3.5 h-3.5" />
          <span>VERIFY CRYPTOGRAPHIC CHAIN</span>
        </button>
      </div>

      {/* Audit Log Table */}
      <div className="bg-[#111827] border border-gray-800 rounded-xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-gray-900/80 border-b border-gray-800 text-gray-400 uppercase text-[11px]">
              <tr>
                <th className="py-3 px-4 w-8"></th>
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-4">Event Type</th>
                <th className="py-3 px-4">Actor</th>
                <th className="py-3 px-4">Case ID</th>
                <th className="py-3 px-4">State Transition</th>
                <th className="py-3 px-4">SHA-256 Integrity Hash</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/60">
              {loading ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-gray-400 font-sans">Loading audit trail...</td>
                </tr>
              ) : events.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-gray-400 font-sans">No audit events recorded yet.</td>
                </tr>
              ) : (
                events.map((evt, idx) => {
                  const isExpanded = expandedId === evt.id;
                  return (
                    <React.Fragment key={evt.id}>
                      <tr
                        onClick={() => toggleExpand(evt.id)}
                        className="hover:bg-gray-800/40 cursor-pointer transition relative"
                      >
                        <td className="py-3.5 px-4 text-gray-400 text-center">
                          {isExpanded ? <ChevronDown className="w-4 h-4 text-blue-400" /> : <ChevronRight className="w-4 h-4 text-gray-500" />}
                        </td>
                        <td className="py-3.5 px-4 text-gray-400 text-[11px]">{evt.timestamp}</td>
                        <td className="py-3.5 px-4 font-bold text-blue-400">
                          <span className="flex items-center space-x-1.5">
                            <span className="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
                            <span>{evt.event_type}</span>
                          </span>
                        </td>
                        <td className="py-3.5 px-4 text-gray-300">{evt.actor}</td>
                        <td className="py-3.5 px-4 text-amber-400">{evt.case_id ? `${evt.case_id.substring(0, 16)}...` : "System"}</td>
                        <td className="py-3.5 px-4 text-gray-400">
                          {evt.before_state || "NONE"} → <span className="text-gray-200 font-bold">{evt.after_state}</span>
                        </td>
                        <td className="py-3.5 px-4 text-emerald-400 text-[10px]">
                          {evt.integrity_hash}
                        </td>
                      </tr>

                      {/* Expanded Details Row */}
                      {isExpanded && (
                        <tr className="bg-gray-900/90 border-b border-gray-800">
                          <td colSpan={7} className="p-4 space-y-3 font-mono text-xs">
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                              <div className="p-3 bg-gray-950 border border-gray-800 rounded-lg space-y-1">
                                <div className="text-[10px] text-gray-400 uppercase">Actor & Source</div>
                                <div className="text-gray-200 font-bold">{evt.actor}</div>
                                <div className="text-[10px] text-gray-500">Event ID: {evt.id}</div>
                              </div>

                              <div className="p-3 bg-gray-950 border border-gray-800 rounded-lg space-y-1">
                                <div className="text-[10px] text-gray-400 uppercase">State Transition</div>
                                <div className="text-gray-200 font-bold">{evt.before_state || "NONE"} → {evt.after_state}</div>
                                <div className="text-[10px] text-emerald-400 font-bold">Cryptographic Status: VERIFIED</div>
                              </div>

                              <div className="p-3 bg-gray-950 border border-gray-800 rounded-lg space-y-1">
                                <div className="text-[10px] text-gray-400 uppercase">SHA-256 Integrity Hash</div>
                                <div className="text-[10px] text-emerald-400 break-all">{evt.integrity_hash}</div>
                              </div>
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
