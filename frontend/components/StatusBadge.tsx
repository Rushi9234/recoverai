import React from "react";

interface StatusBadgeProps {
  status: string;
  type?: "state" | "priority" | "decision" | "action";
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, type = "state" }) => {
  const s = (status || "").toUpperCase();

  let badgeStyle = "bg-gray-100 text-gray-700 border-gray-200";

  // Decision & State Colors
  if (["ALLOW", "RECOVERED", "SUCCEEDED", "PASS", "CONSENTED"].includes(s)) {
    badgeStyle = "bg-emerald-50 text-emerald-800 border-emerald-200 font-semibold";
  } else if (["BLOCK", "BLOCKED", "FAIL", "FAILED", "REJECTED", "WITHDRAWN"].includes(s)) {
    badgeStyle = "bg-rose-50 text-rose-800 border-rose-200 font-semibold";
  } else if (["ESCALATE", "ESCALATED", "HIGH", "CRITICAL"].includes(s)) {
    badgeStyle = "bg-amber-50 text-amber-800 border-amber-200 font-semibold";
  } else if (["WAIT", "DELAYED", "MEDIUM"].includes(s)) {
    badgeStyle = "bg-slate-100 text-slate-700 border-slate-200 font-medium";
  } else if (["LOW", "NEW", "RISK_DETECTED", "POLICY_CHECK"].includes(s)) {
    badgeStyle = "bg-[#f4f2e9] text-[#55534e] border-[#e2dec9] font-medium";
  }

  return (
    <span className={`inline-flex items-center px-2 py-0.5 text-[10px] font-mono tracking-wider uppercase rounded border ${badgeStyle}`}>
      {s}
    </span>
  );
};
