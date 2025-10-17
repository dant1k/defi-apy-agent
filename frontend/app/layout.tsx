import "./globals.css";
import type { Metadata } from "next";
import Link from "next/link";
import type { ReactNode } from "react";
import { Inter } from "next/font/google";
import { Navigation } from "../components/navigation";

const inter = Inter({
  subsets: ["latin", "cyrillic"],
  display: "swap",
  adjustFontFallback: false,
});

export const metadata: Metadata = {
  title: {
    default: "DeFi Analytics Dashboard | DeFi APY Agent",
    template: "%s · DeFi APY Agent",
  },
  description: "Professional DeFi analytics dashboard with AI-powered insights, risk analysis, and yield optimization tools.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="ru">
      <body className={inter.className}>
        <Navigation />
        <div className="app-shell">
          <main>{children}</main>
          <footer>
            <span>Данные поставляет DeFiLlama • Осторожно оценивайте риски</span>
          </footer>
        </div>
      </body>
    </html>
  );
}
