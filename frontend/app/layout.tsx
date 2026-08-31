import React from "react";
import "./globals.css";
import { Navbar } from "@/components/Navbar";

export const metadata = {
  title: "RecoverAI — Merchant Revenue Recovery Control Plane",
  description: "Autonomous AI Revenue Recovery Control Plane for Razorpay Merchants",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="light">
      <body className="min-h-screen bg-[#f7f5ef] text-[#1a1a1f] antialiased flex">
        {/* Left Sidebar */}
        <Navbar />

        {/* Main Workspace Area */}
        <div className="flex-1 flex flex-col min-w-0">
          <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-8">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
