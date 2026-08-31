"use client";

import React, { useEffect, useState } from "react";
import { fetchApi } from "@/lib/api";
import { Sliders, ShieldCheck, CheckCircle2, Save, RefreshCw } from "lucide-react";

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
      setSaveMessage(`Policy updated successfully to version ${res.data.version}!`);
    } catch (err: any) {
      console.error("Save error", err);
    } finally {
      setSaving(false);
    }
  };

  if (loading && !policy) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex items-center space-x-3 text-gray-400 font-mono text-sm">
          <RefreshCw className="w-5 h-5 animate-spin text-blue-500" />
          <span>Loading Merchant Policy...</span>
        </div>
      </div>
    );
  }

  const p = policy || {};

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-gray-800">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">Merchant Policy & Guardrails</h1>
          <p className="text-xs text-gray-400 mt-1">Configure deterministic parameters governing AI action execution.</p>
        </div>
        <div className="text-xs font-mono px-3 py-1 bg-blue-950 text-blue-400 border border-blue-800 rounded font-bold">
          Policy Version: v{p.version || 1}
        </div>
      </div>

      {saveMessage && (
        <div className="p-4 bg-emerald-950 border border-emerald-800 text-emerald-300 rounded-xl text-xs font-mono flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          <span>{saveMessage}</span>
        </div>
      )}

      <form onSubmit={handleSave} className="space-y-6">
        <div className="p-6 bg-[#111827] border border-gray-800 rounded-xl space-y-6 font-mono text-xs">
          <h3 className="text-xs font-bold text-gray-200 uppercase tracking-wider">HARD POLICY LIMITS</h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-gray-400 mb-1">Max Retry Limit</label>
              <input
                type="number"
                value={p.retry_limit || 3}
                onChange={(e) => setPolicy({ ...p, retry_limit: Number(e.target.value) })}
                className="w-full bg-gray-900 border border-gray-700 text-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:border-blue-500"
              />
              <p className="text-[10px] text-gray-500 mt-1">Hard cap on payment retry attempts per subscription.</p>
            </div>

            <div>
              <label className="block text-gray-400 mb-1">Contact Limit (24 Hours)</label>
              <input
                type="number"
                value={p.contact_limit_24h || 1}
                onChange={(e) => setPolicy({ ...p, contact_limit_24h: Number(e.target.value) })}
                className="w-full bg-gray-900 border border-gray-700 text-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:border-blue-500"
              />
              <p className="text-[10px] text-gray-500 mt-1">Maximum customer outreach messages allowed within 24 hours.</p>
            </div>

            <div>
              <label className="block text-gray-400 mb-1">Contact Limit (7 Days)</label>
              <input
                type="number"
                value={p.contact_limit_7d || 3}
                onChange={(e) => setPolicy({ ...p, contact_limit_7d: Number(e.target.value) })}
                className="w-full bg-gray-900 border border-gray-700 text-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:border-blue-500"
              />
              <p className="text-[10px] text-gray-500 mt-1">Maximum customer outreach messages allowed within 7 days.</p>
            </div>

            <div>
              <label className="block text-gray-400 mb-1">Cooldown Hours</label>
              <input
                type="number"
                value={p.cooldown_hours || 24}
                onChange={(e) => setPolicy({ ...p, cooldown_hours: Number(e.target.value) })}
                className="w-full bg-gray-900 border border-gray-700 text-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:border-blue-500"
              />
              <p className="text-[10px] text-gray-500 mt-1">Required quiet period between consecutive contact events.</p>
            </div>

            <div>
              <label className="block text-gray-400 mb-1">High-Value Review Threshold (Paise)</label>
              <input
                type="number"
                value={p.high_value_threshold_minor || 1000000}
                onChange={(e) => setPolicy({ ...p, high_value_threshold_minor: Number(e.target.value) })}
                className="w-full bg-gray-900 border border-gray-700 text-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:border-blue-500"
              />
              <p className="text-[10px] text-gray-500 mt-1">Amounts exceeding this require human operator sign-off (Default: ₹10,000).</p>
            </div>

            <div>
              <label className="block text-gray-400 mb-1">Minimum Confidence Escalation Threshold</label>
              <input
                type="number"
                step="0.05"
                value={p.escalation_confidence || 0.70}
                onChange={(e) => setPolicy({ ...p, escalation_confidence: Number(e.target.value) })}
                className="w-full bg-gray-900 border border-gray-700 text-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:border-blue-500"
              />
              <p className="text-[10px] text-gray-500 mt-1">AI confidence below this automatically triggers human escalation.</p>
            </div>
          </div>

          <div className="pt-4 border-t border-gray-800">
            <button
              type="submit"
              disabled={saving}
              className="px-6 py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-lg shadow-lg shadow-blue-600/30 flex items-center space-x-2 transition"
            >
              {saving ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
              <span>SAVE & DEPLOY POLICY PARAMETERS</span>
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
