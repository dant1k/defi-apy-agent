"use client";

import "./globals.css";
import type { ReactNode } from "react";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="ru">
      <body>
        <div className="app-shell">
          <header>
            <h1>DeFi APY Agent</h1>
            <p>Найди лучшие стратегии доходности в пара кликов</p>
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
