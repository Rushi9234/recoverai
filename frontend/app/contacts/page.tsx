"use client";

import React, { useState } from "react";
import { fetchApi } from "@/lib/api";
import { UserCheck, ShieldCheck, AlertCircle, RefreshCw } from "lucide-react";

export default function ContactGuardScreen() {
  const [customerId, setCustomerId] = useState("");
  const [result, setResult] = useState<any>(null);
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
      <div className="pb-4 border-b border-gray-800">
        <h1 className="text-xl font-bold text-white tracking-tight">Customer Contact Guard</h1>
        <p className="text-xs text-gray-400 mt-1">Enforce strict contact frequency caps (24h/7d limits, cooldowns, consent & suppression).</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Guard Check Form */}
        <div className="p-6 bg-[#111827] border border-gray-800 rounded-xl space-y-4">
          <h3 className="text-xs font-mono font-bold text-gray-200 uppercase">TEST CONTACT BUDGET CHECK</h3>

          <form onSubmit={checkGuard} className="space-y-4 font-mono text-xs">
            <div>
              <label className="block text-gray-400 mb-1">Customer Ref / ID (Optional)</label>
              <input
                type="text"
                placeholder="cust_demo_101"
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
              <span>EVALUATE CONTACT GUARD BUDGET</span>
            </button>
          </form>
        </div>

        {/* Evaluation Output */}
        <div className="p-6 bg-[#111827] border border-gray-800 rounded-xl space-y-4">
          <h3 className="text-xs font-mono font-bold text-gray-200 uppercase">GUARD EVALUATION RESULT</h3>

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
