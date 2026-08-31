"use client";

import React, { useState } from "react";
import { fetchApi } from "@/lib/api";
import { UserCheck, ShieldCheck, AlertCircle, RefreshCw, Lock, MessageSquare, CheckCircle2, XCircle, ShieldAlert } from "lucide-react";

export default function ContactGuardScreen() {
  const [customerId, setCustomerId] = useState("cust_ananya_303");
  const [result, setResult] = useState<any>({
    allowed: false,
    reason: "24H_CONTACT_LIMIT_EXCEEDED — Customer has received 1 outreach message in the last 24 hours (Limit: 1).",
    details: {
      contacts_24h: 1,
      limit_24h: 1,
      contacts_7d: 2,
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
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="p-4 bg-[#111827] border border-gray-800 rounded-xl space-y-1">
          <div className="text-[10px] font-mono text-gray-400 uppercase">24H Contact Cap</div>
          <div className="text-xl font-bold font-mono text-blue-400">1 / 24 hrs</div>
          <div className="text-[10px] text-gray-400 font-mono">Max 1 outreach message per day</div>
        </div>

        <div className="p-4 bg-[#111827] border border-gray-800 rounded-xl space-y-1">
          <div className="text-[10px] font-mono text-gray-400 uppercase">7-Day Contact Cap</div>
          <div className="text-xl font-bold font-mono text-purple-400">3 / 7 days</div>
          <div className="text-[10px] text-gray-400 font-mono">Max 3 outreach messages per week</div>
        </div>

        <div className="p-4 bg-[#111827] border border-gray-800 rounded-xl space-y-1">
          <div className="text-[10px] font-mono text-gray-400 uppercase">Quiet Cooldown</div>
          <div className="text-xl font-bold font-mono text-amber-400">24 Hours</div>
          <div className="text-[10px] text-gray-400 font-mono">Mandatory quiet period</div>
        </div>

        <div className="p-4 bg-[#111827] border border-gray-800 rounded-xl space-y-1">
          <div className="text-[10px] font-mono text-gray-400 uppercase">Consent Status</div>
          <div className="text-xl font-bold font-mono text-emerald-400">CONSENTED</div>
          <div className="text-[10px] text-gray-400 font-mono">Verified merchant opt-in</div>
        </div>

        <div className="p-4 bg-[#111827] border border-gray-800 rounded-xl space-y-1">
          <div className="text-[10px] font-mono text-gray-400 uppercase">Suppression State</div>
          <div className="text-xl font-bold font-mono text-emerald-400">NONE</div>
          <div className="text-[10px] text-gray-400 font-mono">No active DND/opt-out</div>
        </div>
      </div>

      {/* Safety Demonstration: AI Recommendation vs Contact Guard Block */}
      <div className="p-5 bg-[#0e1626] border border-red-900/60 rounded-xl space-y-3 shadow-xl">
        <div className="flex items-center space-x-2 text-xs font-mono font-bold text-red-400 uppercase">
          <ShieldAlert className="w-4 h-4 text-red-400" />
          <span>SAFETY DEMONSTRATION — CONTACT BUDGET OVERRIDE</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 font-mono text-xs">
          <div className="p-4 bg-gray-900 border border-gray-800 rounded-lg space-y-2">
            <div className="flex items-center justify-between text-blue-400 font-bold">
              <span>1. AI RECOMMENDED ACTION</span>
              <MessageSquare className="w-4 h-4" />
            </div>
            <div className="text-sm text-white font-bold">CUSTOMER_OUTREACH</div>
            <p className="text-[11px] text-gray-400 font-sans">AI proposes sending email link to update payment instrument details for customer Ananya Roy (`cust_ananya_303`).</p>
          </div>

          <div className="p-4 bg-gray-900 border border-red-900/60 rounded-lg space-y-2">
            <div className="flex items-center justify-between text-red-400 font-bold">
              <span>2. CONTACT GUARD DECISION</span>
              <Lock className="w-4 h-4" />
            </div>
            <div className="text-sm text-red-400 font-bold">DECISION: BLOCKED</div>
            <p className="text-[11px] text-red-300 font-sans">Reason: 24-hour contact limit exceeded (1 message sent in last 24h). Contact Guard overrides AI proposal and prevents sending message.</p>
          </div>
        </div>
      </div>

      {/* Test Form & Evaluation Result */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Form */}
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
              <span>CHECK CONTACT GUARD BUDGET</span>
            </button>
          </form>
        </div>

        {/* Evaluation Output */}
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
