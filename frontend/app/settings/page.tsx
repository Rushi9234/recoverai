"use client";

import React, { useEffect, useState } from "react";
import { fetchApi } from "@/lib/api";
import { Sliders, ShieldCheck, CheckCircle2, Save, RefreshCw, Lock, UserCheck, AlertTriangle, Layers } from "lucide-react";

export default function SettingsPolicyScreen() {
  const [policy, setPolicy] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState<string | null>(null);

  const loadPolicy = async () => {
    try {
      setLoading(true);
      const res = await fetchApi("/policy");
      setPolicy(res.data);
    } catch (e) {
      console.error("Policy load error", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPolicy();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSaving(true);
      setSaveMessage(null);
      const res = await fetchApi("/policy", {
        method: "PUT",
        body: JSON.stringify(policy)
      });
      setPolicy(res.data);
      setSaveMessage(`Policy parameters successfully updated & deployed as Version v${res.data.version}!`);
    } catch (err: any) {
      console.error("Save error", err);
    } finally {
      setSaving(false);
    }
  };

  if (loading && !policy) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex items-center space-x-3 text-[#6e6d67] font-mono text-xs">
          <RefreshCw className="w-4 h-4 animate-spin text-[#d97706]" />
          <span>Loading Merchant Guardrail Policy...</span>
        </div>
      </div>
    );
  }

  const p = policy || {};

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-[#e5e1d5]">
        <div>
          <h1 className="text-xl font-bold font-serif text-[#111113] tracking-tight">Merchant Policy & Guardrails</h1>
          <p className="text-xs text-[#6e6d67] mt-1">Configure deterministic parameters and safety controls governing AI action execution.</p>
        </div>
        <div className="flex items-center space-x-2 font-mono text-xs">
          <span className="px-3 py-1 bg-[#fffbeb] text-[#b45309] border border-[#fde68a] rounded font-bold">
            POLICY VERSION: v{p.version || 1}
          </span>
          <span className="px-3 py-1 bg-[#ecfdf5] text-[#047857] border border-[#a7f3d0] rounded font-bold">
            ACTIVE & ENFORCED
          </span>
        </div>
      </div>

      {saveMessage && (
        <div className="p-4 bg-[#ecfdf5] border border-[#a7f3d0] text-[#047857] rounded-xl text-xs font-mono flex items-center space-x-2 shadow-sm">
          <CheckCircle2 className="w-4 h-4 text-[#047857] shrink-0" />
          <span>{saveMessage}</span>
        </div>
      )}

      <form onSubmit={handleSave} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 font-mono text-xs">
          {/* Group 1: RECOVERY LIMITS */}
          <div className="p-6 bg-white border border-[#e5e1d5] rounded-xl space-y-4 shadow-sm">
            <div className="flex items-center space-x-2 border-b border-[#e5e1d5] pb-3">
              <Lock className="w-4 h-4 text-[#0284c7]" />
              <h3 className="text-xs font-bold text-[#111113] uppercase tracking-wider">1. RECOVERY RETRY LIMITS</h3>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-[#6e6d67] mb-1">Max Retry Limit</label>
                <input
                  type="number"
                  value={p.retry_limit || 3}
                  onChange={(e) => setPolicy({ ...p, retry_limit: Number(e.target.value) })}
                  className="w-full bg-[#fcfbf7] border border-[#e5e1d5] text-[#111113] rounded-lg px-3 py-2 focus:outline-none focus:border-[#b8860b] font-mono"
                />
                <p className="text-[10px] text-[#6e6d67] mt-1">Hard cap on maximum payment retry attempts per subscription billing cycle.</p>
              </div>

              <div>
                <label className="block text-[#6e6d67] mb-1">Retry Cooldown (Hours)</label>
                <input
                  type="number"
                  value={p.cooldown_hours || 24}
                  onChange={(e) => setPolicy({ ...p, cooldown_hours: Number(e.target.value) })}
                  className="w-full bg-[#fcfbf7] border border-[#e5e1d5] text-[#111113] rounded-lg px-3 py-2 focus:outline-none focus:border-[#b8860b] font-mono"
                />
                <p className="text-[10px] text-[#6e6d67] mt-1">Required quiet period between consecutive payment retry attempts.</p>
              </div>
            </div>
          </div>

          {/* Group 2: CUSTOMER CONTACT LIMITS */}
          <div className="p-6 bg-white border border-[#e5e1d5] rounded-xl space-y-4 shadow-sm">
            <div className="flex items-center space-x-2 border-b border-[#e5e1d5] pb-3">
              <UserCheck className="w-4 h-4 text-[#6d28d9]" />
              <h3 className="text-xs font-bold text-[#111113] uppercase tracking-wider">2. CUSTOMER CONTACT BUDGET</h3>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-[#6e6d67] mb-1">24-Hour Contact Limit</label>
                <input
                  type="number"
                  value={p.contact_limit_24h || 1}
                  onChange={(e) => setPolicy({ ...p, contact_limit_24h: Number(e.target.value) })}
                  className="w-full bg-[#fcfbf7] border border-[#e5e1d5] text-[#111113] rounded-lg px-3 py-2 focus:outline-none focus:border-[#b8860b] font-mono"
                />
                <p className="text-[10px] text-[#6e6d67] mt-1">Maximum customer outreach notifications permitted within a 24-hour window.</p>
              </div>

              <div>
                <label className="block text-[#6e6d67] mb-1">7-Day Contact Limit</label>
                <input
                  type="number"
                  value={p.contact_limit_7d || 3}
                  onChange={(e) => setPolicy({ ...p, contact_limit_7d: Number(e.target.value) })}
                  className="w-full bg-[#fcfbf7] border border-[#e5e1d5] text-[#111113] rounded-lg px-3 py-2 focus:outline-none focus:border-[#b8860b] font-mono"
                />
                <p className="text-[10px] text-[#6e6d67] mt-1">Maximum customer outreach notifications permitted within a 7-day window.</p>
              </div>
            </div>
          </div>

          {/* Group 3: ESCALATION */}
          <div className="p-6 bg-white border border-[#e5e1d5] rounded-xl space-y-4 shadow-sm">
            <div className="flex items-center space-x-2 border-b border-[#e5e1d5] pb-3">
              <AlertTriangle className="w-4 h-4 text-[#b45309]" />
              <h3 className="text-xs font-bold text-[#111113] uppercase tracking-wider">3. ESCALATION RULES</h3>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-[#6e6d67] mb-1">High-Value Threshold (Paise)</label>
                <input
                  type="number"
                  value={p.high_value_threshold_minor || 1000000}
                  onChange={(e) => setPolicy({ ...p, high_value_threshold_minor: Number(e.target.value) })}
                  className="w-full bg-[#fcfbf7] border border-[#e5e1d5] text-[#111113] rounded-lg px-3 py-2 focus:outline-none focus:border-[#b8860b] font-mono"
                />
                <p className="text-[10px] text-[#6e6d67] mt-1">Amounts exceeding this require human operator sign-off (Default: 1,000,000 paise = ₹10,000).</p>
              </div>

              <div>
                <label className="block text-[#6e6d67] mb-1">Min Confidence Escalation Threshold</label>
                <input
                  type="number"
                  step="0.05"
                  value={p.escalation_confidence || 0.70}
                  onChange={(e) => setPolicy({ ...p, escalation_confidence: Number(e.target.value) })}
                  className="w-full bg-[#fcfbf7] border border-[#e5e1d5] text-[#111113] rounded-lg px-3 py-2 focus:outline-none focus:border-[#b8860b] font-mono"
                />
                <p className="text-[10px] text-[#6e6d67] mt-1">AI confidence below this threshold automatically triggers human escalation.</p>
              </div>
            </div>
          </div>

          {/* Group 4: ALLOWED ACTIONS */}
          <div className="p-6 bg-white border border-[#e5e1d5] rounded-xl space-y-4 shadow-sm">
            <div className="flex items-center space-x-2 border-b border-[#e5e1d5] pb-3">
              <Layers className="w-4 h-4 text-[#047857]" />
              <h3 className="text-xs font-bold text-[#111113] uppercase tracking-wider">4. PERMITTED RECOVERY ACTIONS</h3>
            </div>

            <div className="space-y-2">
              {["RETRY_LATER", "PAYMENT_METHOD_RECOVERY", "CUSTOMER_OUTREACH", "HUMAN_ESCALATION"].map((act) => (
                <div key={act} className="flex items-center justify-between p-2.5 bg-[#fcfbf7] border border-[#e5e1d5] rounded-lg text-xs font-mono">
                  <span className="text-[#111113] font-semibold">{act}</span>
                  <span className="text-[#047857] font-bold text-[10px] px-2 py-0.5 bg-[#ecfdf5] border border-[#a7f3d0] rounded">PERMITTED</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Save Button */}
        <div className="pt-2">
          <button
            type="submit"
            disabled={saving}
            className="px-6 py-3 bg-[#b8860b] hover:bg-[#92400e] text-white font-mono font-bold rounded-lg shadow-sm flex items-center space-x-2 transition"
          >
            {saving ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
            <span>SAVE & DEPLOY POLICY PARAMETERS</span>
          </button>
        </div>
      </form>
    </div>
  );
}
