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
    default: "Genora - AI DeFi Aggregator",
    template: "%s · Genora",
  },
  description: "AI-powered DeFi analytics and yield optimization platform with advanced market insights, risk analysis, and smart strategy recommendations.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="ru">
      <body className={inter.className}>
        <Navigation />
        <div className="main-content-with-sidebar">
          <main>{children}</main>
          <footer>
            <span>Данные поставляет DeFiLlama • Осторожно оценивайте риски</span>
          </footer>
        </div>
      </body>
    </html>
  );
}
