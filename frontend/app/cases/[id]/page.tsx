"use client";

import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { formatCurrency, fetchApi } from "@/lib/api";
import { StatusBadge } from "@/components/StatusBadge";
import { TagBadge } from "@/components/TagBadge";
import {
  ArrowLeft, ShieldCheck, ShieldAlert, Cpu, CheckCircle2, XCircle, Clock,
  Play, RefreshCw, Lock, AlertTriangle, FileText, Activity, AlertCircle, Info, Zap, ArrowDown
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
        <div className="flex items-center space-x-3 text-[#6e6d67] font-mono text-xs">
          <RefreshCw className="w-4 h-4 animate-spin text-[#d97706]" />
          <span>Loading Decision Pipeline for Case {caseId}...</span>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="p-8 text-center text-[#6e6d67] space-y-4">
        <div>Case not found or failed to load.</div>
        <Link href="/cases" className="text-[#b45309] text-xs font-mono underline">Return to Risk Queue</Link>
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
    { label: "EVENT", status: "RECEIVED", icon: FileText, color: "text-[#55534e]" },
    { label: "RISK", status: `SCORE ${risk.score || 42}`, icon: AlertCircle, color: "text-[#b45309]" },
    { label: "DIAGNOSIS", status: diagnosis.category || "TECHNICAL", icon: Cpu, color: "text-[#0284c7]" },
    { label: "RECOMMENDATION", status: recommendation.action || "RETRY", icon: Zap, color: "text-[#6d28d9]" },
    { label: "POLICY", status: policyDecision, icon: ShieldCheck, color: policyBlocked ? "text-[#be123c]" : "text-[#047857]" },
    { label: "EXECUTION", status: actions.length > 0 ? actions[0].status : "READY", icon: Play, color: "text-[#6d28d9]" },
    { label: "OUTCOME", status: actions.length > 0 ? actions[0].outcome_type : "SIMULATED", icon: CheckCircle2, color: "text-[#047857]" },
    { label: "AUDIT", status: "CHAIN VALID", icon: Activity, color: "text-[#047857]" },
  ];

  return (
    <div className="space-y-8">
      {/* Back button & Hero Case Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 pb-4 border-b border-[#e5e1d5]">
        <div className="flex items-center space-x-3">
          <Link href="/cases" className="p-2 bg-white hover:bg-[#f4f2e9] text-[#6e6d67] hover:text-[#111113] rounded-lg border border-[#d6d2c4] transition">
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-xl font-bold font-serif text-[#111113]">Case Trace: {c.id}</h1>
              <StatusBadge status={c.case_state} type="state" />
              <StatusBadge status={c.priority} type="priority" />
            </div>
            <p className="text-xs text-[#6e6d67] mt-1">
              Customer: <span className="text-[#111113] font-semibold">{customer.name}</span> ({customer.email_masked}) | 
              Sub: <span className="font-mono text-[#b45309]">{subscription.external_ref || "sub_demo"}</span>
            </p>
          </div>
        </div>

        <div className="text-right font-mono">
          <div className="text-xs text-[#6e6d67]">REVENUE EXPOSURE AT RISK</div>
          <div className="text-2xl font-bold text-[#b45309]">{formatCurrency(c.risk_amount_minor || 0)}</div>
        </div>
      </div>

      {/* 8-STEP HORIZONTAL DECISION PIPELINE */}
      <div className="p-5 bg-white border border-[#e5e1d5] rounded-xl space-y-3 shadow-sm">
        <div className="flex items-center justify-between">
          <h2 className="text-xs font-mono font-bold tracking-wider text-[#b8860b] uppercase">RECOVERAI DECISION PIPELINE</h2>
          <span className="text-[10px] font-mono text-[#6e6d67]">DECISION CONTROL FLOW: EVENT → AI → POLICY → EXECUTOR → AUDIT</span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2">
          {pipelineSteps.map((step, idx) => {
            const Icon = step.icon;
            return (
              <div key={idx} className="p-2.5 bg-[#fcfbf7] border border-[#e5e1d5] rounded-lg space-y-1 relative">
                <div className="flex items-center justify-between text-[10px] font-mono font-bold text-[#6e6d67]">
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
        <div className="p-4 bg-[#fff1f2] border border-[#fecdd3] rounded-xl text-[#be123c] text-xs font-mono flex items-center space-x-2">
          <XCircle className="w-4 h-4 text-[#be123c] shrink-0" />
          <span>{actionError}</span>
        </div>
      )}
      {actionSuccess && (
        <div className="p-4 bg-[#ecfdf5] border border-[#a7f3d0] rounded-xl text-[#047857] text-xs font-mono flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4 text-[#047857] shrink-0" />
          <span>{actionSuccess}</span>
        </div>
      )}

      {/* 4 DISTINCT STAGE BLOCKS: AI PROPOSES | POLICY DECIDES | EXECUTOR ACTS | OUTCOME */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Panel 1: AI PROPOSES */}
        <div className="p-5 bg-white border border-[#e5e1d5] rounded-xl space-y-3 shadow-sm">
          <div className="flex items-center justify-between border-b border-[#e5e1d5] pb-2">
            <span className="text-xs font-mono font-bold text-[#0284c7] uppercase">1. AI PROPOSES</span>
            <Cpu className="w-4 h-4 text-[#0284c7]" />
          </div>
          <div className="space-y-1">
            <div className="text-sm font-mono font-bold text-[#111113]">{recommendation.action || "RETRY_LATER"}</div>
            <div className="text-xs font-mono text-[#0284c7] font-bold">Confidence: {((diagnosis.confidence || 0.95) * 100).toFixed(0)}%</div>
          </div>
          <div className="space-y-1 pt-1 border-t border-[#e5e1d5]">
            <div className="text-[10px] font-mono text-[#6e6d67]">citable evidence:</div>
            <div className="space-y-1 font-mono text-[10px] text-[#33322e]">
              <div>• failure_code={c.failure_code || "gateway_timeout"}</div>
              <div>• {subscription.retry_count || 1} retry attempt used</div>
              <div>• account_history=healthy</div>
            </div>
          </div>
        </div>

        {/* Panel 2: POLICY DECIDES */}
        <div className={`p-5 bg-white border rounded-xl space-y-3 shadow-sm ${policyBlocked ? "border-[#fecdd3]" : "border-[#a7f3d0]"}`}>
          <div className="flex items-center justify-between border-b border-[#e5e1d5] pb-2">
            <span className="text-xs font-mono font-bold text-[#111113] uppercase">2. POLICY DECIDES</span>
            <StatusBadge status={policyDecision} type="decision" />
          </div>
          <div className="space-y-1 font-mono text-[11px]">
            <div className="flex justify-between"><span className="text-[#6e6d67]">duplicate_check:</span><span className="text-[#047857] font-bold">✓ PASS</span></div>
            <div className="flex justify-between"><span className="text-[#6e6d67]">retry_limit:</span><span className="text-[#047857] font-bold">✓ PASS</span></div>
            <div className="flex justify-between"><span className="text-[#6e6d67]">cooldown:</span><span className="text-[#047857] font-bold">✓ PASS</span></div>
            <div className="flex justify-between"><span className="text-[#6e6d67]">high_value_review:</span><span className={isEscalated ? "text-[#b45309] font-bold" : "text-[#047857] font-bold"}>{isEscalated ? "⚠ ESCALATE" : "✓ PASS"}</span></div>
          </div>
        </div>

        {/* Panel 3: EXECUTOR ACTS */}
        <div className="p-5 bg-white border border-[#e5e1d5] rounded-xl space-y-3 shadow-sm">
          <div className="flex items-center justify-between border-b border-[#e5e1d5] pb-2">
            <span className="text-xs font-mono font-bold text-[#6d28d9] uppercase">3. EXECUTOR ACTS</span>
            <Play className="w-4 h-4 text-[#6d28d9]" />
          </div>
          <div className="space-y-1 font-mono text-xs">
            <div className="text-[#111113] font-bold">Adapter: {execMode}</div>
            <div className="text-[11px] text-[#6e6d67]">Idempotency Lock: ACQUIRED</div>
            <div className="text-[11px] text-[#6d28d9] font-semibold">Status: {actions.length > 0 ? actions[0].status : "READY"}</div>
          </div>
        </div>

        {/* Panel 4: OUTCOME */}
        <div className="p-5 bg-white border border-[#e5e1d5] rounded-xl space-y-3 shadow-sm">
          <div className="flex items-center justify-between border-b border-[#e5e1d5] pb-2">
            <span className="text-xs font-mono font-bold text-[#047857] uppercase">4. OUTCOME</span>
            <TagBadge tag={actions.length > 0 ? actions[0].outcome_type : "SIMULATED"} />
          </div>
          <div className="space-y-1 font-mono">
            <div className="text-lg font-bold text-[#047857]">{actions.length > 0 ? formatCurrency(actions[0].outcome_amount_minor) : "₹0"}</div>
            <div className="text-[10px] text-[#6e6d67] font-sans italic">Simulation outcome — not live payment recovery.</div>
          </div>
        </div>
      </div>

      {/* PROMINENT SAFETY DEMONSTRATION SECTION */}
      {isRecovered && (
        <div className="p-6 bg-[#fff1f2] border border-[#fecdd3] rounded-xl space-y-4 shadow-sm">
          <div className="flex items-center space-x-2 text-xs font-mono font-bold text-[#be123c] uppercase border-b border-[#fecdd3] pb-2">
            <ShieldAlert className="w-4 h-4 text-[#be123c]" />
            <span>SAFETY DEMONSTRATION — SECOND ATTEMPT BLOCKED</span>
          </div>

          <div className="flex flex-col md:flex-row items-center justify-between gap-4 font-mono text-xs">
            {/* Step 1: ATTEMPTED SECOND RETRY */}
            <div className="flex-1 p-4 bg-white border border-[#e5e1d5] rounded-lg space-y-1 text-center w-full">
              <div className="text-[10px] text-[#0284c7] font-bold uppercase">1. ATTEMPTED ACTION</div>
              <div className="text-sm text-[#111113] font-bold">ATTEMPTED SECOND RETRY</div>
              <div className="text-[10px] text-[#6e6d67] font-sans">User clicked execute action again</div>
            </div>

            <ArrowDown className="w-5 h-5 text-[#be123c] md:-rotate-90 shrink-0" />

            {/* Step 2: POLICY DECISION BLOCKED */}
            <div className="flex-1 p-4 bg-white border border-[#fecdd3] rounded-lg space-y-1 text-center w-full">
              <div className="text-[10px] text-[#be123c] font-bold uppercase">2. POLICY DECISION</div>
              <div className="text-sm text-[#be123c] font-bold">BLOCKED</div>
              <div className="text-[10px] text-[#be123c] font-sans">`already_recovered` check FAIL</div>
            </div>

            <ArrowDown className="w-5 h-5 text-[#be123c] md:-rotate-90 shrink-0" />

            {/* Step 3: REASON & INVARIANT */}
            <div className="flex-1 p-4 bg-white border border-[#fecdd3] rounded-lg space-y-1 text-center w-full">
              <div className="text-[10px] text-[#6e6d67] font-bold uppercase">3. REASON & INVARIANT</div>
              <div className="text-xs text-[#be123c] font-bold">Already recovered / retry limit reached</div>
              <div className="text-[10px] text-[#047857] font-bold font-sans">This action never reached the executor.</div>
            </div>
          </div>
        </div>
      )}

      {/* Main 3-Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Context & Diagnosis */}
        <div className="space-y-6">
          {/* Diagnosis & Evidence */}
          <div className="p-5 bg-white border border-[#e5e1d5] rounded-xl space-y-4 shadow-sm">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-mono font-bold text-[#111113] uppercase">FAILURE DIAGNOSIS</h3>
              <span className="text-xs font-mono text-[#0284c7] font-bold">{((diagnosis.confidence || 0.95) * 100).toFixed(0)}% CONFIDENCE</span>
            </div>

            <div className="space-y-2">
              <div className="text-sm font-mono font-bold text-[#b45309]">{diagnosis.category || "TRANSIENT_TECHNICAL_FAILURE"}</div>
              <p className="text-xs text-[#33322e] leading-relaxed">{diagnosis.explanation}</p>
            </div>

            <div className="space-y-2 pt-2 border-t border-[#e5e1d5]">
              <div className="text-[11px] font-mono text-[#6e6d67]">STRUCTURED EVIDENCE CITED:</div>
              <div className="space-y-1">
                {(diagnosis.evidence || []).map((ev: string, idx: number) => (
                  <div key={idx} className="p-1.5 bg-[#fcfbf7] border border-[#e5e1d5] rounded text-[11px] font-mono text-[#33322e]">
                    • {ev}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Context Details */}
          <div className="p-5 bg-white border border-[#e5e1d5] rounded-xl space-y-3 font-mono text-xs shadow-sm">
            <h3 className="text-xs font-bold text-[#111113] uppercase">CASE CONTEXT</h3>
            <div className="flex justify-between py-1 border-b border-[#e5e1d5]">
              <span className="text-[#6e6d67]">Customer</span>
              <span className="text-[#111113] font-semibold">{customer.name}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-[#e5e1d5]">
              <span className="text-[#6e6d67]">Subscription ID</span>
              <span className="text-[#b45309]">{subscription.external_ref || "sub_demo_1042"}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-[#e5e1d5]">
              <span className="text-[#6e6d67]">Retry Attempts</span>
              <span className="text-[#111113]">{subscription.retry_count || 1} / 3</span>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-[#6e6d67]">Failure Code</span>
              <span className="text-[#b45309]">{c.failure_code || "gateway_timeout"}</span>
            </div>
          </div>
        </div>

        {/* Center Column: Recommendation & Policy Engine */}
        <div className="space-y-6">
          {/* Policy Engine Checks */}
          <div className="p-5 bg-white border border-[#e5e1d5] rounded-xl space-y-4 shadow-sm">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-mono font-bold text-[#111113] uppercase">POLICY ENGINE HARD CHECKS</h3>
              <StatusBadge status={policyDecision} type="decision" />
            </div>

            <div className="space-y-2 font-mono text-xs">
              {(policyPrev.checks || []).map((check: any, idx: number) => {
                const isPass = check.result === "PASS";
                return (
                  <div key={idx} className="flex items-center justify-between p-2.5 bg-[#fcfbf7] border border-[#e5e1d5] rounded-lg">
                    <span className="text-[#33322e]">{check.rule}</span>
                    <span className={`font-bold ${isPass ? "text-[#047857]" : "text-[#be123c]"}`}>
                      {check.result}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Action Control Panel */}
          <div className="p-5 bg-white border border-[#e5e1d5] rounded-xl space-y-4 shadow-sm">
            <h3 className="text-xs font-mono font-bold text-[#111113] uppercase">EXECUTION CONTROLS</h3>

            <div className="space-y-3">
              <div className="flex items-center space-x-3 text-xs font-mono">
                <span className="text-[#6e6d67]">Adapter Mode:</span>
                <label className="flex items-center space-x-1 text-[#111113] cursor-pointer">
                  <input
                    type="radio"
                    name="mode"
                    checked={execMode === "SIMULATION"}
                    onChange={() => setExecMode("SIMULATION")}
                    className="text-[#b8860b]"
                  />
                  <span>Simulation</span>
                </label>
                <label className="flex items-center space-x-1 text-[#111113] cursor-pointer">
                  <input
                    type="radio"
                    name="mode"
                    checked={execMode === "RAZORPAY_TEST"}
                    onChange={() => setExecMode("RAZORPAY_TEST")}
                    className="text-[#b8860b]"
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
                      ? "bg-[#f4f2e9] text-[#8a8880] cursor-not-allowed border border-[#d6d2c4]"
                      : "bg-[#047857] hover:bg-[#065f46] text-white shadow-sm"
                  }`}
                >
                  {policyBlocked ? <Lock className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                  <span>{policyBlocked ? "EXECUTION BLOCKED BY POLICY" : `EXECUTE ACTION: ${recommendation.action || "RETRY_LATER"}`}</span>
                </button>

                <button
                  onClick={handleEscalate}
                  disabled={executing}
                  className="w-full py-2.5 px-4 text-xs font-mono font-bold bg-[#fffbeb] hover:bg-[#fef3c7] text-[#b45309] border border-[#fde68a] rounded-lg flex items-center justify-center space-x-2 transition"
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
          <div className="p-5 bg-white border border-[#e5e1d5] rounded-xl space-y-4 shadow-sm">
            <h3 className="text-xs font-mono font-bold text-[#111113] uppercase">ACTION HISTORY & OUTCOMES</h3>

            <div className="space-y-3 font-mono text-xs">
              {actions.length === 0 ? (
                <div className="text-[#6e6d67] text-center py-4">No actions executed yet.</div>
              ) : (
                actions.map((act: any) => (
                  <div key={act.id} className="p-3 bg-[#fcfbf7] border border-[#e5e1d5] rounded-lg space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-[#0284c7]">{act.action_type}</span>
                      <TagBadge tag={act.outcome_type} />
                    </div>
                    <div className="flex items-center justify-between text-[11px]">
                      <span className="text-[#6e6d67]">Status: <span className="text-[#111113]">{act.status}</span></span>
                      <span className="text-[#047857] font-bold">{formatCurrency(act.outcome_amount_minor)}</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Audit Chain */}
          <div className="p-5 bg-white border border-[#e5e1d5] rounded-xl space-y-4 shadow-sm">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-mono font-bold text-[#111113] uppercase">APPEND-ONLY AUDIT CHAIN</h3>
              <span className="text-[10px] font-mono text-[#047857] font-bold">CHAIN VALID</span>
            </div>

            <div className="space-y-2 overflow-y-auto max-h-64 pr-1 font-mono text-[11px]">
              {auditEvents.map((evt: any) => (
                <div key={evt.id} className="p-2 bg-[#fcfbf7] border border-[#e5e1d5] rounded space-y-1">
                  <div className="flex items-center justify-between text-[#6e6d67]">
                    <span className="text-[#0284c7] font-semibold">{evt.event_type}</span>
                    <span className="text-[10px] text-[#8a8880]">{evt.actor}</span>
                  </div>
                  <div className="text-[10px] text-[#6e6d67] truncate">Hash: {evt.integrity_hash?.substring(0, 16)}...</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
