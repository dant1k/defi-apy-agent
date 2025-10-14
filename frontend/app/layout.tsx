import "./globals.css";
import type { Metadata } from "next";
import Link from "next/link";
import type { ReactNode } from "react";
import { Inter } from "next/font/google";

const inter = Inter({
  subsets: ["latin", "cyrillic"],
  display: "swap",
  adjustFontFallback: false,
});

export const metadata: Metadata = {
  title: {
    default: "DeFi APY Agent",
    template: "%s · DeFi APY Agent",
  },
  description: "Подбор DeFi-стратегий и аналитика доходности с минимальной задержкой.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="ru">
      <body className={inter.className}>
        <div className="app-shell">
          <header>
            <h1>
              <Link href="/" prefetch>
                DeFi APY Agent
              </Link>
            </h1>
            <p>Найди лучшие стратегии доходности в пару кликов</p>
          </header>
          <main>{children}</main>
          <footer>
            <span>Данные поставляет DeFiLlama • Осторожно оценивайте риски</span>
          </footer>
        </div>
      </body>
    </html>
  );
}
