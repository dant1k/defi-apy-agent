"use client";

import { ReactNode } from "react";

interface TerminalLayoutProps {
  children: ReactNode;
}

export default function TerminalLayout({ children }: TerminalLayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50">
      <aside className="fixed left-0 top-0 h-full w-64 bg-gray-900 text-white p-4">
        <h1 className="text-2xl font-bold mb-6">Genora Terminal</h1>
        <nav className="space-y-2">
          <a
            href="/terminal/aptos/dex"
            className="block px-4 py-2 rounded hover:bg-gray-800"
          >
            Aptos DEXes
          </a>
        </nav>
      </aside>
      <main className="ml-64">{children}</main>
    </div>
  );
}

