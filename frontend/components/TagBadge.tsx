import React from "react";

interface TagBadgeProps {
  tag: "OBSERVED" | "SIMULATED" | "PROJECTED" | string;
  size?: "sm" | "md";
}

export const TagBadge: React.FC<TagBadgeProps> = ({ tag, size = "md" }) => {
  const t = (tag || "").toUpperCase();
  let badgeStyle = "bg-slate-900 text-slate-300 border-slate-700";

  if (t === "OBSERVED") {
    badgeStyle = "bg-emerald-950/90 text-emerald-300 border-emerald-700/80 shadow-sm shadow-emerald-950/50";
  } else if (t === "SIMULATED") {
    badgeStyle = "bg-purple-950/90 text-purple-300 border-purple-700/80 shadow-sm shadow-purple-950/50";
  } else if (t === "PROJECTED") {
    badgeStyle = "bg-sky-950/90 text-sky-300 border-sky-700/80 shadow-sm shadow-sky-950/50";
  }

  const px = size === "sm" ? "px-1.5 py-0.2" : "px-2 py-0.5";
  const fontSize = size === "sm" ? "text-[9px]" : "text-[10px]";

  return (
    <span className={`inline-flex items-center ${px} ${fontSize} tracking-wider uppercase font-mono font-bold rounded border ${badgeStyle}`}>
      {t}
    </span>
  );
};
