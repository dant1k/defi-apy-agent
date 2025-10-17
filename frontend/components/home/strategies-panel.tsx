import { ChangeEvent, useEffect, useMemo, useState, useRef } from "react";
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
  tokens?: string[];
};

type FetchState = {
  items: AggregatedStrategy[];
  total: number;
  updatedAt: string | null;
};

const DEFAULT_FILTERS: FiltersState = {
  chain: "all",
  protocol: "all",
  token: "all",
  minTvl: 1_000_000,
  minApy: 0,
  sort: "ai_score_desc",
};

const PAGE_LIMIT = 150;

export default function StrategiesPanel({ apiBaseUrl, chains, protocols, tokens = [] }: StrategiesPanelProps): JSX.Element {
  const [filters, setFilters] = useState<FiltersState>(DEFAULT_FILTERS);
  const [fetchState, setFetchState] = useState<FetchState>({ items: [], total: 0, updatedAt: null });
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedStrategy, setSelectedStrategy] = useState<AggregatedStrategy | null>(null);
  // удалён текстовый поиск по токену

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
        const fetched = response.items;
        const filteredByToken = filters.token && filters.token !== "all"
          ? fetched.filter((it) => (it.token_pair || "").toUpperCase().includes((filters.token || "").toUpperCase()))
          : fetched;
        setFetchState({ items: filteredByToken, total: filteredByToken.length, updatedAt: response.updated_at });
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

  function getChainIconUrl(name: string): string {
    // Нормализуем имя для файла
    const file = name?.toUpperCase().replace(/[^A-Z0-9]/g, "");
    return `/icons/chains/${encodeURIComponent(file)}.png`;
  }

  function getTokenIconUrl(symbol: string): string {
    return `/icons/tokens/${encodeURIComponent(symbol)}.png`;
  }

  function getProtocolIconUrl(name: string): string {
    // нормализуем имя протокола для поиска в DeFiLlama иконках
    const file = name?.toUpperCase().replace(/[^A-Z0-9]/g, "");
    return `/icons/protocols/${encodeURIComponent(file)}.png`;
  }

  const rows = fetchState.items;


  return (
    <div className="strategies-panel">
      <header className="strategies-header">
        <h2>Top DeFi Strategies</h2>
        <p>
          Подборка стратегий с учётом APY, роста TVL и риск-скоринга. Актуальность:{" "}
          {fetchState.updatedAt ? new Date(fetchState.updatedAt).toLocaleString("ru-RU") : "—"}.
        </p>
      </header>

      <section className="strategies-filters">
        <div className="filter-group">
          <label htmlFor="chain-select">Сеть</label>
          <SearchableSelect
            value={filters.chain}
            onChange={(value) => setFilters(prev => ({ ...prev, chain: value }))}
            options={[
              { value: "all", label: "Все сети", icon: null },
              ...chains.map(item => ({
                value: item,
                label: formatLabel(item),
                icon: getChainIconUrl(item)
              }))
            ]}
            placeholder="Выберите сеть"
            searchPlaceholder="Поиск сети..."
          />
        </div>

        <div className="filter-group">
          <label htmlFor="protocol-select">Протокол</label>
          <SearchableSelect
            value={filters.protocol}
            onChange={(value) => setFilters(prev => ({ ...prev, protocol: value }))}
            options={[
              { value: "all", label: "Все протоколы", icon: null },
              ...protocols.map(item => ({
                value: item,
                label: formatLabel(item),
                icon: getProtocolIconUrl(item)
              }))
            ]}
            placeholder="Выберите протокол"
            searchPlaceholder="Поиск протокола..."
          />
        </div>

        <div className="filter-group">
          <label htmlFor="token-select">Токен</label>
          <SearchableSelect
            value={filters.token}
            onChange={(value) => setFilters(prev => ({ ...prev, token: value }))}
            options={[
              { value: "all", label: "Все токены", icon: null },
              ...tokens.map(symbol => ({
                value: symbol,
                label: symbol,
                icon: getTokenIconUrl(symbol)
              }))
            ]}
            placeholder="Выберите токен"
            searchPlaceholder="Поиск токена..."
          />
        </div>

        {/* Поле поиска по токену удалено по просьбе пользователя */}

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
          total={rows.length}
          onSelect={(item) => setSelectedStrategy(item)}
          getChainIconUrl={getChainIconUrl}
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
  getChainIconUrl,
}: {
  strategies: AggregatedStrategy[];
  total: number;
  onSelect: (strategy: AggregatedStrategy) => void;
  getChainIconUrl: (name: string) => string;
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
              <td>
                <span style={{ display: "inline-flex", alignItems: "center", gap: 8 }}>
                  {strategy.icon_url && (
                    <img src={strategy.icon_url} alt="" width={16} height={16} loading="lazy" onError={(e) => ((e.currentTarget.style.display = "none"))} />
                  )}
                  {formatLabel(strategy.protocol)}
                </span>
              </td>
              <td>
                <span style={{ display: "inline-flex", alignItems: "center", gap: 8 }}>
                  <img src={getChainIconUrl(strategy.chain)} alt="" width={16} height={16} loading="lazy" onError={(e) => ((e.currentTarget.style.display = "none"))} />
                  {formatLabel(strategy.chain)}
                </span>
              </td>
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

// Icon with Fallback Component
type IconWithFallbackProps = {
  src: string;
  alt: string;
  width?: number;
  height?: number;
  className?: string;
};

function IconWithFallback({ src, alt, width = 18, height = 18, className }: IconWithFallbackProps) {
  const [currentSrc, setCurrentSrc] = useState(src);
  const [hasError, setHasError] = useState(false);

  const handleError = () => {
    if (!hasError && currentSrc.startsWith('/icons/')) {
      // Если локальная иконка не найдена, пробуем через бекенд
      const backendSrc = currentSrc.replace('/icons/', 'http://localhost:8000/icons/');
      setCurrentSrc(backendSrc);
      setHasError(true);
    } else {
      // Скрываем иконку, если и бекенд не помог
      setCurrentSrc('');
    }
  };

  if (!currentSrc) {
    return null;
  }

  return (
    <img 
      src={currentSrc} 
      alt={alt} 
      width={width} 
      height={height} 
      loading="lazy" 
      onError={handleError}
      className={className}
    />
  );
}

// Custom Select Component with Icons
type SelectOption = {
  value: string;
  label: string;
  icon: string | null;
};

type CustomSelectProps = {
  value: string;
  onChange: (value: string) => void;
  options: SelectOption[];
  placeholder?: string;
};

type SearchableSelectProps = {
  value: string;
  onChange: (value: string) => void;
  options: SelectOption[];
  placeholder?: string;
  searchPlaceholder?: string;
};

function CustomSelect({ value, onChange, options, placeholder }: CustomSelectProps) {
  const [isOpen, setIsOpen] = useState(false);
  const selectRef = useRef<HTMLDivElement>(null);

  const selectedOption = options.find(option => option.value === value);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (selectRef.current && !selectRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="custom-select" ref={selectRef}>
      <div 
        className={`custom-select__trigger ${isOpen ? 'is-open' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="custom-select__value">
          {selectedOption?.icon && (
            <IconWithFallback 
              src={selectedOption.icon} 
              alt="" 
              width={18} 
              height={18}
            />
          )}
          <span>{selectedOption?.label || placeholder}</span>
        </div>
        <div className="custom-select__arrow">▼</div>
      </div>
      
      {isOpen && (
        <div className="custom-select__options">
          {options.map((option) => (
            <div
              key={option.value}
              className={`custom-select__option ${option.value === value ? 'is-selected' : ''}`}
              onClick={() => {
                onChange(option.value);
                setIsOpen(false);
              }}
            >
              {option.icon && (
                <IconWithFallback 
                  src={option.icon} 
                  alt="" 
                  width={18} 
                  height={18}
                />
              )}
              <span>{option.label}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function SearchableSelect({ value, onChange, options, placeholder, searchPlaceholder = "Поиск..." }: SearchableSelectProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const selectRef = useRef<HTMLDivElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);

  const selectedOption = options.find(option => option.value === value);

  // Фильтруем опции по поисковому запросу
  const filteredOptions = options.filter(option =>
    option.label.toLowerCase().includes(searchQuery.toLowerCase())
  );

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (selectRef.current && !selectRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setSearchQuery("");
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    if (isOpen && searchInputRef.current) {
      searchInputRef.current.focus();
    }
  }, [isOpen]);

  const handleOptionClick = (optionValue: string) => {
    onChange(optionValue);
    setIsOpen(false);
    setSearchQuery("");
  };

  return (
    <div className="custom-select" ref={selectRef}>
      <div 
        className={`custom-select__trigger ${isOpen ? 'is-open' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="custom-select__value">
          {selectedOption?.icon && (
            <IconWithFallback 
              src={selectedOption.icon} 
              alt="" 
              width={18} 
              height={18}
            />
          )}
          <span>{selectedOption?.label || placeholder}</span>
        </div>
        <div className="custom-select__arrow">▼</div>
      </div>
      
      {isOpen && (
        <div className="custom-select__options">
          <div className="custom-select__search">
            <input
              ref={searchInputRef}
              type="text"
              placeholder={searchPlaceholder}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="custom-select__search-input"
              onClick={(e) => e.stopPropagation()}
            />
          </div>
          <div className="custom-select__options-list">
            {filteredOptions.length > 0 ? (
              filteredOptions.map((option) => (
                <div
                  key={option.value}
                  className={`custom-select__option ${option.value === value ? 'is-selected' : ''}`}
                  onClick={() => handleOptionClick(option.value)}
                >
                  {option.icon && (
                    <IconWithFallback 
                      src={option.icon} 
                      alt="" 
                      width={18} 
                      height={18}
                    />
                  )}
                  <span>{option.label}</span>
                </div>
              ))
            ) : (
              <div className="custom-select__no-results">
                Ничего не найдено
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}