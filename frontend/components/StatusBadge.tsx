import React from "react";

interface StatusBadgeProps {
  status: string;
  type?: "state" | "priority" | "decision" | "outcome";
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, type = "state" }) => {
  const s = (status || "").toUpperCase();
  let color = "bg-gray-800 text-gray-300 border-gray-700";

  if (s === "CRITICAL" || s === "FAILED" || s === "BLOCKED" || s === "BLOCK") {
    color = "bg-red-950/70 text-red-400 border-red-800";
  } else if (s === "HIGH" || s === "ESCALATED" || s === "ESCALATE") {
    color = "bg-amber-950/70 text-amber-400 border-amber-800";
  } else if (s === "MEDIUM" || s === "WAIT" || s === "WAITING" || s === "POLICY_CHECK") {
    color = "bg-yellow-950/70 text-yellow-400 border-yellow-800";
  } else if (s === "LOW" || s === "RECOVERED" || s === "SUCCEEDED" || s === "ALLOW" || s === "APPROVED") {
    color = "bg-emerald-950/70 text-emerald-400 border-emerald-800";
  } else if (s === "NEW" || s === "INGESTED" || s === "RISK_DETECTED" || s === "DIAGNOSED" || s === "EXECUTING") {
    color = "bg-blue-950/70 text-blue-400 border-blue-800";
  }

  return (
    <span className={`px-2.5 py-0.5 text-xs font-mono font-semibold rounded-full border ${color}`}>
      {s}
    </span>
  );
};
