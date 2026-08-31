"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { ShieldCheck, LayoutDashboard, ListOrdered, Play, UserCheck, Activity, Sliders, Zap, CheckCircle2 } from "lucide-react";

export const Navbar: React.FC = () => {
  const pathname = usePathname();

  const navItems = [
    { name: "Dashboard", href: "/", icon: LayoutDashboard },
    { name: "Risk Queue", href: "/cases", icon: ListOrdered },
    { name: "Simulator", href: "/simulator", icon: Play },
    { name: "Contact Guard", href: "/contacts", icon: UserCheck },
    { name: "Audit Trail", href: "/audit", icon: Activity },
    { name: "Settings", href: "/settings", icon: Sliders },
  ];

  return (
    <aside className="w-64 bg-[#0c0d11] text-gray-300 flex flex-col justify-between min-h-screen border-r border-[#1a1c23] shrink-0 sticky top-0 h-screen z-50">
      <div className="p-5 space-y-6">
        {/* Brand & Product Identity */}
        <div className="flex items-center space-x-3 pb-4 border-b border-[#1f212a]">
          <div className="w-9 h-9 rounded-lg bg-[#b8860b] flex items-center justify-center text-white shadow-md shadow-amber-900/30 shrink-0">
            <ShieldCheck className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-1.5">
              <span className="text-base font-bold text-white tracking-tight font-serif">Recover<span className="text-[#d97706]">AI</span></span>
              <span className="px-1.5 py-0.5 text-[9px] font-mono font-bold bg-[#261f10] text-[#f59e0b] border border-[#78350f] rounded">
                v1.0
              </span>
            </div>
            <p className="text-[10px] text-gray-400 font-mono">Razorpay Revenue Control</p>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex items-center space-x-3 px-3 py-2.5 rounded-md text-xs font-medium transition-all ${
                  isActive
                    ? "bg-[#181a22] text-white border-l-2 border-[#d97706] font-semibold shadow-sm"
                    : "text-gray-400 hover:text-gray-200 hover:bg-[#14151c]"
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? "text-[#d97706]" : "text-gray-400"}`} />
                <span>{item.name}</span>
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Footer Environment Status Badge */}
      <div className="p-4 border-t border-[#1a1c23] bg-[#090a0d]">
        <div className="p-2.5 bg-[#12141c] border border-[#212433] rounded-lg space-y-1.5">
          <div className="flex items-center space-x-2 font-mono text-[10px] text-emerald-400">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span className="font-bold tracking-wider">TEST MODE · SIMULATION</span>
          </div>
          <p className="text-[10px] text-gray-400 font-mono leading-tight">Razorpay Test Mode Active</p>
        </div>
      </div>
    </aside>
  );
};
