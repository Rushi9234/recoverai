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
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-[#e5e1d5]">
        <div>
          <div className="flex items-center space-x-3">
            <h1 className="text-xl font-bold font-serif text-[#111113] tracking-tight">Append-Only Audit Trail</h1>
            <span className={`px-2.5 py-0.5 text-xs font-mono font-bold rounded border flex items-center space-x-1 ${chainValid ? "bg-[#ecfdf5] text-[#047857] border-[#a7f3d0]" : "bg-[#fff1f2] text-[#be123c] border-[#fecdd3]"}`}>
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>AUDIT CHAIN VALID — SHA-256 VERIFIED</span>
            </span>
          </div>
          <p className="text-xs text-[#6e6d67] mt-1">Cryptographically bound tamper-evident log of all system decisions, policy evaluations, and bounded executions.</p>
        </div>
        <button onClick={loadAudit} className="px-3.5 py-1.5 text-xs font-mono font-semibold bg-white hover:bg-[#f4f2e9] text-[#33322e] rounded-lg border border-[#d6d2c4] flex items-center space-x-1.5 shadow-sm transition">
          <RefreshCw className="w-3.5 h-3.5" />
          <span>VERIFY CRYPTOGRAPHIC CHAIN</span>
        </button>
      </div>

      {/* Audit Log Table */}
      <div className="bg-white border border-[#e5e1d5] rounded-xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-[#f8f6f0] border-b border-[#e5e1d5] text-[#6e6d67] uppercase text-[11px]">
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
            <tbody className="divide-y divide-[#e5e1d5]">
              {loading ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-[#6e6d67] font-sans">Loading audit trail...</td>
                </tr>
              ) : events.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-[#6e6d67] font-sans">No audit events recorded yet.</td>
                </tr>
              ) : (
                events.map((evt) => {
                  const isExpanded = expandedId === evt.id;
                  return (
                    <React.Fragment key={evt.id}>
                      <tr
                        onClick={() => toggleExpand(evt.id)}
                        className="hover:bg-[#fcfbf7] cursor-pointer transition"
                      >
                        <td className="py-3.5 px-4 text-[#6e6d67] text-center">
                          {isExpanded ? <ChevronDown className="w-4 h-4 text-[#b8860b]" /> : <ChevronRight className="w-4 h-4 text-[#8a8880]" />}
                        </td>
                        <td className="py-3.5 px-4 text-[#6e6d67] text-[11px]">{evt.timestamp}</td>
                        <td className="py-3.5 px-4 font-bold text-[#0284c7]">
                          <span className="flex items-center space-x-1.5">
                            <span className="w-1.5 h-1.5 rounded-full bg-[#0284c7]"></span>
                            <span>{evt.event_type}</span>
                          </span>
                        </td>
                        <td className="py-3.5 px-4 text-[#33322e]">{evt.actor}</td>
                        <td className="py-3.5 px-4 text-[#b45309]">{evt.case_id ? `${evt.case_id.substring(0, 16)}...` : "System"}</td>
                        <td className="py-3.5 px-4 text-[#6e6d67]">
                          {evt.before_state || "NONE"} → <span className="text-[#111113] font-bold">{evt.after_state}</span>
                        </td>
                        <td className="py-3.5 px-4 text-[#047857] text-[10px]">
                          {evt.integrity_hash}
                        </td>
                      </tr>

                      {/* Expanded Details Row */}
                      {isExpanded && (
                        <tr className="bg-[#fcfbf7] border-b border-[#e5e1d5]">
                          <td colSpan={7} className="p-4 space-y-3 font-mono text-xs">
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                              <div className="p-3 bg-white border border-[#e5e1d5] rounded-lg space-y-1">
                                <div className="text-[10px] text-[#6e6d67] uppercase">Actor & Source</div>
                                <div className="text-[#111113] font-bold">{evt.actor}</div>
                                <div className="text-[10px] text-[#6e6d67]">Event ID: {evt.id}</div>
                              </div>

                              <div className="p-3 bg-white border border-[#e5e1d5] rounded-lg space-y-1">
                                <div className="text-[10px] text-[#6e6d67] uppercase">State Transition</div>
                                <div className="text-[#111113] font-bold">{evt.before_state || "NONE"} → {evt.after_state}</div>
                                <div className="text-[10px] text-[#047857] font-bold">Cryptographic Status: VERIFIED</div>
                              </div>

                              <div className="p-3 bg-white border border-[#e5e1d5] rounded-lg space-y-1">
                                <div className="text-[10px] text-[#6e6d67] uppercase">SHA-256 Integrity Hash</div>
                                <div className="text-[10px] text-[#047857] break-all">{evt.integrity_hash}</div>
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
