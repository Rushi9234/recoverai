"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { ShieldCheck, LayoutDashboard, ListOrdered, GitMerge, Sliders, Activity, UserCheck, Play } from "lucide-react";

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
    <nav className="border-b border-gray-800 bg-[#0d1322] sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-lg shadow-blue-600/30">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <span className="text-lg font-bold text-white tracking-tight">Recover<span className="text-blue-500">AI</span></span>
              <span className="ml-2 px-1.5 py-0.5 text-[10px] font-mono font-bold bg-blue-950 text-blue-400 border border-blue-800 rounded">
                CONTROL PLANE
              </span>
            </div>
          </div>

          <div className="flex items-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`flex items-center space-x-1.5 px-3 py-2 rounded-md text-xs font-medium transition-colors ${
                    isActive
                      ? "bg-blue-900/50 text-blue-400 border border-blue-700/60 font-semibold"
                      : "text-gray-400 hover:text-gray-200 hover:bg-gray-800/60"
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </div>

          <div className="flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span className="text-xs font-mono text-gray-400">TEST MODE</span>
          </div>
        </div>
      </div>
    </nav>
  );
};
