import { FormEvent, useEffect, useMemo, useRef, useState, useTransition } from "react";
import dynamic from "next/dynamic";
import { ApiResponse, RiskLevel, Strategy, StrategyCacheEntry, TokenOption } from "./types";
import { formatLabel, formatNumber, formatPercent } from "./formatters";
import { fetchStrategies } from "../../lib/api";
import { useStrategyFilters, SortOption, GrowthFilter } from "../../store/useStrategyFilters";
import { useShallow } from "zustand/react/shallow";

const LoadingGenie = dynamic(() => import("./loading-genie").then((mod) => mod.LoadingGenie), {
  ssr: false,
});
const StrategiesSkeleton = dynamic(
  () => import("./home-skeleton").then((mod) => mod.StrategiesSkeleton),
  { ssr: false },
);

const riskOptions: { label: string; value: RiskLevel }[] = [
  { label: "Низкий", value: "низкий" },
  { label: "Средний", value: "средний" },
  { label: "Высокий", value: "высокий" },
];

const sortOptions: { value: SortOption; label: string }[] = [
  { value: "apy", label: "APY" },
  { value: "tvl", label: "TVL" },
  { value: "novelty", label: "Новизне" },
];

const CACHE_TTL_MS = 5 * 60 * 1000;
const DEFAULT_ETA_SECONDS = 7;

type StrategiesPanelProps = {
  tokenOptions: TokenOption[];
  apiBaseUrl: string;
  cache: Record<string, StrategyCacheEntry>;
  onCacheUpdate: (key: string, entry: StrategyCacheEntry) => void;
};

type FetchState = {
  response: ApiResponse | null;
  error: string | null;
  isLoading: boolean;
  isRefreshing: boolean;
  isCached: boolean;
  lastUpdated: number | null;
};

const initialFetchState: FetchState = {
  response: null,
  error: null,
  isLoading: false,
  isRefreshing: false,
  isCached: false,
  lastUpdated: null,
};

function getCacheKey(token: string, risk: RiskLevel, wrappers: boolean): string {
  return JSON.stringify({ token: token.trim().toUpperCase(), risk, wrappers });
}

