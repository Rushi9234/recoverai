import React from "react";
import "./globals.css";
import { Navbar } from "@/components/Navbar";

export const metadata = {
  title: "RecoverAI — Merchant Revenue Recovery Control Plane",
  description: "AI Revenue Recovery Agent for Razorpay Merchants",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-[#090d16] text-gray-100 antialiased selection:bg-blue-600 selection:text-white">
        <Navbar />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
      </body>
    </html>
  );
}
