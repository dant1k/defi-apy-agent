"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

type RiskLevel = "низкий" | "средний" | "высокий";

type Strategy = {
  platform?: string;
  chain?: string;
  symbol?: string;
  apy?: number;
  risk_level?: RiskLevel;
  risk_description?: string;
  lockup_days?: number;
  tvl_usd?: number;
  score?: number;
  pool_url?: string | null;
  protocol_url?: string | null;
  action_url?: string | null;
};

type OkResponse = {
  status: "ok";
  token: string;
  best_strategy: Strategy;
  alternatives: Strategy[];
  statistics?: { matched?: number; considered?: number };
  warnings?: string[];
};

type EmptyResponse = {
  status: "empty";
  token?: string;
  warnings?: string[];
};

type ErrorResponse = {
  status: "error";
  message: string;
  warnings?: string[];
};

type ApiResponse = OkResponse | EmptyResponse | ErrorResponse;

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

const riskOptions: { label: string; value: RiskLevel }[] = [
  { label: "Низкий", value: "низкий" },
  { label: "Средний", value: "средний" },
  { label: "Высокий", value: "высокий" },
];

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

type TokenOption = {
  value: string;
  label: string;
  slug?: string;
};

const FALLBACK_TOKENS: TokenOption[] = [
  { value: "USDT", label: "USDT" },
  { value: "USDC", label: "USDC" },
  { value: "ETH", label: "ETH" },
  { value: "APT", label: "APT" },
  { value: "SUI", label: "SUI" },
];

