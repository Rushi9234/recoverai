"use client";

import React from "react";
import Link from "next/link";
import { Play, ShieldAlert, RefreshCw, UserCheck, MessageSquare, AlertTriangle } from "lucide-react";

export default function ActionCenter() {
  const actions = [
    {
      type: "RETRY_LATER",
      name: "Scheduled Payment Retry",
      description: "Trigger a bounded payment retry attempt after transient failure cooldown.",
      safety: "Policy Check: PASS (Attempt 1/3)",
      color: "border-blue-800 bg-blue-950/30 text-blue-400"
    },
    {
      type: "PAYMENT_METHOD_RECOVERY",
      name: "Payment Method Recovery",
      description: "Send link for customer to update expired or invalid card details.",
      safety: "Policy Check: PASS",
      color: "border-emerald-800 bg-emerald-950/30 text-emerald-400"
    },
    {
      type: "CUSTOMER_OUTREACH",
      name: "Customer Outreach",
      description: "Draft and queue customer notification within contact guard budget.",
      safety: "Policy Check: PASS (1 contact in 24h)",
      color: "border-purple-800 bg-purple-950/30 text-purple-400"
    },
    {
      type: "HUMAN_ESCALATION",
      name: "Human Escalation",
      description: "Route ambiguous or high-value case to merchant operations queue.",
      safety: "Policy Check: ESCALATE",
      color: "border-amber-800 bg-amber-950/30 text-amber-400"
    }
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-gray-800">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">Recovery Action Center</h1>
          <p className="text-xs text-gray-400 mt-1">Bounded intervention workflows gated by merchant safety policies.</p>
        </div>
        <Link href="/cases" className="px-3.5 py-1.5 text-xs font-mono font-semibold bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition">
          View Active Cases
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {actions.map((act) => (
          <div key={act.type} className={`p-6 border rounded-xl space-y-4 ${act.color}`}>
            <div className="flex items-center justify-between">
              <h3 className="text-base font-bold font-mono text-white">{act.name}</h3>
              <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-gray-900 border border-gray-800 text-gray-300">
                {act.type}
              </span>
            </div>
            <p className="text-xs text-gray-300 leading-relaxed">{act.description}</p>
            <div className="p-2.5 bg-gray-900/80 border border-gray-800 rounded-lg text-xs font-mono text-gray-300 flex items-center justify-between">
              <span>{act.safety}</span>
              <span className="text-emerald-400 font-bold">POLICY GATED</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
