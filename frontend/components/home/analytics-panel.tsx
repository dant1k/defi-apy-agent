'use client';

import { useMemo, useState } from "react";
import { formatLabel, formatNumber, formatPercent } from "./formatters";
import type { TokenOption } from "./types";

type AnalyticsPool = {
  pool_id: string;
  pair: string;
  protocol?: string;
  chain?: string;
  tvl_usd: number;
  apy: number;
  tvl_change_pct?: number | null;
  apy_change_pct?: number | null;
  momentum?: number | null;
  category?: string;
  first_seen?: string | null;
  action_url?: string | null;
};

type AnalyticsResponse = {
  period: string;
  days: number;
  min_tvl: number;
  filters: { symbols: string[]; chains: string[] };
  count: number;
  pools: AnalyticsPool[];
};

const chainOptions = [
  { value: "ethereum", label: "Ethereum" },
  { value: "arbitrum", label: "Arbitrum" },
  { value: "optimism", label: "Optimism" },
  { value: "polygon", label: "Polygon" },
  { value: "base", label: "Base" },
  { value: "bsc", label: "BNB Chain" },
  { value: "solana", label: "Solana" },
  { value: "avalanche", label: "Avalanche" },
  { value: "aptos", label: "Aptos" },
  { value: "sui", label: "Sui" },
  { value: "gnosis", label: "Gnosis" },
  { value: "fantom", label: "Fantom" },
];

const sortOptions: { label: string; value: "tvl_change" | "apy_change" }[] = [
  { label: "Рост TVL", value: "tvl_change" },
  { label: "Рост APY", value: "apy_change" },
];

type AnalyticsPanelProps = {
  tokenOptions: TokenOption[];
  apiBaseUrl: string;
};

