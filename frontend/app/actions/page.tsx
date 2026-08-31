"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { formatCurrency, fetchApi } from "@/lib/api";
import { StatusBadge } from "@/components/StatusBadge";
import { TagBadge } from "@/components/TagBadge";
import { Play, ShieldCheck, RefreshCw, ArrowUpRight, Zap, CheckCircle2, Lock } from "lucide-react";

export default function ActionCenterScreen() {
  const [cases, setCases] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const loadActions = async () => {
    try {
      setLoading(true);
      const res = await fetchApi("/cases?page_size=25");
      setCases(res.data.items || []);
    } catch (e) {
      console.error("Action center load error", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadActions();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-[#e5e1d5]">
        <div>
          <h1 className="text-xl font-bold font-serif text-[#111113] tracking-tight">Recovery Action Center</h1>
          <p className="text-xs text-[#6e6d67] mt-1">Review policy-bounded recovery actions prior to simulation or Razorpay execution.</p>
        </div>
        <button onClick={loadActions} className="px-3.5 py-1.5 text-xs font-mono font-semibold bg-white hover:bg-[#f4f2e9] text-[#33322e] rounded-lg border border-[#d6d2c4] flex items-center space-x-1.5 shadow-sm transition">
          <RefreshCw className="w-3.5 h-3.5" />
          <span>REFRESH ACTIONS</span>
        </button>
      </div>

      {/* Action Categories Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 font-mono text-xs">
        <div className="p-4 bg-white border border-[#e5e1d5] rounded-xl space-y-1 shadow-sm">
          <div className="text-[10px] text-[#6e6d67] uppercase">RETRY_LATER</div>
          <div className="text-xl font-bold text-[#b45309]">Delayed Auto Retry</div>
          <div className="text-[10px] text-[#047857] font-bold">✓ Policy Bounded</div>
        </div>

        <div className="p-4 bg-white border border-[#e5e1d5] rounded-xl space-y-1 shadow-sm">
          <div className="text-[10px] text-[#6e6d67] uppercase">PAYMENT_METHOD_RECOVERY</div>
          <div className="text-xl font-bold text-[#6d28d9]">Method Swap Link</div>
          <div className="text-[10px] text-[#047857] font-bold">✓ Token Verification</div>
        </div>

        <div className="p-4 bg-white border border-[#e5e1d5] rounded-xl space-y-1 shadow-sm">
          <div className="text-[10px] text-[#6e6d67] uppercase">CUSTOMER_OUTREACH</div>
          <div className="text-xl font-bold text-[#0284c7]">Direct Email Link</div>
          <div className="text-[10px] text-[#b45309] font-bold">⚠ Contact Budget Gated</div>
        </div>

        <div className="p-4 bg-white border border-[#e5e1d5] rounded-xl space-y-1 shadow-sm">
          <div className="text-[10px] text-[#6e6d67] uppercase">HUMAN_ESCALATION</div>
          <div className="text-xl font-bold text-[#be123c]">Operator Review</div>
          <div className="text-[10px] text-[#be123c] font-bold">High Value / Low Confidence</div>
        </div>
      </div>

      {/* Proposed Actions Table */}
      <div className="bg-white border border-[#e5e1d5] rounded-xl overflow-hidden shadow-sm">
        <div className="p-4 border-b border-[#e5e1d5] flex items-center justify-between font-mono">
          <h3 className="text-xs font-bold text-[#111113] uppercase tracking-wider">PROPOSED RECOVERY ACTIONS QUEUE</h3>
          <span className="text-[10px] text-[#6e6d67]">Simulation-Before-Execution Enabled</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-[#f8f6f0] border-b border-[#e5e1d5] text-[#6e6d67] uppercase text-[11px]">
              <tr>
                <th className="py-3 px-4">Case & Customer</th>
                <th className="py-3 px-4">Amount Exposure</th>
                <th className="py-3 px-4">Proposed Action</th>
                <th className="py-3 px-4">Policy Gate</th>
                <th className="py-3 px-4">Mode</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#e5e1d5]">
              {loading ? (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-[#6e6d67]">Loading actions queue...</td>
                </tr>
              ) : cases.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-[#6e6d67]">No actions queued.</td>
                </tr>
              ) : (
                cases.map((c) => (
                  <tr key={c.case_id} className="hover:bg-[#fcfbf7] transition">
                    <td className="py-3.5 px-4">
                      <div className="font-bold text-[#111113]">{c.customer_name}</div>
                      <div className="text-[10px] text-[#6e6d67]">{c.case_id.substring(0, 16)}...</div>
                    </td>
                    <td className="py-3.5 px-4 font-bold text-[#b45309]">
                      {formatCurrency(c.amount_minor, c.currency)}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="text-[#0284c7] font-bold px-2 py-0.5 bg-[#f0f9ff] border border-[#bae6fd] rounded text-[11px]">
                        {c.recommended_action || "RETRY_LATER"}
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      <StatusBadge status={c.case_state === "ESCALATED" ? "ESCALATE" : (c.case_state === "RECOVERED" ? "BLOCK" : "ALLOW")} type="decision" />
                    </td>
                    <td className="py-3.5 px-4">
                      <TagBadge tag="SIMULATED" size="sm" />
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <Link
                        href={`/cases/${c.case_id}`}
                        className="inline-flex items-center space-x-1 px-3 py-1.5 bg-[#b8860b] hover:bg-[#92400e] text-white font-bold rounded text-[11px] shadow-sm transition"
                      >
                        <span>Review & Execute</span>
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
