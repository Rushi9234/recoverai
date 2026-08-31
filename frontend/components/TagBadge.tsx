import React from "react";

interface TagBadgeProps {
  tag: "OBSERVED" | "SIMULATED" | "PROJECTED" | string;
  size?: "sm" | "md";
}

export const TagBadge: React.FC<TagBadgeProps> = ({ tag, size = "md" }) => {
  const t = (tag || "").toUpperCase();
  let badgeStyle = "bg-slate-100 text-slate-700 border-slate-300";

  if (t === "OBSERVED") {
    badgeStyle = "bg-emerald-50 text-emerald-800 border-emerald-300 font-semibold";
  } else if (t === "SIMULATED") {
    badgeStyle = "bg-purple-50 text-purple-800 border-purple-300 font-semibold";
  } else if (t === "PROJECTED") {
    badgeStyle = "bg-teal-50 text-teal-800 border-teal-300 font-semibold";
  }

  const px = size === "sm" ? "px-1.5 py-0.2 text-[9px]" : "px-2 py-0.5 text-[10px]";

  return (
    <span className={`inline-flex items-center ${px} tracking-wider uppercase font-mono rounded border ${badgeStyle}`}>
      {t}
    </span>
  );
};