export default function AnalyticsPanel({
  tokenOptions,
  apiBaseUrl,
}: AnalyticsPanelProps): JSX.Element {
  const [analyticsPeriod, setAnalyticsPeriod] = useState("7d");
  const [analyticsSort, setAnalyticsSort] = useState<"tvl_change" | "apy_change">("tvl_change");
  const [analyticsChains, setAnalyticsChains] = useState<string[]>([]);
  const [analyticsTokens, setAnalyticsTokens] = useState<string[]>([]);
  const [analyticsTokenSearch, setAnalyticsTokenSearch] = useState("");
  const [analyticsChainSearch, setAnalyticsChainSearch] = useState("");
  const [isAnalyticsChainModalOpen, setAnalyticsChainModalOpen] = useState(false);
  const [isSymbolModalOpen, setSymbolModalOpen] = useState(false);
  const [analyticsData, setAnalyticsData] = useState<AnalyticsResponse | null>(null);
  const [analyticsError, setAnalyticsError] = useState<string | null>(null);
  const [isAnalyticsLoading, setAnalyticsLoading] = useState(false);

  const filteredAnalyticsTokens = useMemo(() => {
    if (!analyticsTokenSearch.trim()) {
      return tokenOptions;
    }
    const q = analyticsTokenSearch.trim().toLowerCase();
    return tokenOptions.filter(
      (token) =>
        token.value.toLowerCase().includes(q) ||
        token.label.toLowerCase().includes(q) ||
        (token.slug ?? "").toLowerCase().includes(q),
    );
  }, [tokenOptions, analyticsTokenSearch]);

  const filteredAnalyticsChains = useMemo(() => {
    if (!analyticsChainSearch.trim()) {
      return chainOptions;
    }
    const q = analyticsChainSearch.trim().toLowerCase();
    return chainOptions.filter((chain) => chain.label.toLowerCase().includes(q));
  }, [analyticsChainSearch]);

  async function loadAnalytics(customSort?: "tvl_change" | "apy_change") {
    if (analyticsTokens.length === 0) {
      setAnalyticsError("Выберите хотя бы один тикер из топ-100");
      return;
    }
    setAnalyticsLoading(true);
    setAnalyticsError(null);
    try {
      const sortValue = customSort ?? analyticsSort;

      const params = new URLSearchParams({
        period: analyticsPeriod,
        min_tvl: String(1_000_000),
        sort: sortValue,
        limit: "30",
      });
      analyticsTokens.forEach((token) => params.append("symbols", token));
      analyticsChains.forEach((chain) => params.append("chains", chain));

      const res = await fetch(`${apiBaseUrl}/analytics/new-pools?${params.toString()}`);
      if (!res.ok) {
        const detail = await res.json().catch(() => null);
        throw new Error(detail?.detail ?? "Сервер вернул ошибку");
      }
      const data = (await res.json()) as AnalyticsResponse;
      setAnalyticsData(data);
      setAnalyticsSort(sortValue);
    } catch (fetchError) {
      const message = fetchError instanceof Error ? fetchError.message : "Не удалось загрузить аналитику";
      setAnalyticsError(message);
    } finally {
      setAnalyticsLoading(false);
    }
  }

  function exportAnalyticsAsCsv() {
    if (!analyticsData || analyticsData.pools.length === 0) {
      return;
    }
    const headers = [
      "Pair",
      "Protocol",
      "Chain",
      "TVL (USD)",
      "TVL Change %",
      "APY",
      "APY Change %",
      "Momentum",
      "Category",
      "First Seen",
      "URL",
    ];
    const rows = analyticsData.pools.map((pool) => [
      pool.pair,
      pool.protocol ?? "",
      pool.chain ?? "",
      String(pool.tvl_usd ?? ""),
      pool.tvl_change_pct != null ? pool.tvl_change_pct.toString() : "",
      String(pool.apy ?? ""),
      pool.apy_change_pct != null ? pool.apy_change_pct.toString() : "",
      pool.momentum != null ? pool.momentum.toString() : "",
      pool.category ?? "",
      pool.first_seen ?? "",
      pool.action_url ?? "",
    ]);
    const csv = [headers, ...rows]
      .map((line) => line.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(","))
      .join("\n");

    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `new-pools-${analyticsPeriod}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="analytics-panel">
      <header className="analytics-header">
        <h2>Новые DeFi пулы</h2>
        <span>Следи за свежими возможностями по росту TVL и APY</span>
      </header>

      <div className="analytics-filters">
        <div className="form-row">
          <label htmlFor="analyticsPeriod">Период</label>
          <select
            id="analyticsPeriod"
            value={analyticsPeriod}
            onChange={(event) => setAnalyticsPeriod(event.target.value)}
          >
            <option value="24h">24 часа</option>
            <option value="7d">7 дней</option>
            <option value="30d">30 дней</option>
          </select>
        </div>
        <div className="form-row">
          <label htmlFor="analyticsSort">Сортировка</label>
          <select
            id="analyticsSort"
            value={analyticsSort}
            onChange={(event) => setAnalyticsSort(event.target.value as "tvl_change" | "apy_change")}
          >
            {sortOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
        <div className="form-row">
          <label>Сети</label>
          <div className="multi-select">
            <button
              type="button"
              className="multiselect-trigger"
              onClick={() => {
                setAnalyticsChainSearch("");
                setAnalyticsChainModalOpen(true);
              }}
            >
              {analyticsChains.length ? `Выбрано: ${analyticsChains.length}` : "Выбрать сети"}
            </button>
            <ChipGroup
              items={analyticsChains}
              onRemove={(value) =>
                setAnalyticsChains((prev) => prev.filter((item) => item !== value))
              }
            />
          </div>
        </div>
        <div className="form-row">
          <label>Тикеры</label>
          <div className="multi-select">
            <button
              type="button"
              className="multiselect-trigger"
              onClick={() => {
                setAnalyticsTokenSearch("");
                setSymbolModalOpen(true);
              }}
            >
              {analyticsTokens.length ? `Выбрано: ${analyticsTokens.length}` : "Выбрать тикеры"}
            </button>
            <ChipGroup
              items={analyticsTokens}
              onRemove={(value) =>
                setAnalyticsTokens((prev) => prev.filter((item) => item !== value))
              }
            />
          </div>
        </div>
        <div className="analytics-actions">
          <button type="button" className="submit secondary" onClick={() => loadAnalytics()}>
            {isAnalyticsLoading ? "Загружаем..." : "Показать"}
          </button>
          <button
            type="button"
            className="submit ghost"
            onClick={() => loadAnalytics(analyticsSort === "tvl_change" ? "apy_change" : "tvl_change")}
          >
            Сменить сортировку
          </button>
          <button type="button" className="submit ghost" onClick={exportAnalyticsAsCsv}>
            Экспорт CSV
          </button>
        </div>
      </div>

      {analyticsError && <div className="error-card">⚠️ {analyticsError}</div>}

      {analyticsData && analyticsData.pools.length > 0 && (
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Пара</th>
                <th>Протокол</th>
                <th>Сеть</th>
                <th>TVL</th>
                <th>Δ TVL</th>
                <th>APY</th>
                <th>Δ APY</th>
                <th>Momentum</th>
                <th>Категория</th>
                <th>Дата</th>
                <th>Ссылка</th>
              </tr>
            </thead>
            <tbody>
              {analyticsData.pools.map((pool) => (
                <tr key={pool.pool_id}>
                  <td>{pool.pair}</td>
                  <td>{pool.protocol ?? "-"}</td>
                  <td>{pool.chain ?? "-"}</td>
                  <td>{formatNumber(pool.tvl_usd, 0)} $</td>
                  <td>{formatPercent(pool.tvl_change_pct)}</td>
                  <td>{formatNumber(pool.apy)}%</td>
                  <td>{formatPercent(pool.apy_change_pct)}</td>
                  <td>{formatNumber(pool.momentum ?? undefined, 2)}</td>
                  <td>{pool.category ?? "-"}</td>
                  <td>{pool.first_seen ? new Date(pool.first_seen).toLocaleString() : "-"}</td>
                  <td>
                    {pool.action_url ? (
                      <a href={pool.action_url} target="_blank" rel="noopener noreferrer">
                        Перейти
                      </a>
                    ) : (
                      "-"
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {analyticsData && analyticsData.pools.length === 0 && !analyticsError && (
        <div className="empty-state">Пулы не найдены по заданным фильтрам.</div>
      )}

      <SelectionModal
        title="Выбор тикеров для аналитики"
        isOpen={isSymbolModalOpen}
        options={filteredAnalyticsTokens}
        selected={analyticsTokens}
        query={analyticsTokenSearch}
        onQueryChange={setAnalyticsTokenSearch}
        onToggle={(value) =>
          setAnalyticsTokens((prev) =>
            prev.includes(value) ? prev.filter((item) => item !== value) : [...prev, value],
          )
        }
        onClose={() => setSymbolModalOpen(false)}
        onClear={() => setAnalyticsTokens([])}
      />

      <SelectionModal
        title="Сети для аналитики"
        isOpen={isAnalyticsChainModalOpen}
        options={filteredAnalyticsChains}
        selected={analyticsChains}
        query={analyticsChainSearch}
        onQueryChange={setAnalyticsChainSearch}
        onToggle={(value) =>
          setAnalyticsChains((prev) =>
            prev.includes(value) ? prev.filter((item) => item !== value) : [...prev, value],
          )
        }
        onClose={() => setAnalyticsChainModalOpen(false)}
        onClear={() => setAnalyticsChains([])}
      />
    </div>
  );
}

function ChipGroup({
  items,
  onRemove,
}: {
  items: string[];
  onRemove: (value: string) => void;
}) {
  if (!items.length) {
    return null;
  }

  return (
    <div className="chip-group">
      {items.map((item) => (
        <span key={item} className="chip">
          {formatLabel(item)}
          <button type="button" onClick={() => onRemove(item)} aria-label="Удалить значение">
            ×
          </button>
        </span>
      ))}
    </div>
  );
}

function SelectionModal({
  title,
  isOpen,
  options,
  selected,
  query,
  onQueryChange,
  onToggle,
  onClose,
  onClear,
}: {
  title: string;
  isOpen: boolean;
  options: { value: string; label: string }[];
  selected: string[];
  query: string;
  onQueryChange: (value: string) => void;
  onToggle: (value: string) => void;
  onClose: () => void;
  onClear: () => void;
}) {
  if (!isOpen) {
    return null;
  }

  return (
    <div className="modal-backdrop" role="dialog" aria-modal="true">
      <div className="modal large">
        <header className="modal-header">
          <h3>{title}</h3>
          <div className="modal-actions">
            <button type="button" onClick={onClear}>
              Очистить
            </button>
            <button type="button" onClick={onClose} aria-label="Закрыть">
              ×
            </button>
          </div>
        </header>
        <div className="modal-search">
          <input
            type="search"
            placeholder="Поиск"
            value={query}
            onChange={(event) => onQueryChange(event.target.value)}
          />
        </div>
        <div className="modal-content">
          <ul>
            {options.map((option) => (
              <li key={option.value}>
                <button
                  type="button"
                  className={selected.includes(option.value) ? "selected" : ""}
                  onClick={() => onToggle(option.value)}
                >
                  <span>{option.label}</span>
                  {selected.includes(option.value) && <span className="badge">✓</span>}
                </button>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
