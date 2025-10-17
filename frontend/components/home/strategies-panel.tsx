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
  minTvl: "",
  minApy: "",
  sort: "ai_score_desc",
};

const PAGE_LIMIT = 150;

export default function StrategiesPanel({ apiBaseUrl, chains, protocols, tokens = [] }: StrategiesPanelProps): JSX.Element {
  const [filters, setFilters] = useState<FiltersState>(DEFAULT_FILTERS);
  const [fetchState, setFetchState] = useState<FetchState>({ items: [], total: 0, updatedAt: null });
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedStrategy, setSelectedStrategy] = useState<AggregatedStrategy | null>(null);
  const [showAllStrategies, setShowAllStrategies] = useState<boolean>(false);
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
            min_tvl: filters.minTvl ? Number(filters.minTvl) : null,
            min_apy: filters.minApy ? Number(filters.minApy) : null,
            sort: filters.sort,
            limit: PAGE_LIMIT,
          },
          controller.signal,
        );
        const fetched = response.items;
        
        // Filter by TVL (minimum 100,000)
        const filteredByTvl = fetched.filter((it) => (it.tvl_usd || 0) >= 100000);
        
        // Filter by token if specified
        const filteredByToken = filters.token && filters.token !== "all"
          ? filteredByTvl.filter((it) => (it.token_pair || "").toUpperCase().includes((filters.token || "").toUpperCase()))
          : filteredByTvl;
          
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
    setFilters((prev) => ({ ...prev, [name]: value }));
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

  function getTokenPairIcons(pair: string): { first: string; second: string } | null {
    if (!pair) return null;
    
    // Разделяем пару по дефису или слешу
    const tokens = pair.split(/[-/]/);
    if (tokens.length >= 2) {
      return {
        first: getTokenIconUrl(tokens[0].trim()),
        second: getTokenIconUrl(tokens[1].trim())
      };
    }
    return null;
  }

  const rows = fetchState.items;


  return (
    <div className="strategies-panel">
      <header className="mb-8">
        <h2 className="font-orbitron text-3xl font-bold text-[var(--neonAqua)] mb-4">
          Top DeFi Strategies
        </h2>
        <p className="font-inter text-white/70 text-lg">
          Advanced strategy filtering with AI-powered insights. Last updated:{" "}
          {fetchState.updatedAt ? new Date(fetchState.updatedAt).toLocaleString("ru-RU") : "—"}
        </p>
      </header>

      <section className="card-genora mb-8">
        <h3 className="font-orbitron text-xl font-bold text-[var(--neonAqua)] mb-6">
          Advanced Filters
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="filter-group">
            <label htmlFor="chain-select" className="font-orbitron text-sm font-semibold text-white mb-2 block">
              Сеть
            </label>
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
            <label htmlFor="protocol-select" className="font-orbitron text-sm font-semibold text-white mb-2 block">
              Протокол
            </label>
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
            <label htmlFor="token-select" className="font-orbitron text-sm font-semibold text-white mb-2 block">
              Токен
            </label>
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

          <div className="filter-group">
            <label htmlFor="minTvl" className="font-orbitron text-sm font-semibold text-white mb-2 block">
              Мин. TVL ($)
            </label>
            <input
              id="minTvl"
              name="minTvl"
              type="number"
              min={0}
              step={100000}
              value={filters.minTvl}
              onChange={handleNumberChange}
              className="w-full px-3 py-2 bg-[var(--graphiteGray)] border border-white/20 rounded text-white placeholder-white/50 focus:border-[var(--neonAqua)] focus:outline-none"
              placeholder="0"
            />
          </div>

          <div className="filter-group">
            <label htmlFor="minApy" className="font-orbitron text-sm font-semibold text-white mb-2 block">
              Мин. APY (%)
            </label>
            <input
              id="minApy"
              name="minApy"
              type="number"
              min={0}
              step={0.1}
              value={filters.minApy}
              onChange={handleNumberChange}
              className="w-full px-3 py-2 bg-[var(--graphiteGray)] border border-white/20 rounded text-white placeholder-white/50 focus:border-[var(--neonAqua)] focus:outline-none"
              placeholder="0"
            />
          </div>
        </div>
      </section>

      <section className="card-genora mb-8">
        <h3 className="font-orbitron text-xl font-bold text-[var(--neonAqua)] mb-6">
          Sorting Options
        </h3>
        <div className="flex flex-wrap gap-3">
          {sortOptions.map((option) => (
            <button
              key={option.value}
              type="button"
              className={`px-4 py-2 rounded font-medium transition-colors ${
                filters.sort === option.value 
                  ? 'bg-[var(--neonAqua)] text-black' 
                  : 'bg-[var(--graphiteGray)] text-white/70 hover:text-white hover:border-[var(--neonAqua)] border border-transparent'
              }`}
              onClick={() => setFilters((prev) => ({ ...prev, sort: option.value }))}
            >
              {option.label}
            </button>
          ))}
        </div>
      </section>

      {error && (
        <div className="card-genora mb-8 border-red-500/50 bg-red-500/10">
          <div className="font-inter text-red-400 text-center py-4">
            {error}
          </div>
        </div>
      )}

      {isLoading ? (
        <div className="card-genora">
          <div className="text-center py-8">
            <div className="font-inter text-white/60">Loading strategies...</div>
          </div>
        </div>
      ) : (
        <>
          {/* Featured Strategy Section */}
          {rows.length > 0 && (
            <div className="mb-8">
              <h3 className="font-orbitron text-2xl font-bold text-[var(--neonAqua)] mb-6">
                Featured Strategy
              </h3>
              <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                {/* Main Strategy Card */}
                <div className="lg:col-span-2">
                  <div className="card-genora shadow-glow cursor-pointer hover:scale-105 transition-transform"
                       onClick={() => setSelectedStrategy(rows[0])}>
                    <div className="flex items-center space-x-4 mb-4">
                      {(() => {
                        const pair = rows[0].token_pair || rows[0].name;
                        const icons = getTokenPairIcons(pair);
                        return icons ? (
                          <>
                            <img src={icons.first} alt="" width={24} height={24} className="rounded" />
                            <img src={icons.second} alt="" width={24} height={24} className="rounded" />
                          </>
                        ) : null;
                      })()}
                      <div>
                        <h4 className="font-orbitron text-lg font-bold text-white">
                          {rows[0].token_pair || rows[0].name}
                        </h4>
                        <p className="font-inter text-sm text-white/60">
                          {formatLabel(rows[0].protocol)} • {formatLabel(rows[0].chain)}
                        </p>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="font-spacemono text-xs text-white/60">APY</p>
                        <p className="font-spacemono text-xl font-bold text-[var(--profitGreen)]">
                          {formatPercent(rows[0].apy)}
                        </p>
                      </div>
                      <div>
                        <p className="font-spacemono text-xs text-white/60">TVL</p>
                        <p className="font-spacemono text-lg font-semibold text-white">
                          {formatNumber(rows[0].tvl_usd, 2)} $
                        </p>
                      </div>
                      <div>
                        <p className="font-spacemono text-xs text-white/60">Risk</p>
                        <p className="font-spacemono text-sm text-white">
                          {rows[0].risk_index?.toFixed(2) || "—"}
                        </p>
                      </div>
                      <div>
                        <p className="font-spacemono text-xs text-white/60">AI Score</p>
                        <p className="font-spacemono text-sm font-bold text-[var(--neonAqua)]">
                          {rows[0].ai_score?.toFixed(2) || "—"}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Alternative Strategies */}
                <div className="lg:col-span-2">
                  <h4 className="font-orbitron text-lg font-bold text-[var(--neonAqua)] mb-4">
                    Alternative Strategies
                  </h4>
                  <div className="space-y-3">
                    {rows.slice(1, 4).map((strategy, index) => (
                      <div key={strategy.id} 
                           className="card-genora cursor-pointer hover:scale-102 transition-transform"
                           onClick={() => setSelectedStrategy(strategy)}>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            {(() => {
                              const pair = strategy.token_pair || strategy.name;
                              const icons = getTokenPairIcons(pair);
                              return icons ? (
                                <>
                                  <img src={icons.first} alt="" width={16} height={16} className="rounded" />
                                  <img src={icons.second} alt="" width={16} height={16} className="rounded" />
                                </>
                              ) : null;
                            })()}
                            <div>
                              <p className="font-orbitron text-sm font-semibold text-white">
                                {strategy.token_pair || strategy.name}
                              </p>
                              <p className="font-inter text-xs text-white/60">
                                {formatLabel(strategy.protocol)} • {formatLabel(strategy.chain)}
                              </p>
                            </div>
                          </div>
                          <div className="text-right">
                            <p className="font-spacemono text-sm font-bold text-[var(--profitGreen)]">
                              {formatPercent(strategy.apy)}
                            </p>
                            <p className="font-spacemono text-xs text-white/60">
                              {formatNumber(strategy.tvl_usd, 0)} $
                            </p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Show All Strategies Button */}
          {rows.length > 4 && (
            <div className="text-center mb-8">
              <button
                onClick={() => setShowAllStrategies(!showAllStrategies)}
                className="button-genora"
              >
                {showAllStrategies ? 'Hide All Strategies' : `Show All Strategies (${rows.length - 4} more)`}
              </button>
            </div>
          )}

          {/* All Strategies Table */}
          {showAllStrategies && (
            <StrategyTable
              strategies={rows}
              total={rows.length}
              onSelect={(item) => setSelectedStrategy(item)}
              getChainIconUrl={getChainIconUrl}
              getTokenPairIcons={getTokenPairIcons}
            />
          )}
        </>
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
  getTokenPairIcons,
}: {
  strategies: AggregatedStrategy[];
  total: number;
  onSelect: (strategy: AggregatedStrategy) => void;
  getChainIconUrl: (name: string) => string;
  getTokenPairIcons: (pair: string) => { first: string; second: string } | null;
}): JSX.Element {
  return (
    <div className="card-genora">
      <div className="flex justify-between items-center mb-6">
        <h3 className="font-orbitron text-xl font-bold text-[var(--neonAqua)]">
          Strategy Results
        </h3>
        <div className="font-spacemono text-sm text-white/60">
          Found: {total} strategies
        </div>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-white/10">
              <th className="text-left py-3 px-4 font-orbitron text-sm font-semibold text-[var(--neonAqua)]">Pair</th>
              <th className="text-left py-3 px-4 font-orbitron text-sm font-semibold text-[var(--neonAqua)]">Protocol</th>
              <th className="text-left py-3 px-4 font-orbitron text-sm font-semibold text-[var(--neonAqua)]">Chain</th>
              <th className="text-left py-3 px-4 font-orbitron text-sm font-semibold text-[var(--neonAqua)]">APY</th>
              <th className="text-left py-3 px-4 font-orbitron text-sm font-semibold text-[var(--neonAqua)]">TVL</th>
              <th className="text-left py-3 px-4 font-orbitron text-sm font-semibold text-[var(--neonAqua)]">TVL Growth 24h</th>
              <th className="text-left py-3 px-4 font-orbitron text-sm font-semibold text-[var(--neonAqua)]">Risk</th>
              <th className="text-left py-3 px-4 font-orbitron text-sm font-semibold text-[var(--neonAqua)]">AI Score</th>
              <th className="text-left py-3 px-4 font-orbitron text-sm font-semibold text-[var(--neonAqua)]">Link</th>
          </tr>
        </thead>
        <tbody>
          {strategies.map((strategy) => (
            <tr
              key={strategy.id}
              className="border-b border-white/5 hover:bg-white/5 cursor-pointer transition-colors"
              onClick={() => onSelect(strategy)}
              tabIndex={0}
              role="button"
              aria-label={`View strategy details: ${strategy.name}`}
              onKeyDown={(event) => {
                if (event.key === "Enter" || event.key === " ") {
                  event.preventDefault();
                  onSelect(strategy);
                }
              }}
            >
              <td className="py-4 px-4">
                <div className="flex items-center space-x-2">
                  {(() => {
                    const pair = strategy.token_pair || strategy.name;
                    const icons = getTokenPairIcons(pair);
                    
                    if (icons) {
                      return (
                        <>
                          <img 
                            src={icons.first} 
                            alt="" 
                            width={16} 
                            height={16} 
                            loading="lazy" 
                            onError={(e) => ((e.currentTarget.style.display = "none"))} 
                            className="rounded" 
                          />
                          <img 
                            src={icons.second} 
                            alt="" 
                            width={16} 
                            height={16} 
                            loading="lazy" 
                            onError={(e) => ((e.currentTarget.style.display = "none"))} 
                            className="rounded" 
                          />
                          <span className="font-orbitron text-sm font-semibold text-white">
                            {pair}
                          </span>
                        </>
                      );
                    }
                    
                    return (
                      <span className="font-orbitron text-sm font-semibold text-white">
                        {pair || "—"}
                      </span>
                    );
                  })()}
                </div>
              </td>
              <td className="py-4 px-4">
                <div className="flex items-center space-x-2">
                  {strategy.icon_url && (
                    <img src={strategy.icon_url} alt="" width={16} height={16} loading="lazy" onError={(e) => ((e.currentTarget.style.display = "none"))} className="rounded" />
                  )}
                  <span className="font-inter text-sm text-white">{formatLabel(strategy.protocol)}</span>
                </div>
              </td>
              <td className="py-4 px-4">
                <div className="flex items-center space-x-2">
                  <img src={getChainIconUrl(strategy.chain)} alt="" width={16} height={16} loading="lazy" onError={(e) => ((e.currentTarget.style.display = "none"))} className="rounded" />
                  <span className="font-inter text-sm text-white">{formatLabel(strategy.chain)}</span>
                </div>
              </td>
              <td className="py-4 px-4">
                <span className="font-spacemono text-sm font-bold text-[var(--profitGreen)]">{formatPercent(strategy.apy)}</span>
              </td>
              <td className="py-4 px-4">
                <span className="font-spacemono text-sm text-white">{formatNumber(strategy.tvl_usd, 2)} $</span>
              </td>
              <td className={`py-4 px-4 ${strategy.tvl_growth_24h >= 0 ? "text-[var(--profitGreen)]" : "text-red-400"}`}>
                <span className="font-spacemono text-sm font-medium">{formatPercent(strategy.tvl_growth_24h)}</span>
              </td>
              <td className="py-4 px-4">
                <span className="font-spacemono text-sm text-white">
                  {strategy.risk_index !== null ? strategy.risk_index.toFixed(2) : "—"}
                </span>
              </td>
              <td className="py-4 px-4">
                <span className="font-spacemono text-sm font-bold text-[var(--neonAqua)]">
                  {strategy.ai_score !== null && strategy.ai_score !== undefined ? strategy.ai_score.toFixed(2) : "—"}
                </span>
              </td>
              <td className="py-4 px-4">
                {strategy.url ? (
                  <a 
                    href={strategy.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="button-genora text-xs px-3 py-1"
                  >
                    Open
                  </a>
                ) : (
                  <span className="font-inter text-sm text-white/50">—</span>
                )}
              </td>
            </tr>
          ))}
          {strategies.length === 0 && (
            <tr>
              <td colSpan={9} className="py-8 text-center">
                <div className="font-inter text-white/60">
                  No matching strategies found. Try adjusting your filters.
                </div>
              </td>
            </tr>
          )}
        </tbody>
      </table>
      </div>
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