const DEFAULT_FORM = {
  token: "ETH",
  riskLevel: "средний" as RiskLevel,
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ?? "http://localhost:8000";

export default function HomePage(): JSX.Element {
  const [form, setForm] = useState(DEFAULT_FORM);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<ApiResponse | null>(null);
  const [activeView, setActiveView] = useState<"strategies" | "analytics">("strategies");
  const [isTokenModalOpen, setTokenModalOpen] = useState(false);
  const [tokenOptions, setTokenOptions] = useState<TokenOption[]>(FALLBACK_TOKENS);
  const [tokenQuery, setTokenQuery] = useState("");
  const [analyticsTokenSearch, setAnalyticsTokenSearch] = useState("");
  const [analyticsChainSearch, setAnalyticsChainSearch] = useState("");
  const [isAnalyticsChainModalOpen, setAnalyticsChainModalOpen] = useState(false);
  const [analyticsPeriod, setAnalyticsPeriod] = useState("7d");
  const [analyticsSort, setAnalyticsSort] = useState<"tvl_change" | "apy_change">("tvl_change");
  const [analyticsChains, setAnalyticsChains] = useState<string[]>([]);
  const [analyticsTokens, setAnalyticsTokens] = useState<string[]>([]);
  const [isSymbolModalOpen, setSymbolModalOpen] = useState(false);
  const [analyticsData, setAnalyticsData] = useState<AnalyticsResponse | null>(null);
  const [analyticsError, setAnalyticsError] = useState<string | null>(null);
  const [isAnalyticsLoading, setAnalyticsLoading] = useState(false);

  const filteredTokens = useMemo(() => {
    if (!tokenQuery.trim()) {
      return tokenOptions;
    }
    const q = tokenQuery.trim().toLowerCase();
    return tokenOptions.filter(
      (token) =>
        token.value.toLowerCase().includes(q) ||
        token.label.toLowerCase().includes(q) ||
        (token.slug ?? "").toLowerCase().includes(q),
    );
  }, [tokenOptions, tokenQuery]);

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

  useEffect(() => {
    let cancelled = false;
    async function fetchTokens() {
      try {
        const res = await fetch(`${API_BASE_URL}/tokens`);
        if (!res.ok) {
          throw new Error("failed to fetch");
        }
        const data = (await res.json()) as { tokens: { symbol: string; name: string; slug?: string }[] };
        if (cancelled) return;
        if (Array.isArray(data.tokens) && data.tokens.length > 0) {
          const next = data.tokens
            .map((item) => ({
              value: item.symbol.toUpperCase(),
              label: `${item.symbol.toUpperCase()} · ${item.name}`,
              slug: item.slug,
            }))
            .slice(0, 100);
          setTokenOptions(next);
        }
      } catch (fetchError) {
        console.warn("Failed to fetch token list, using fallback", fetchError);
        if (!cancelled) {
          setTokenOptions(FALLBACK_TOKENS);
        }
      }
    }
    fetchTokens();
    return () => {
      cancelled = true;
    };
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsLoading(true);
    setError(null);
    setResponse(null);

    try {
      const payload = {
        token: form.token,
        preferences: {
          risk_level: form.riskLevel,
          min_tvl: 1_000_000,
        },
      };

      const res = await fetch(`${API_BASE_URL}/strategies`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const detail = await res.json().catch(() => null);
        throw new Error(detail?.detail ?? "Сервер вернул ошибку");
      }

      const data: ApiResponse = await res.json();
      setResponse(data);
    } catch (fetchError: unknown) {
      const message =
        fetchError instanceof Error ? fetchError.message : "Не удалось выполнить запрос";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }

  const sortOptions: { label: string; value: "tvl_change" | "apy_change" }[] = [
    { label: "Рост TVL", value: "tvl_change" },
    { label: "Рост APY", value: "apy_change" },
  ];

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

      const res = await fetch(`${API_BASE_URL}/analytics/new-pools?${params.toString()}`);
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
    <section className="page">
      <div className="view-switcher">
        <button
          type="button"
          className={activeView === "strategies" ? "active" : ""}
          onClick={() => setActiveView("strategies")}
        >
          Поиск стратегий
        </button>
        <button
          type="button"
          className={activeView === "analytics" ? "active" : ""}
          onClick={() => setActiveView("analytics")}
        >
          Новые пулы
        </button>
      </div>

      {activeView === "strategies" && (
        <form className="form" onSubmit={handleSubmit}>
        <div className="grid-row">
          <div className="form-row">
            <label>Токен</label>
            <div className="multi-select single">
              <button
                type="button"
                className="multiselect-trigger"
                onClick={() => setTokenModalOpen(true)}
              >
                {form.token || "Выбрать токен"}
              </button>
            </div>
          </div>
          <div className="form-row">
            <label htmlFor="riskLevel">Уровень риска</label>
            <select
              id="riskLevel"
              value={form.riskLevel}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, riskLevel: e.target.value as RiskLevel }))
              }
            >
              {riskOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <button className="submit" type="submit" disabled={isLoading || !form.token}>
          {isLoading ? "Ищем стратегии..." : "Найти стратегии"}
        </button>
      </form>
      )}

      {activeView === "strategies" && error && <div className="error-card">⚠️ {error}</div>}

      {activeView === "strategies" && response && <ResultsCard response={response} />}

      {activeView === "analytics" && (
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
              onChange={(event) =>
                setAnalyticsSort(event.target.value as "tvl_change" | "apy_change")
              }
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
        </div>

        <div className="analytics-actions">
          <button
            type="button"
            onClick={() => loadAnalytics()}
            disabled={isAnalyticsLoading || analyticsTokens.length === 0}
          >
            {isAnalyticsLoading ? "Загружаем..." : "Показать новые пулы"}
          </button>
          <button
            type="button"
            className="secondary"
            onClick={() => loadAnalytics("tvl_change")}
            disabled={isAnalyticsLoading || analyticsTokens.length === 0}
          >
            🔥 Новые трендовые
          </button>
          <button
            type="button"
            className="outlined"
            onClick={exportAnalyticsAsCsv}
            disabled={!analyticsData || analyticsData.pools.length === 0}
          >
            Экспорт CSV
          </button>
        </div>

        {analyticsError && <div className="error-card">⚠️ {analyticsError}</div>}

        {analyticsData && analyticsData.pools.length > 0 && (
          <div className="analytics-table-wrapper">
            <table className="analytics-table">
              <thead>
                <tr>
                  <th>Пул</th>
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
      </div>
      )}

      <SingleSelectionModal
        title="Выбор токена"
        isOpen={isTokenModalOpen}
        options={filteredTokens}
        selected={form.token}
        query={tokenQuery}
        onQueryChange={setTokenQuery}
        onSelect={(value) => {
          setForm((prev) => ({ ...prev, token: value }));
          setTokenModalOpen(false);
        }}
        onClose={() => setTokenModalOpen(false)}
        isLoading={!tokenOptions.length}
      />

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

    </section>
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

type SelectionModalProps = {
  title: string;
  isOpen: boolean;
  options: { value: string; label: string }[];
  selected: string[];
  query: string;
  onQueryChange: (value: string) => void;
  onToggle: (value: string) => void;
  onClose: () => void;
  onClear?: () => void;
};

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
}: SelectionModalProps) {
  if (!isOpen) {
    return null;
  }

  return (
    <div className="modal-backdrop" role="dialog" aria-modal="true">
      <div className="modal">
        <header>
          <h3>{title}</h3>
          <button type="button" onClick={onClose} className="close-button" aria-label="Закрыть">
            ×
          </button>
        </header>
        <div className="modal-search">
          <input
            type="text"
            placeholder="Поиск по символу или названию"
            value={query}
            onChange={(event) => onQueryChange(event.target.value)}
          />
        </div>
        <div className="options">
          {options.map((option) => {
            const isSelected = selected.includes(option.value);
            return (
              <label key={option.value} className={`option ${isSelected ? "selected" : ""}`}>
                <input
                  type="checkbox"
                  checked={isSelected}
                  onChange={() => onToggle(option.value)}
                />
                <span>{option.label}</span>
              </label>
            );
          })}
          {options.length === 0 && <span className="hint">Ничего не найдено</span>}
        </div>
        <footer>
          {onClear && (
            <button type="button" className="outlined" onClick={onClear}>
              Сбросить
            </button>
          )}
          <button type="button" onClick={onClose}>
            Готово
          </button>
        </footer>
      </div>
    </div>
  );
}

type SingleSelectionModalProps = {
  title: string;
  isOpen: boolean;
  options: TokenOption[];
  selected: string;
  query: string;
  onQueryChange: (value: string) => void;
  onSelect: (value: string) => void;
  onClose: () => void;
  isLoading?: boolean;
};

function SingleSelectionModal({
  title,
  isOpen,
  options,
  selected,
  query,
  onQueryChange,
  onSelect,
  onClose,
  isLoading = false,
}: SingleSelectionModalProps) {
  if (!isOpen) {
    return null;
  }

  return (
    <div className="modal-backdrop" role="dialog" aria-modal="true">
      <div className="modal">
        <header>
          <h3>{title}</h3>
          <button type="button" onClick={onClose} className="close-button" aria-label="Закрыть">
            ×
          </button>
        </header>
        <div className="modal-search">
          <input
            type="text"
            placeholder="Поиск по символу или названию"
            value={query}
            onChange={(event) => onQueryChange(event.target.value)}
          />
        </div>
        <div className="options">
          {isLoading && <span className="hint">Загружаем список токенов...</span>}
          {!isLoading &&
            options.map((option) => {
              const isSelected = selected === option.value;
              return (
                <label key={option.value} className={`option ${isSelected ? "selected" : ""}`}>
                  <input
                    type="radio"
                    name="token-select"
                    checked={isSelected}
                    onChange={() => onSelect(option.value)}
                  />
                  <span>{option.label}</span>
                </label>
              );
            })}
          {!isLoading && options.length === 0 && (
            <span className="hint">Ничего не найдено — попробуй другой поиск.</span>
          )}
        </div>
        <footer>
          <button type="button" onClick={onClose}>
            Готово
          </button>
        </footer>
      </div>
    </div>
  );
}

function formatLabel(value: string): string {
  if (!value) {
    return value;
  }
  return value
    .split(/[-_\s]/)
    .map((chunk) => chunk.charAt(0).toUpperCase() + chunk.slice(1))
    .join(" ");
}

function formatNumber(value?: number, fractionDigits = 2): string {
  if (value === undefined || value === null || Number.isNaN(value)) {
    return "-";
  }
  return value.toLocaleString("ru-RU", {
    maximumFractionDigits: fractionDigits,
  });
}

function formatPercent(value?: number | null, fractionDigits = 2): string {
  if (value === undefined || value === null || Number.isNaN(value)) {
    return "-";
  }
  return `${value.toFixed(fractionDigits)}%`;
}

function formatLockup(days?: number): string {
  if (days === undefined || days === null) {
    return "-";
  }
  if (days === 0) {
    return "нет";
  }
  if (days % 30 === 0) {
    return `${days / 30} мес.`;
  }
  if (days % 7 === 0) {
    return `${days / 7} нед.`;
  }
  return `${days} дней`;
}

function ResultsCard({ response }: { response: ApiResponse }) {
  if (response.status === "error") {
    return (
      <div className="error-card">
        <strong>Ошибка:</strong> {response.message}
      </div>
    );
  }

  if (response.status === "empty") {
    return (
      <div className="result-card">
        <h3>Стратегии не найдены</h3>
        {response.warnings?.length ? (
          <ul className="warnings">
            {response.warnings.map((warning) => (
              <li key={warning}>{warning}</li>
            ))}
          </ul>
        ) : (
          <p>Попробуй ослабить фильтры или изменить токен.</p>
        )}
      </div>
    );
  }

  const { best_strategy, alternatives, statistics, warnings } = response;

  return (
    <div className="result-card">
      <h3>Лучшая стратегия для {response.token}</h3>
      <StrategyBlock strategy={best_strategy} isBest />

      {alternatives.length > 0 && (
        <div className="alternatives">
          <h4>Другие варианты</h4>
          <div className="alternative-grid">
            {alternatives.map((item, index) => (
              <StrategyBlock key={`${item.platform}-${index}`} strategy={item} />
            ))}
          </div>
        </div>
      )}

      {statistics && (
        <p className="stats">
          Подобрано {statistics.matched ?? 0} стратегий из {statistics.considered ?? 0} найденных.
        </p>
      )}

      {warnings && warnings.length > 0 && (
        <ul className="warnings">
          {warnings.map((warning) => (
            <li key={warning}>{warning}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

function StrategyBlock({ strategy, isBest = false }: { strategy: Strategy; isBest?: boolean }) {
  const title = strategy.platform ?? strategy.symbol ?? "Неизвестный протокол";
  const link = strategy.action_url ?? strategy.protocol_url ?? strategy.pool_url ?? undefined;

  return (
    <article className={`strategy ${isBest ? "best" : ""}`}>
      <header>
        {link ? (
          <a href={link} target="_blank" rel="noopener noreferrer">
            {title}
          </a>
        ) : (
          <strong>{title}</strong>
        )}
        {strategy.chain && <span className="chain-tag">{formatLabel(strategy.chain)}</span>}
      </header>
      <dl>
        <div>
          <dt>Тикер</dt>
          <dd>{strategy.symbol ?? "-"}</dd>
        </div>
        <div>
          <dt>APY</dt>
          <dd>{strategy.apy !== undefined ? `${formatNumber(strategy.apy)}%` : "-"}</dd>
        </div>
        <div>
          <dt>Риск</dt>
          <dd>
            {strategy.risk_level ? strategy.risk_level.toUpperCase() : "-"}
            {strategy.risk_description && <span className="sub">{strategy.risk_description}</span>}
          </dd>
        </div>
        <div>
          <dt>Локап</dt>
          <dd>{formatLockup(strategy.lockup_days)}</dd>
        </div>
        <div>
          <dt>TVL</dt>
          <dd>{strategy.tvl_usd ? `${formatNumber(strategy.tvl_usd, 0)} $` : "-"}</dd>
        </div>
        {strategy.score !== undefined && (
          <div>
            <dt>Score</dt>
            <dd>{formatNumber(strategy.score)}</dd>
          </div>
        )}
      </dl>
    </article>
  );
}
