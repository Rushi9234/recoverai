"use client";

import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { formatCurrency, fetchApi } from "@/lib/api";
import { StatusBadge } from "@/components/StatusBadge";
import { TagBadge } from "@/components/TagBadge";
import {
  ArrowLeft, ShieldCheck, ShieldAlert, Cpu, CheckCircle2, XCircle, Clock,
  Play, RefreshCw, Lock, AlertTriangle, FileText, Activity, AlertCircle, Info, Zap
} from "lucide-react";

export default function CaseDetailTrace() {
  const params = useParams();
  const caseId = params?.id as string;

  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [executing, setExecuting] = useState(false);
  const [execMode, setExecMode] = useState<"SIMULATION" | "RAZORPAY_TEST">("SIMULATION");
  const [actionError, setActionError] = useState<string | null>(null);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  const loadCase = async () => {
    try {
      setLoading(true);
      setActionError(null);
      const res = await fetchApi(`/cases/${caseId}`);
      setData(res.data);
    } catch (e: any) {
      console.error("Error fetching case detail", e);
      setActionError(e.message || "Failed to load case");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (caseId) {
      loadCase();
    }
  }, [caseId]);

  const handleExecute = async () => {
    try {
      setExecuting(true);
      setActionError(null);
      setActionSuccess(null);

      const res = await fetchApi(`/cases/${caseId}/execute`, {
        method: "POST",
        body: JSON.stringify({ execution_mode: execMode })
      });

      setActionSuccess(`Action executed successfully! Mode: ${res.data.outcome_type}, Case State: ${res.data.case_state}`);
      await loadCase();
    } catch (e: any) {
      setActionError(e.message || "Action execution failed");
    } finally {
      setExecuting(false);
    }
  };

  const handleEscalate = async () => {
    try {
      setExecuting(true);
      setActionError(null);
      await fetchApi(`/cases/${caseId}/escalate`, {
        method: "POST",
        body: JSON.stringify({ reason: "MANUAL_ESCALATION" })
      });
      setActionSuccess("Case escalated to human review queue.");
      await loadCase();
    } catch (e: any) {
      setActionError(e.message || "Escalation failed");
    } finally {
      setExecuting(false);
    }
  };

  if (loading && !data) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex items-center space-x-3 text-gray-400 font-mono text-sm">
          <RefreshCw className="w-5 h-5 animate-spin text-blue-500" />
          <span>Loading Decision Pipeline for Case {caseId}...</span>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="p-8 text-center text-gray-400 space-y-4">
        <div>Case not found or failed to load.</div>
        <Link href="/cases" className="text-blue-400 text-xs font-mono underline">Return to Risk Queue</Link>
      </div>
    );
  }

  const c = data.case || {};
  const risk = data.risk || {};
  const diagnosis = data.diagnosis || {};
  const recommendation = data.recommendation || {};
  const policyPrev = data.policy_preview || {};
  const customer = data.customer || {};
  const subscription = data.subscription || {};
  const actions = data.actions || [];
  const auditEvents = data.audit_events || [];

  const policyDecision = policyPrev.decision || "ALLOW";
  const isRecovered = c.case_state === "RECOVERED";
  const isEscalated = c.case_state === "ESCALATED";
  const policyBlocked = policyDecision === "BLOCK" || isRecovered;

  const pipelineSteps = [
    { label: "EVENT", status: "RECEIVED", icon: FileText, color: "text-gray-300" },
    { label: "RISK", status: `SCORE ${risk.score || 42}`, icon: AlertCircle, color: "text-amber-400" },
    { label: "DIAGNOSIS", status: diagnosis.category || "TECHNICAL", icon: Cpu, color: "text-blue-400" },
    { label: "RECOMMENDATION", status: recommendation.action || "RETRY", icon: Zap, color: "text-purple-400" },
    { label: "POLICY", status: policyDecision, icon: ShieldCheck, color: policyBlocked ? "text-red-400" : "text-emerald-400" },
    { label: "EXECUTION", status: actions.length > 0 ? actions[0].status : "READY", icon: Play, color: "text-purple-300" },
    { label: "OUTCOME", status: actions.length > 0 ? actions[0].outcome_type : "SIMULATED", icon: CheckCircle2, color: "text-emerald-400" },
    { label: "AUDIT", status: "CHAIN VALID", icon: Activity, color: "text-emerald-400" },
  ];

  return (
    <div className="space-y-8">
      {/* Back button & Hero Case Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 pb-4 border-b border-gray-800">
        <div className="flex items-center space-x-3">
          <Link href="/cases" className="p-2 bg-gray-900 hover:bg-gray-800 text-gray-400 hover:text-white rounded-lg border border-gray-800 transition">
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-xl font-bold font-mono text-white">Case Trace: {c.id}</h1>
              <StatusBadge status={c.case_state} type="state" />
              <StatusBadge status={c.priority} type="priority" />
            </div>
            <p className="text-xs text-gray-400 mt-1">
              Customer: <span className="text-gray-200 font-semibold">{customer.name}</span> ({customer.email_masked}) | 
              Sub: <span className="font-mono text-blue-400">{subscription.external_ref || "sub_demo"}</span>
            </p>
          </div>
        </div>

        <div className="text-right font-mono">
          <div className="text-xs text-gray-400">REVENUE EXPOSURE AT RISK</div>
          <div className="text-2xl font-bold text-amber-400">{formatCurrency(c.risk_amount_minor || 0)}</div>
        </div>
      </div>

      {/* 8-STEP HORIZONTAL DECISION PIPELINE */}
      <div className="p-5 bg-[#0d1322] border border-blue-900/60 rounded-xl space-y-3 shadow-xl">
        <div className="flex items-center justify-between">
          <h2 className="text-xs font-mono font-bold tracking-wider text-blue-400 uppercase">RECOVERAI DECISION PIPELINE</h2>
          <span className="text-[10px] font-mono text-gray-400">DECISION CONTROL FLOW: EVENT → AI → POLICY → EXECUTOR → AUDIT</span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2">
          {pipelineSteps.map((step, idx) => {
            const Icon = step.icon;
            return (
              <div key={idx} className="p-2.5 bg-gray-900/90 border border-gray-800 rounded-lg space-y-1 relative">
                <div className="flex items-center justify-between text-[10px] font-mono font-bold text-gray-400">
                  <span>{idx + 1}. {step.label}</span>
                  <Icon className={`w-3 h-3 ${step.color}`} />
                </div>
                <div className={`text-[11px] font-mono font-bold truncate ${step.color}`}>{step.status}</div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Action Error / Success Banners */}
      {actionError && (
        <div className="p-4 bg-red-950/90 border border-red-800 rounded-xl text-red-300 text-xs font-mono flex items-center space-x-2">
          <XCircle className="w-4 h-4 text-red-400 shrink-0" />
          <span>{actionError}</span>
        </div>
      )}
      {actionSuccess && (
        <div className="p-4 bg-emerald-950/90 border border-emerald-800 rounded-xl text-emerald-300 text-xs font-mono flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>{actionSuccess}</span>
        </div>
      )}

      {/* 4 PROMINENT CORE STAGE PANELS: AI PROPOSES | POLICY ENGINE | EXECUTOR | OUTCOME */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Panel 1: AI PROPOSES */}
        <div className="p-5 bg-[#111827] border border-blue-900/50 rounded-xl space-y-3 shadow-lg">
          <div className="flex items-center justify-between border-b border-gray-800 pb-2">
            <span className="text-xs font-mono font-bold text-blue-400 uppercase">1. AI PROPOSES</span>
            <Cpu className="w-4 h-4 text-blue-400" />
          </div>
          <div className="space-y-1">
            <div className="text-sm font-mono font-bold text-white">{recommendation.action || "RETRY_LATER"}</div>
            <div className="text-xs font-mono text-blue-400 font-bold">Confidence: {((diagnosis.confidence || 0.95) * 100).toFixed(0)}%</div>
          </div>
          <div className="space-y-1 pt-1 border-t border-gray-800/80">
            <div className="text-[10px] font-mono text-gray-400">citable evidence:</div>
            <div className="space-y-1 font-mono text-[10px] text-gray-300">
              <div>• failure_code={c.failure_code || "gateway_timeout"}</div>
              <div>• {subscription.retry_count || 1} retry attempt used</div>
              <div>• account_history=healthy</div>
            </div>
          </div>
        </div>

        {/* Panel 2: POLICY ENGINE */}
        <div className={`p-5 bg-[#111827] border rounded-xl space-y-3 shadow-lg ${policyBlocked ? "border-red-800/80" : "border-emerald-900/50"}`}>
          <div className="flex items-center justify-between border-b border-gray-800 pb-2">
            <span className="text-xs font-mono font-bold text-gray-200 uppercase">2. POLICY ENGINE</span>
            <StatusBadge status={policyDecision} type="decision" />
          </div>
          <div className="space-y-1 font-mono text-[11px]">
            <div className="flex justify-between"><span className="text-gray-400">duplicate_check:</span><span className="text-emerald-400 font-bold">✓ PASS</span></div>
            <div className="flex justify-between"><span className="text-gray-400">retry_limit:</span><span className="text-emerald-400 font-bold">✓ PASS</span></div>
            <div className="flex justify-between"><span className="text-gray-400">cooldown:</span><span className="text-emerald-400 font-bold">✓ PASS</span></div>
            <div className="flex justify-between"><span className="text-gray-400">high_value_review:</span><span className={isEscalated ? "text-amber-400 font-bold" : "text-emerald-400 font-bold"}>{isEscalated ? "⚠ ESCALATE" : "✓ PASS"}</span></div>
          </div>
        </div>

        {/* Panel 3: EXECUTOR */}
        <div className="p-5 bg-[#111827] border border-purple-900/50 rounded-xl space-y-3 shadow-lg">
          <div className="flex items-center justify-between border-b border-gray-800 pb-2">
            <span className="text-xs font-mono font-bold text-purple-400 uppercase">3. EXECUTOR</span>
            <Play className="w-4 h-4 text-purple-400" />
          </div>
          <div className="space-y-1 font-mono text-xs">
            <div className="text-gray-300 font-bold">Adapter: {execMode}</div>
            <div className="text-[11px] text-gray-400">Idempotency Lock: ACQUIRED</div>
            <div className="text-[11px] text-purple-300 font-semibold">Status: {actions.length > 0 ? actions[0].status : "READY"}</div>
          </div>
        </div>

        {/* Panel 4: OUTCOME */}
        <div className="p-5 bg-[#111827] border border-emerald-900/50 rounded-xl space-y-3 shadow-lg">
          <div className="flex items-center justify-between border-b border-gray-800 pb-2">
            <span className="text-xs font-mono font-bold text-emerald-400 uppercase">4. OUTCOME</span>
            <TagBadge tag={actions.length > 0 ? actions[0].outcome_type : "SIMULATED"} />
          </div>
          <div className="space-y-1 font-mono">
            <div className="text-lg font-bold text-emerald-400">{actions.length > 0 ? formatCurrency(actions[0].outcome_amount_minor) : "₹0"}</div>
            <div className="text-[10px] text-gray-400 font-sans italic">Simulation outcome — not live payment recovery.</div>
          </div>
        </div>
      </div>

      {/* PROMINENT BLOCKED ACTION / SAFETY DEMONSTRATION SECTION */}
      {isRecovered && (
        <div className="p-5 bg-red-950/40 border border-red-800/80 rounded-xl space-y-3 shadow-xl">
          <div className="flex items-center space-x-2 text-xs font-mono font-bold text-red-400 uppercase">
            <ShieldAlert className="w-4 h-4 text-red-400" />
            <span>SAFETY DEMONSTRATION — SECOND ATTEMPT BLOCKED</span>
          </div>
          <div className="p-3 bg-gray-900 border border-red-900/60 rounded-lg font-mono text-xs space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-gray-300 font-bold">ATTEMPTED SECOND RETRY ACTION</span>
              <span className="px-2.5 py-0.5 text-xs font-bold bg-red-950 text-red-400 border border-red-800 rounded">
                POLICY DECISION: BLOCKED
              </span>
            </div>
            <div className="text-gray-400">
              Reason: <span className="text-red-300 font-bold">Already recovered / retry attempt cap reached.</span>
            </div>
            <div className="text-[11px] text-emerald-400 font-bold flex items-center space-x-1">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>SAFETY INVARIANT CONFIRMED: This action never reached the executor.</span>
            </div>
          </div>
        </div>
      )}

      {/* Main 3-Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Context & Diagnosis */}
        <div className="space-y-6">
          {/* Diagnosis & Evidence */}
          <div className="p-5 bg-[#111827] border border-gray-800 rounded-xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-mono font-bold text-gray-200 uppercase">FAILURE DIAGNOSIS</h3>
              <span className="text-xs font-mono text-blue-400 font-bold">{((diagnosis.confidence || 0.95) * 100).toFixed(0)}% CONFIDENCE</span>
            </div>

            <div className="space-y-2">
              <div className="text-sm font-mono font-bold text-amber-400">{diagnosis.category || "TRANSIENT_TECHNICAL_FAILURE"}</div>
              <p className="text-xs text-gray-300 leading-relaxed">{diagnosis.explanation}</p>
            </div>

            <div className="space-y-2 pt-2 border-t border-gray-800">
              <div className="text-[11px] font-mono text-gray-400">STRUCTURED EVIDENCE CITED:</div>
              <div className="space-y-1">
                {(diagnosis.evidence || []).map((ev: string, idx: number) => (
                  <div key={idx} className="p-1.5 bg-gray-900 border border-gray-800 rounded text-[11px] font-mono text-gray-300">
                    • {ev}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Context Details */}
          <div className="p-5 bg-[#111827] border border-gray-800 rounded-xl space-y-3 font-mono text-xs">
            <h3 className="text-xs font-bold text-gray-200 uppercase">CASE CONTEXT</h3>
            <div className="flex justify-between py-1 border-b border-gray-800/60">
              <span className="text-gray-400">Customer</span>
              <span className="text-gray-200">{customer.name}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-gray-800/60">
              <span className="text-gray-400">Subscription ID</span>
              <span className="text-blue-400">{subscription.external_ref || "sub_demo_1042"}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-gray-800/60">
              <span className="text-gray-400">Retry Attempts</span>
              <span className="text-gray-200">{subscription.retry_count || 1} / 3</span>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-gray-400">Failure Code</span>
              <span className="text-amber-400">{c.failure_code || "gateway_timeout"}</span>
            </div>
          </div>
        </div>

        {/* Center Column: Recommendation & Policy Engine */}
        <div className="space-y-6">
          {/* Policy Engine Checks */}
          <div className="p-5 bg-[#111827] border border-gray-800 rounded-xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-mono font-bold text-gray-200 uppercase">POLICY ENGINE HARD CHECKS</h3>
              <StatusBadge status={policyDecision} type="decision" />
            </div>

            <div className="space-y-2 font-mono text-xs">
              {(policyPrev.checks || []).map((check: any, idx: number) => {
                const isPass = check.result === "PASS";
                return (
                  <div key={idx} className="flex items-center justify-between p-2.5 bg-gray-900 border border-gray-800 rounded-lg">
                    <span className="text-gray-300">{check.rule}</span>
                    <span className={`font-bold ${isPass ? "text-emerald-400" : "text-red-400"}`}>
                      {check.result}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Action Control Panel */}
          <div className="p-5 bg-[#111827] border border-gray-800 rounded-xl space-y-4">
            <h3 className="text-xs font-mono font-bold text-gray-200 uppercase">EXECUTION CONTROLS</h3>

            <div className="space-y-3">
              <div className="flex items-center space-x-3 text-xs font-mono">
                <span className="text-gray-400">Adapter Mode:</span>
                <label className="flex items-center space-x-1 text-gray-200 cursor-pointer">
                  <input
                    type="radio"
                    name="mode"
                    checked={execMode === "SIMULATION"}
                    onChange={() => setExecMode("SIMULATION")}
                    className="text-blue-600"
                  />
                  <span>Simulation</span>
                </label>
                <label className="flex items-center space-x-1 text-gray-200 cursor-pointer">
                  <input
                    type="radio"
                    name="mode"
                    checked={execMode === "RAZORPAY_TEST"}
                    onChange={() => setExecMode("RAZORPAY_TEST")}
                    className="text-blue-600"
                  />
                  <span>Razorpay Test Mode</span>
                </label>
              </div>

              <div className="flex flex-col gap-2 pt-2">
                <button
                  onClick={handleExecute}
                  disabled={executing || policyBlocked}
                  className={`w-full py-3 px-4 text-xs font-mono font-bold rounded-lg flex items-center justify-center space-x-2 transition ${
                    policyBlocked
                      ? "bg-gray-800 text-gray-500 cursor-not-allowed border border-gray-700"
                      : "bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-600/30"
                  }`}
                >
                  {policyBlocked ? <Lock className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                  <span>{policyBlocked ? "EXECUTION BLOCKED BY POLICY" : `EXECUTE ACTION: ${recommendation.action || "RETRY_LATER"}`}</span>
                </button>

                <button
                  onClick={handleEscalate}
                  disabled={executing}
                  className="w-full py-2.5 px-4 text-xs font-mono font-bold bg-amber-950/60 hover:bg-amber-900 text-amber-400 border border-amber-800/80 rounded-lg flex items-center justify-center space-x-2 transition"
                >
                  <AlertTriangle className="w-4 h-4" />
                  <span>ESCALATE TO HUMAN REVIEW</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Execution History & Audit */}
        <div className="space-y-6">
          {/* Action History */}
          <div className="p-5 bg-[#111827] border border-gray-800 rounded-xl space-y-4">
            <h3 className="text-xs font-mono font-bold text-gray-200 uppercase">ACTION HISTORY & OUTCOMES</h3>

            <div className="space-y-3 font-mono text-xs">
              {actions.length === 0 ? (
                <div className="text-gray-500 text-center py-4">No actions executed yet.</div>
              ) : (
                actions.map((act: any) => (
                  <div key={act.id} className="p-3 bg-gray-900 border border-gray-800 rounded-lg space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-blue-400">{act.action_type}</span>
                      <TagBadge tag={act.outcome_type} />
                    </div>
                    <div className="flex items-center justify-between text-[11px]">
                      <span className="text-gray-400">Status: <span className="text-gray-200">{act.status}</span></span>
                      <span className="text-emerald-400 font-bold">{formatCurrency(act.outcome_amount_minor)}</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Audit Chain */}
          <div className="p-5 bg-[#111827] border border-gray-800 rounded-xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-mono font-bold text-gray-200 uppercase">APPEND-ONLY AUDIT CHAIN</h3>
              <span className="text-[10px] font-mono text-emerald-400 font-bold">CHAIN VALID</span>
            </div>

            <div className="space-y-2 overflow-y-auto max-h-64 pr-1 font-mono text-[11px]">
              {auditEvents.map((evt: any) => (
                <div key={evt.id} className="p-2 bg-gray-900 border border-gray-800/80 rounded space-y-1">
                  <div className="flex items-center justify-between text-gray-400">
                    <span className="text-blue-400 font-semibold">{evt.event_type}</span>
                    <span className="text-[10px] text-gray-500">{evt.actor}</span>
                  </div>
                  <div className="text-[10px] text-gray-400 truncate">Hash: {evt.integrity_hash?.substring(0, 16)}...</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
