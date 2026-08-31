import React from "react";

interface TagBadgeProps {
  tag: "OBSERVED" | "SIMULATED" | "PROJECTED" | string;
}

export const TagBadge: React.FC<TagBadgeProps> = ({ tag }) => {
  const t = (tag || "").toUpperCase();
  let badgeStyle = "bg-slate-800 text-slate-300 border-slate-700";

  if (t === "OBSERVED") {
    badgeStyle = "bg-emerald-950 text-emerald-300 border-emerald-700 shadow-sm shadow-emerald-900/50";
  } else if (t === "SIMULATED") {
    badgeStyle = "bg-purple-950 text-purple-300 border-purple-700 shadow-sm shadow-purple-900/50";
  } else if (t === "PROJECTED") {
    badgeStyle = "bg-sky-950 text-sky-300 border-sky-700 shadow-sm shadow-sky-900/50";
  }

  return (
    <span className={`px-2 py-0.5 text-[10px] tracking-wider uppercase font-mono font-bold rounded border ${badgeStyle}`}>
      {t}
    </span>
  );
};