export default function StrategiesPanel({
  tokenOptions,
  apiBaseUrl,
  cache,
  onCacheUpdate,
}: StrategiesPanelProps): JSX.Element {
  const {
    token,
    riskLevel,
    includeWrappers,
    sortBy,
    growthFilter,
    onlyNew,
    onlyTop,
    requestId,
    setToken,
    setRiskLevel,
    setIncludeWrappers,
    setSortBy,
    setGrowthFilter,
    setOnlyNew,
    setOnlyTop,
    triggerFetch,
  } = useStrategyFilters(
    useShallow((state) => ({
      token: state.token,
      riskLevel: state.riskLevel,
      includeWrappers: state.includeWrappers,
      sortBy: state.sortBy,
      growthFilter: state.growthFilter,
      onlyNew: state.onlyNew,
      onlyTop: state.onlyTop,
      requestId: state.requestId,
      setToken: state.setToken,
      setRiskLevel: state.setRiskLevel,
      setIncludeWrappers: state.setIncludeWrappers,
      setSortBy: state.setSortBy,
      setGrowthFilter: state.setGrowthFilter,
      setOnlyNew: state.setOnlyNew,
      setOnlyTop: state.setOnlyTop,
      triggerFetch: state.triggerFetch,
    })),
  );

  const [fetchState, setFetchState] = useState<FetchState>(initialFetchState);
  const [isTokenModalOpen, setTokenModalOpen] = useState(false);
  const [tokenQuery, setTokenQuery] = useState("");
  const [showAll, setShowAll] = useState(false);
  const [etaSeconds, setEtaSeconds] = useState<number | null>(null);
  const [showSkeleton, setShowSkeleton] = useState(false);
  const [isPending, startTransition] = useTransition();

  const cacheRef = useRef(cache);
  const bypassRef = useRef(false);
  const controllerRef = useRef<AbortController | null>(null);
  const etaTimerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    cacheRef.current = cache;
  }, [cache]);

  useEffect(() => {
    if (fetchState.isLoading || fetchState.isRefreshing) {
      setEtaSeconds(DEFAULT_ETA_SECONDS);
      if (etaTimerRef.current) {
        clearInterval(etaTimerRef.current);
      }
      etaTimerRef.current = setInterval(() => {
        setEtaSeconds((prev) => {
          if (prev === null) return null;
          if (prev <= 0) return 0;
          return prev - 1;
        });
      }, 1000);
    } else {
      setEtaSeconds(null);
      if (etaTimerRef.current) {
        clearInterval(etaTimerRef.current);
        etaTimerRef.current = null;
      }
    }

    return () => {
      if (etaTimerRef.current) {
        clearInterval(etaTimerRef.current);
        etaTimerRef.current = null;
      }
    };
  }, [fetchState.isLoading, fetchState.isRefreshing]);

  useEffect(() => {
    const trimmedToken = token.trim();
    if (!trimmedToken) {
      setFetchState(initialFetchState);
      return;
    }

    const cacheKey = getCacheKey(trimmedToken, riskLevel, includeWrappers);
    const cachedEntry = cacheRef.current[cacheKey];
    const controller = new AbortController();

    if (controllerRef.current) {
      controllerRef.current.abort();
    }
    controllerRef.current = controller;

    const shouldUseCache =
      !bypassRef.current &&
      cachedEntry &&
      Date.now() - cachedEntry.updatedAt < CACHE_TTL_MS &&
      cachedEntry.data.status === "ok";

    setFetchState((prev) => ({
      ...prev,
      isLoading: true,
      isRefreshing: !shouldUseCache,
      isCached: shouldUseCache,
      error: null,
      response: shouldUseCache ? cachedEntry.data : prev.response,
      lastUpdated: shouldUseCache ? cachedEntry.updatedAt : prev.lastUpdated,
    }));

    const run = async () => {
      try {
        const data = await fetchStrategies(
          apiBaseUrl,
          {
            token: trimmedToken,
            preferences: {
              risk_level: riskLevel,
              include_wrappers: includeWrappers,
              min_tvl: 1_000_000,
            },
            result_limit: 200,
          },
          controller.signal,
        );
        if (controller.signal.aborted) {
          return;
        }

        const entry: StrategyCacheEntry = {
          data,
          updatedAt: Date.now(),
        };
        cacheRef.current[cacheKey] = entry;
        onCacheUpdate(cacheKey, entry);

        setFetchState({
          response: data,
          error: null,
          isLoading: false,
          isRefreshing: false,
          isCached: false,
          lastUpdated: entry.updatedAt,
        });
      } catch (err) {
        if (controller.signal.aborted) {
          return;
        }
        const message =
          err instanceof Error ? err.message : "Не удалось загрузить стратегии, попробуйте позже.";
        setFetchState((prev) => ({
          ...prev,
          error: message,
          isLoading: false,
          isRefreshing: false,
        }));
      } finally {
        bypassRef.current = false;
      }
    };

    run();

    return () => {
      controller.abort();
    };
  }, [apiBaseUrl, includeWrappers, onCacheUpdate, requestId, riskLevel, token]);

  useEffect(() => {
    let timer: NodeJS.Timeout | null = null;
    if ((fetchState.isLoading || fetchState.isRefreshing || isPending) && !timer) {
      timer = setTimeout(() => setShowSkeleton(true), 100);
    } else {
      setShowSkeleton(false);
    }
    return () => {
      if (timer) {
        clearTimeout(timer);
      }
    };
  }, [fetchState.isLoading, fetchState.isRefreshing, isPending]);

  const filteredTokens = useMemo(() => {
    if (!tokenQuery.trim()) {
      return tokenOptions;
    }
    const q = tokenQuery.trim().toLowerCase();
    return tokenOptions.filter((item) => {
      const label = item.label.toLowerCase();
      const value = item.value.toLowerCase();
      const slug = item.slug?.toLowerCase() ?? "";
      return label.includes(q) || value.includes(q) || slug.includes(q);
    });
  }, [tokenOptions, tokenQuery]);

  const filteredStrategies = useMemo(() => {
    if (fetchState.response?.status !== "ok") {
      return [] as Strategy[];
    }

    const list = fetchState.response.all_strategies ?? [
      fetchState.response.best_strategy,
      ...fetchState.response.alternatives,
    ];

    let result = list.filter(Boolean) as Strategy[];

    if (growthFilter === "apy_growth_gt_5") {
      result = result.filter((item) => (item.apy_7d ?? 0) >= 5);
    }

    if (onlyNew) {
      result = result.filter((item) => {
        const delta = item.apy_7d ?? 0;
        const tvl = item.tvl_usd ?? 0;
        return delta >= 0.5 || tvl < 2_000_000;
      });
    }

    switch (sortBy) {
      case "tvl":
        result = result.slice().sort((a, b) => (b.tvl_usd ?? 0) - (a.tvl_usd ?? 0));
        break;
      case "novelty":
        result = result.slice().sort((a, b) => (b.apy_7d ?? -Infinity) - (a.apy_7d ?? -Infinity));
        break;
      case "apy":
      default:
        result = result.slice().sort((a, b) => (b.apy ?? 0) - (a.apy ?? 0));
        break;
    }

    if (onlyTop) {
      result = result.slice(0, 10);
    }

    return result;
  }, [fetchState.response, growthFilter, onlyNew, onlyTop, sortBy]);

  const bestStrategy = useMemo(() => {
    if (fetchState.response?.status !== "ok") {
      return null;
    }
    return fetchState.response.best_strategy;
  }, [fetchState.response]);

  const previewStrategies = useMemo(() => {
    if (!filteredStrategies.length) {
      return bestStrategy ? [bestStrategy] : [];
    }
    const list: Strategy[] = [];
    if (bestStrategy) {
      list.push(bestStrategy);
    }
    filteredStrategies
      .filter((strategy) => !bestStrategy || strategyKey(strategy) !== strategyKey(bestStrategy))
      .slice(0, 3)
      .forEach((item) => list.push(item));

    return list;
  }, [bestStrategy, filteredStrategies]);

  const tableStrategies = useMemo(() => {
    const bestKey = bestStrategy ? strategyKey(bestStrategy) : null;
    return filteredStrategies.filter((item) => !bestKey || strategyKey(item) !== bestKey);
  }, [bestStrategy, filteredStrategies]);

  const totalVisible = previewStrategies.length;
  const totalFound =
    fetchState.response?.status === "ok"
      ? fetchState.response.statistics?.matched ?? filteredStrategies.length
      : 0;

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!token.trim()) {
      setFetchState((prev) => ({
        ...prev,
        error: "Укажи тикер токена",
      }));
      return;
    }
    bypassRef.current = true;
    triggerFetch();
  };

  const showLoadingGenie = fetchState.isLoading || fetchState.isRefreshing;
  const genieMode = fetchState.isLoading ? "search" : "refresh";

  return (
    <>
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
                {token || "Выбрать токен"}
              </button>
            </div>
          </div>
          <div className="form-row">
            <label htmlFor="riskLevel">Уровень риска</label>
            <select
              id="riskLevel"
              value={riskLevel}
              onChange={(event) => setRiskLevel(event.target.value as RiskLevel)}
            >
              {riskOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="form-row checkbox-row">
          <label className="checkbox">
            <input
              type="checkbox"
              checked={includeWrappers}
              onChange={(event) => setIncludeWrappers(event.target.checked)}
            />
            <span>Показывать обёрнутые токены (wETH, stETH и т.д.)</span>
          </label>
        </div>

        <button className="submit" type="submit" disabled={!token.trim()}>
          {fetchState.isLoading
            ? "Ищем стратегии..."
            : fetchState.isRefreshing && fetchState.isCached
              ? "Обновляем..."
              : "Найти стратегии"}
        </button>
      </form>

      {showSkeleton && (fetchState.isLoading || fetchState.isRefreshing || isPending) && (
        <StrategiesSkeleton />
      )}

      {showLoadingGenie && <LoadingGenie mode={genieMode} etaSeconds={etaSeconds} />}

      <div className="sort-toolbar">
        <div className="sort-toolbar__group">
          <span className="sort-toolbar__label">Сортировать по</span>
          <div className="sort-toolbar__options">
            {sortOptions.map((option) => (
              <button
                key={option.value}
                type="button"
                className={`sort-option${sortBy === option.value ? " is-active" : ""}`}
                onClick={() => setSortBy(option.value)}
                aria-pressed={sortBy === option.value}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>
        <div className="sort-toolbar__group">
          <span className="sort-toolbar__label">Фильтры</span>
          <div className="sort-toolbar__filters">
            <button
              type="button"
              className={`toolbar-toggle${growthFilter === "apy_growth_gt_5" ? " is-active" : ""}`}
              onClick={() =>
                setGrowthFilter(growthFilter === "apy_growth_gt_5" ? "none" : "apy_growth_gt_5")
              }
              aria-pressed={growthFilter === "apy_growth_gt_5"}
            >
              Рост APY &gt; 5%
            </button>
            <button
              type="button"
              className={`toolbar-toggle${onlyNew ? " is-active" : ""}`}
              onClick={() => setOnlyNew(!onlyNew)}
              aria-pressed={onlyNew}
            >
              Только новые
            </button>
            <button
              type="button"
              className={`toolbar-toggle${onlyTop ? " is-active" : ""}`}
              onClick={() => setOnlyTop(!onlyTop)}
              aria-pressed={onlyTop}
            >
              Топовые
            </button>
          </div>
        </div>
      </div>

      {fetchState.error && <div className="error-card">⚠️ {fetchState.error}</div>}

      {fetchState.response?.status === "ok" && (
        <div className="result-card">
          <h3>Лучшая стратегия для {fetchState.response.token}</h3>

          <div className="strategy-list">
            {previewStrategies.map((strategy, index) => (
              <StrategyCard
                key={`${strategyKey(strategy)}-${index}`}
                strategy={strategy}
                isBest={index === 0}
              />
            ))}
          </div>

          <p className="stats">
            Показано {totalVisible} стратегий из {totalFound} найденных.
            {fetchState.lastUpdated
              ? ` Обновлено в ${new Date(fetchState.lastUpdated).toLocaleTimeString("ru-RU")}.`
              : ""}
          </p>

          {tableStrategies.length > 0 && (
            <div className="view-all-toggle">
              <button
                type="button"
                className="submit ghost view-all-button"
                onClick={() => setShowAll((prev) => !prev)}
              >
                {showAll
                  ? "Скрыть все стратегии"
                  : `Показать все стратегии (${tableStrategies.length})`}
              </button>
            </div>
          )}

          {showAll && tableStrategies.length > 0 && (
            <div className="table-wrapper all-strategies">
              <table>
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Протокол</th>
                    <th>Тикер</th>
                    <th>Сеть</th>
                    <th>APY</th>
                    <th>Δ APY 7д</th>
                    <th>Риск</th>
                    <th>TVL</th>
                    <th>Score</th>
                    <th>Ссылка</th>
                  </tr>
                </thead>
                <tbody>
                  {tableStrategies.map((strategy, index) => {
                    const link =
                      strategy.action_url ?? strategy.protocol_url ?? strategy.pool_url ?? undefined;
                    return (
                      <tr key={`${strategyKey(strategy)}-${index}`}>
                        <td>{index + 1}</td>
                        <td>{strategy.platform ?? "—"}</td>
                        <td>{strategy.symbol ?? "—"}</td>
                        <td>{strategy.chain ? formatLabel(strategy.chain) : "—"}</td>
                        <td>{formatPercent(strategy.apy)}</td>
                        <td>{formatPercent(strategy.apy_7d)}</td>
                        <td>{strategy.risk_level ? strategy.risk_level.toUpperCase() : "—"}</td>
                        <td>{strategy.tvl_usd ? `${formatNumber(strategy.tvl_usd, 0)} $` : "—"}</td>
                        <td>{strategy.score !== undefined ? formatNumber(strategy.score) : "—"}</td>
                        <td>
                          {link ? (
                            <a href={link} target="_blank" rel="noopener noreferrer">
                              Открыть
                            </a>
                          ) : (
                            "—"
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {fetchState.response?.status === "empty" && (
        <div className="result-card">
          <h3>Стратегии не найдены</h3>
          <p>Попробуй изменить фильтры или выбрать другой токен.</p>
        </div>
      )}

      <SingleSelectionModal
        title="Выбор токена"
        isOpen={isTokenModalOpen}
        options={filteredTokens}
        selected={token}
        query={tokenQuery}
        onQueryChange={setTokenQuery}
        onSelect={(value) => {
          startTransition(() => setToken(value));
          setTokenModalOpen(false);
        }}
        onClose={() => setTokenModalOpen(false)}
        isLoading={!tokenOptions.length}
      />
    </>
  );
}

function strategyKey(strategy: Strategy): string {
  return [
    strategy.platform ?? "",
    strategy.chain ?? "",
    strategy.symbol ?? "",
    strategy.pool_url ?? "",
    strategy.protocol_url ?? "",
    strategy.action_url ?? "",
  ].join("|");
}

function StrategyCard({ strategy, isBest }: { strategy: Strategy; isBest: boolean }) {
  const title = strategy.platform ?? strategy.symbol ?? "Неизвестный протокол";
  const link = strategy.action_url ?? strategy.protocol_url ?? strategy.pool_url ?? undefined;
  const apyTrend = strategy.apy_7d ?? null;
  const isTrendPositive = (apyTrend ?? 0) >= 0;
  const tokensLabel = (strategy.tokens ?? []).join(" / ") || strategy.symbol || "—";
  const riskLabel = strategy.risk_level ? strategy.risk_level.toUpperCase() : "—";
  const tvlLabel = strategy.tvl_usd ? `${formatNumber(strategy.tvl_usd, 0)} $` : "—";
  const chainLabel = strategy.chain ? formatLabel(strategy.chain) : "Неизвестная сеть";

  return (
    <article className={`strategy-card ${isBest ? "best" : ""}`}>
      <div className="strategy-card__header">
        <div className="strategy-card__title">
          <span className="strategy-avatar">{(strategy.symbol ?? "?").slice(0, 4)}</span>
          <div>
            <div className="strategy-card__name">{title}</div>
            <div className="strategy-card__chain">{chainLabel}</div>
          </div>
        </div>
        <div className="strategy-card__actions">
          {isBest && <span className="strategy-card__badge">Лучшая</span>}
          {link && (
            <a className="strategy-card__cta" href={link} target="_blank" rel="noopener noreferrer">
              Перейти
            </a>
          )}
        </div>
      </div>

      <div className="strategy-card__meta">
        <span>
          <strong>Платформа:</strong> {strategy.platform ?? "—"}
        </span>
        <span>
          <strong>TVL:</strong> {tvlLabel}
        </span>
        <span>
          <strong>Риск:</strong> {riskLabel}
        </span>
      </div>

      <div className="strategy-card__metrics">
        <div className="metric">
          <span className="metric-label">APY</span>
          <span className="metric-value">
            {formatPercent(strategy.apy)}
            {apyTrend !== null && !Number.isNaN(apyTrend) && (
              <span
                className={`apy-trend ${isTrendPositive ? "positive" : "negative"}`}
                title="Динамика доходности за неделю"
              >
                {isTrendPositive ? "▲" : "▼"} {Math.abs(apyTrend).toFixed(2)}%
              </span>
            )}
          </span>
        </div>
        <div className="metric">
          <span className="metric-label">Токен</span>
          <span className="metric-value">{tokensLabel}</span>
        </div>
        {strategy.score !== undefined && (
          <div className="metric">
            <span className="metric-label">Score</span>
            <span className="metric-value">{formatNumber(strategy.score)}</span>
          </div>
        )}
      </div>
    </article>
  );
}

type SingleSelectionModalProps = {
  title: string;
  isOpen: boolean;
  options: { value: string; label: string }[];
  selected: string | null;
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
  isLoading,
}: SingleSelectionModalProps) {
  if (!isOpen) {
    return null;
  }

  return (
    <div className="modal-backdrop" role="dialog" aria-modal="true">
      <div className="modal">
        <header className="modal-header">
          <h3>{title}</h3>
          <button type="button" onClick={onClose} aria-label="Закрыть">
            ×
          </button>
        </header>
        <div className="modal-search">
          <input
            type="search"
            placeholder="Поиск по тикеру или названию"
            value={query}
            onChange={(event) => onQueryChange(event.target.value)}
          />
        </div>
        <div className="modal-content">
          {isLoading ? (
            <p>Загружаем...</p>
          ) : (
            <ul>
              {options.map((option) => (
                <li key={option.value}>
                  <button
                    type="button"
                    className={option.value === selected ? "selected" : ""}
                    onClick={() => onSelect(option.value)}
                  >
                    <span>{option.label}</span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
