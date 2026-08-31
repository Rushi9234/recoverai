"use client";

import React, { useState } from "react";
import { fetchApi } from "@/lib/api";
import { UserCheck, ShieldCheck, AlertCircle, RefreshCw, Lock, MessageSquare, CheckCircle2, XCircle, ShieldAlert, ArrowDown } from "lucide-react";

export default function ContactGuardScreen() {
  const [customerId, setCustomerId] = useState("cust_ananya_303");
  const [result, setResult] = useState<any>({
    allowed: false,
    reason: "24H_CONTACT_LIMIT_EXCEEDED — Customer has received 1 outreach message in the last 24 hours (Limit: 1).",
    details: {
      contacts_24h: 1,
      limit_24h: 1,
      contacts_7d: 3,
      limit_7d: 3,
      cooldown_remaining_hours: 18.5
    }
  });
  const [loading, setLoading] = useState(false);

  const checkGuard = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      const res = await fetchApi("/contact-guard/check", {
        method: "POST",
        body: JSON.stringify({ customer_id: customerId || undefined, channel: "EMAIL" })
      });
      setResult(res.data);
    } catch (err) {
      console.error("Guard check error", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-gray-800">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">Customer Contact Guard</h1>
          <p className="text-xs text-gray-400 mt-1">Enforces strict outreach frequency limits, cooldown periods, consent verification, and suppression lists.</p>
        </div>
        <div className="flex items-center space-x-2 font-mono text-xs text-emerald-400 bg-emerald-950/80 border border-emerald-800 px-3 py-1.5 rounded-lg">
          <ShieldCheck className="w-4 h-4" />
          <span>CONTACT BUDGET ACTIVE</span>
        </div>
      </div>

      {/* Contact Budget Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 font-mono text-xs">
        {/* Card 1: 24H Contact Cap */}
        <div className="p-4 bg-[#111827] border border-gray-800 rounded-xl space-y-1">
          <div className="text-[10px] text-gray-400 uppercase">24H Contact Cap</div>
          <div className="text-lg font-bold text-red-400">USED: 1 / 1</div>
          <div className="text-[10px] text-red-400 font-bold">NEXT OUTREACH: BLOCKED</div>
        </div>

        {/* Card 2: 7-Day Contact Cap */}
        <div className="p-4 bg-[#111827] border border-gray-800 rounded-xl space-y-1">
          <div className="text-[10px] text-gray-400 uppercase">7-Day Contact Cap</div>
          <div className="text-lg font-bold text-amber-400">USED: 3 / 3</div>
          <div className="text-[10px] text-amber-400 font-bold">STATUS: AT LIMIT</div>
        </div>

        {/* Card 3: Quiet Cooldown */}
        <div className="p-4 bg-[#111827] border border-gray-800 rounded-xl space-y-1">
          <div className="text-[10px] text-gray-400 uppercase">Quiet Cooldown</div>
          <div className="text-lg font-bold text-amber-400">24 Hours</div>
          <div className="text-[10px] text-gray-400">Mandatory quiet period</div>
        </div>

        {/* Card 4: Consent Status */}
        <div className="p-4 bg-[#111827] border border-gray-800 rounded-xl space-y-1">
          <div className="text-[10px] text-gray-400 uppercase">Consent Status</div>
          <div className="text-lg font-bold text-emerald-400">CONSENTED</div>
          <div className="text-[10px] text-gray-400">Verified opt-in</div>
        </div>

        {/* Card 5: Suppression State */}
        <div className="p-4 bg-[#111827] border border-gray-800 rounded-xl space-y-1">
          <div className="text-[10px] text-gray-400 uppercase">Suppression State</div>
          <div className="text-lg font-bold text-emerald-400">NONE</div>
          <div className="text-[10px] text-gray-400">No active opt-out</div>
        </div>
      </div>

      {/* Safety Panel Explicit Story: AI PROPOSAL -> CONTACT GUARD BLOCKED -> REASON */}
      <div className="p-6 bg-[#0e1626] border border-red-900/80 rounded-xl space-y-4 shadow-xl">
        <div className="flex items-center space-x-2 text-xs font-mono font-bold text-red-400 uppercase border-b border-red-900/60 pb-2">
          <ShieldAlert className="w-4 h-4 text-red-400" />
          <span>SAFETY DEMONSTRATION — CONTACT BUDGET OVERRIDE</span>
        </div>

        <div className="flex flex-col md:flex-row items-center justify-between gap-4 font-mono text-xs">
          {/* Step 1: AI PROPOSAL */}
          <div className="flex-1 p-4 bg-gray-900 border border-gray-800 rounded-lg space-y-1 text-center w-full">
            <div className="text-[10px] text-blue-400 font-bold uppercase">1. AI PROPOSAL</div>
            <div className="text-sm text-white font-bold">CUSTOMER_OUTREACH</div>
            <div className="text-[10px] text-gray-400 font-sans">Proposes sending payment link email</div>
          </div>

          <ArrowDown className="w-5 h-5 text-red-400 md:-rotate-90 shrink-0" />

          {/* Step 2: CONTACT GUARD */}
          <div className="flex-1 p-4 bg-gray-900 border border-red-900/80 rounded-lg space-y-1 text-center w-full">
            <div className="text-[10px] text-red-400 font-bold uppercase">2. CONTACT GUARD</div>
            <div className="text-sm text-red-400 font-bold">BLOCKED</div>
            <div className="text-[10px] text-red-300 font-sans">Budget cap enforced</div>
          </div>

          <ArrowDown className="w-5 h-5 text-red-400 md:-rotate-90 shrink-0" />

          {/* Step 3: REASON & INVARIANT */}
          <div className="flex-1 p-4 bg-gray-900 border border-red-900/80 rounded-lg space-y-1 text-center w-full">
            <div className="text-[10px] text-gray-400 font-bold uppercase">3. REASON & INVARIANT</div>
            <div className="text-xs text-red-300 font-bold">24-hour contact limit already reached.</div>
            <div className="text-[10px] text-emerald-400 font-bold font-sans">This action never reached the messaging executor.</div>
          </div>
        </div>
      </div>

      {/* Test Form & Evaluation Result */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="p-6 bg-[#111827] border border-gray-800 rounded-xl space-y-4">
          <h3 className="text-xs font-mono font-bold text-gray-200 uppercase">TEST CONTACT BUDGET EVALUATION</h3>

          <form onSubmit={checkGuard} className="space-y-4 font-mono text-xs">
            <div>
              <label className="block text-gray-400 mb-1">Customer ID / Ref</label>
              <input
                type="text"
                value={customerId}
                onChange={(e) => setCustomerId(e.target.value)}
                className="w-full bg-gray-900 border border-gray-700 text-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:border-blue-500"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-lg shadow-lg shadow-blue-600/30 flex items-center justify-center space-x-2 transition"
            >
              {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <UserCheck className="w-4 h-4" />}
              <span>EVALUATE CUSTOMER OUTREACH BUDGET</span>
            </button>
          </form>
        </div>

        <div className="p-6 bg-[#111827] border border-gray-800 rounded-xl space-y-4">
          <h3 className="text-xs font-mono font-bold text-gray-200 uppercase">EVALUATION RESULT</h3>

          {result ? (
            <div className="space-y-3 font-mono text-xs">
              <div className="flex items-center justify-between p-3 bg-gray-900 border border-gray-800 rounded-lg">
                <span className="text-gray-400">Budget Status:</span>
                <span className={`font-bold ${result.allowed ? "text-emerald-400" : "text-red-400"}`}>
                  {result.allowed ? "ALLOWED (PASS)" : "BLOCKED (CAP EXCEEDED)"}
                </span>
              </div>

              <div className="p-3 bg-gray-900 border border-gray-800 rounded-lg space-y-1">
                <div className="text-gray-400">Evaluation Detail:</div>
                <div className="text-gray-200 font-bold">{result.reason}</div>
              </div>
            </div>
          ) : (
            <div className="py-12 text-center text-xs font-mono text-gray-500">
              Submit form to evaluate customer contact budget rules.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
