import { ChangeEvent, useEffect, useMemo, useState } from "react";
import dynamic from "next/dynamic";
import type { AggregatedStrategy, FiltersState } from "./types";
import { formatLabel, formatNumber, formatPercent } from "./formatters";
import { fetchAggregatorStrategies } from "../../lib/api";
import { StrategyDetailModal } from "./strategy-detail-modal";

const StrategiesSkeleton = dynamic(
  () => import("./home-skeleton").then((mod) => mod.StrategiesSkeleton),
  { ssr: false },
);

type StrategiesPanelProps = {
  apiBaseUrl: string;
  chains: string[];
  protocols: string[];
};

type FetchState = {
  items: AggregatedStrategy[];
  total: number;
  updatedAt: string | null;
};

const DEFAULT_FILTERS: FiltersState = {
  chain: "all",
  protocol: "all",
  minTvl: 1_000_000,
  minApy: 0,
  sort: "ai_score_desc",
};

const PAGE_LIMIT = 150;

export default function StrategiesPanel({ apiBaseUrl, chains, protocols }: StrategiesPanelProps): JSX.Element {
  const [filters, setFilters] = useState<FiltersState>(DEFAULT_FILTERS);
  const [fetchState, setFetchState] = useState<FetchState>({ items: [], total: 0, updatedAt: null });
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedStrategy, setSelectedStrategy] = useState<AggregatedStrategy | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    async function loadData() {
      setIsLoading(true);
      setError(null);
      try {
        const response = await fetchAggregatorStrategies(
          apiBaseUrl,
          {
            chain: filters.chain === "all" ? null : filters.chain,
            protocol: filters.protocol === "all" ? null : filters.protocol,
            min_tvl: filters.minTvl || null,
            min_apy: filters.minApy || null,
            sort: filters.sort,
            limit: PAGE_LIMIT,
          },
          controller.signal,
        );
        setFetchState({ items: response.items, total: response.total, updatedAt: response.updated_at });
      } catch (err) {
        if (!controller.signal.aborted) {
          const message = err instanceof Error ? err.message : "Не удалось загрузить данные";
          setError(message);
        }
      } finally {
        if (!controller.signal.aborted) {
          setIsLoading(false);
        }
      }
    }

    loadData();
    return () => controller.abort();
  }, [apiBaseUrl, filters]);

  const handleSelectChange = (event: ChangeEvent<HTMLSelectElement>) => {
    const { name, value } = event.target;
    setFilters((prev) => ({ ...prev, [name]: value }));
  };

  const handleNumberChange = (event: ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target;
    const numeric = Number(value);
    setFilters((prev) => ({ ...prev, [name]: Number.isNaN(numeric) ? prev[name as keyof FiltersState] : numeric }));
  };

  const sortOptions: Array<{ value: FiltersState["sort"]; label: string }> = useMemo(
    () => [
      { value: "ai_score_desc", label: "AI Score" },
      { value: "apy_desc", label: "APY" },
      { value: "tvl_desc", label: "TVL" },
      { value: "tvl_growth_desc", label: "Рост TVL" },
    ],
    [],
  );

  const rows = fetchState.items;

  return (
    <div className="strategies-panel">
      <header className="strategies-header">
        <h2>Top DeFi Strategies</h2>
        <p>
          Подборка стратегий с учётом APY, роста TVL и риск-скоринга. Актуальность:
          {" "}
          {fetchState.updatedAt ? new Date(fetchState.updatedAt).toLocaleString("ru-RU") : "—"}.
        </p>
      </header>

      <section className="strategies-filters">
        <div className="filter-group">
          <label htmlFor="chain-select">Сеть</label>
          <select id="chain-select" name="chain" value={filters.chain} onChange={handleSelectChange}>
            <option value="all">Все сети</option>
            {chains.map((item) => (
              <option key={item} value={item}>
                {formatLabel(item)}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="protocol-select">Протокол</label>
          <select id="protocol-select" name="protocol" value={filters.protocol} onChange={handleSelectChange}>
            <option value="all">Все протоколы</option>
            {protocols.map((item) => (
              <option key={item} value={item}>
                {formatLabel(item)}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="minTvl">Мин. TVL ($)</label>
          <input
            id="minTvl"
            name="minTvl"
            type="number"
            min={0}
            step={100000}
            value={filters.minTvl}
            onChange={handleNumberChange}
          />
        </div>

        <div className="filter-group">
          <label htmlFor="minApy">Мин. APY (%)</label>
          <input
            id="minApy"
            name="minApy"
            type="number"
            min={0}
            step={0.1}
            value={filters.minApy}
            onChange={handleNumberChange}
          />
        </div>

        <div className="filter-group filter-group--sort">
          <span>Сортировка</span>
          <div className="sort-buttons">
            {sortOptions.map((option) => (
              <button
                key={option.value}
                type="button"
                className={`sort-option${filters.sort === option.value ? " is-active" : ""}`}
                onClick={() => setFilters((prev) => ({ ...prev, sort: option.value }))}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>
      </section>

      {error && <div className="error-card">⚠️ {error}</div>}

      {isLoading ? (
        <StrategiesSkeleton />
      ) : (
        <StrategyTable
          strategies={rows}
          total={fetchState.total}
          onSelect={(item) => setSelectedStrategy(item)}
        />
      )}

      {selectedStrategy && (
        <StrategyDetailModal
          apiBaseUrl={apiBaseUrl}
          strategy={selectedStrategy}
          onClose={() => setSelectedStrategy(null)}
        />
      )}
    </div>
  );
}

function StrategyTable({
  strategies,
  total,
  onSelect,
}: {
  strategies: AggregatedStrategy[];
  total: number;
  onSelect: (strategy: AggregatedStrategy) => void;
}): JSX.Element {
  return (
    <div className="strategy-table">
      <div className="table-meta">Найдено стратегий: {total}</div>
      <table>
        <thead>
          <tr>
            <th>Стратегия</th>
            <th>Протокол</th>
            <th>Сеть</th>
            <th>APY</th>
            <th>TVL</th>
            <th>Рост TVL 24ч</th>
            <th>Риск</th>
            <th>AI Score</th>
            <th>Ссылка</th>
          </tr>
        </thead>
        <tbody>
          {strategies.map((strategy) => (
            <tr
              key={strategy.id}
              className="strategy-row"
              onClick={() => onSelect(strategy)}
              tabIndex={0}
              role="button"
              aria-label={`Подробнее о стратегии ${strategy.name}`}
              onKeyDown={(event) => {
                if (event.key === "Enter" || event.key === " ") {
                  event.preventDefault();
                  onSelect(strategy);
                }
              }}
            >
              <td>
                <div className="strategy-name">
                  {strategy.icon_url && (
                    <img src={strategy.icon_url} alt={strategy.protocol} loading="lazy" />
                  )}
                  <div>
                    <strong>{strategy.name}</strong>
                    {strategy.token_pair && <div className="token-pair">{strategy.token_pair}</div>}
                    {strategy.ai_comment && <div className="ai-comment">{strategy.ai_comment}</div>}
                  </div>
                </div>
              </td>
              <td>{formatLabel(strategy.protocol)}</td>
              <td>{formatLabel(strategy.chain)}</td>
              <td>{formatPercent(strategy.apy)}</td>
              <td>{formatNumber(strategy.tvl_usd, 0)} $</td>
              <td className={strategy.tvl_growth_24h >= 0 ? "positive" : "negative"}>
                {formatPercent(strategy.tvl_growth_24h)}
              </td>
              <td>{strategy.risk_index !== null ? strategy.risk_index.toFixed(2) : "—"}</td>
              <td>{strategy.ai_score !== null && strategy.ai_score !== undefined ? strategy.ai_score.toFixed(2) : "—"}</td>
              <td>
                {strategy.url ? (
                  <a href={strategy.url} target="_blank" rel="noopener noreferrer">
                    Открыть
                  </a>
                ) : (
                  "—"
                )}
              </td>
            </tr>
          ))}
          {strategies.length === 0 && (
            <tr>
              <td colSpan={9} className="empty-state">
                Подходящих стратегий пока нет. Попробуй изменить фильтры.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
