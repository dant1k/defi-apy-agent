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
  minApy: "4",
  riskLevel: "средний" as RiskLevel,
  minTvl: "5",
  preferredChains: ["ethereum"],
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ?? "http://localhost:8000";

export default function HomePage(): JSX.Element {
  const [form, setForm] = useState(DEFAULT_FORM);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<ApiResponse | null>(null);
  const [isChainModalOpen, setChainModalOpen] = useState(false);
  const [isTokenModalOpen, setTokenModalOpen] = useState(false);
  const [tokenOptions, setTokenOptions] = useState<TokenOption[]>(FALLBACK_TOKENS);
  const [tokenQuery, setTokenQuery] = useState("");

  const preferredChains = useMemo(() => [...form.preferredChains], [form.preferredChains]);
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
      const minApy = parseFloat(form.minApy);
      const minTvl = parseFloat(form.minTvl);

      const payload = {
        token: form.token,
        preferences: {
          min_apy: Number.isFinite(minApy) ? minApy : 0,
          risk_level: form.riskLevel,
          min_tvl: Number.isFinite(minTvl) ? minTvl : 0,
          preferred_chains: preferredChains,
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

  return (
    <section className="page">
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
            <label htmlFor="minApy">Мин. APY (%)</label>
            <input
              id="minApy"
              type="number"
              inputMode="decimal"
              step="0.1"
              min="0"
              value={form.minApy}
              onChange={(e) => setForm((prev) => ({ ...prev, minApy: e.target.value }))}
            />
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

        <div className="grid-row">
          <div className="form-row">
            <label htmlFor="minTvl">Мин. TVL (млн USD)</label>
            <input
              id="minTvl"
              type="number"
              inputMode="decimal"
              min="0"
              step="0.1"
              value={form.minTvl}
              onChange={(e) => setForm((prev) => ({ ...prev, minTvl: e.target.value }))}
            />
          </div>
          <div className="form-row">
            <label>Предпочитаемые сети</label>
            <div className="multi-select">
              <button
                type="button"
                className="multiselect-trigger"
                onClick={() => setChainModalOpen(true)}
              >
                {preferredChains.length ? `Выбрано: ${preferredChains.length}` : "Выбрать сети"}
              </button>
              <ChipGroup
                items={preferredChains}
                onRemove={(value) =>
                  setForm((prev) => ({
                    ...prev,
                    preferredChains: prev.preferredChains.filter((item) => item !== value),
                  }))
                }
              />
            </div>
          </div>

        </div>

        <button className="submit" type="submit" disabled={isLoading}>
          {isLoading ? "Ищем стратегии..." : "Найти стратегии"}
        </button>
      </form>

      {error && <div className="error-card">⚠️ {error}</div>}

      {response && <ResultsCard response={response} />}

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
        title="Предпочитаемые сети"
        isOpen={isChainModalOpen}
        options={chainOptions}
        selected={preferredChains}
        onToggle={(value) =>
          setForm((prev) => ({
            ...prev,
            preferredChains: toggleSelection(prev.preferredChains, value),
          }))
        }
        onClose={() => setChainModalOpen(false)}
        onClear={() => setForm((prev) => ({ ...prev, preferredChains: [] }))}
      />
    </section>
  );
}

function toggleSelection(values: string[], rawValue: string): string[] {
  const value = rawValue.toLowerCase();
  return values.includes(value)
    ? values.filter((item) => item !== value)
    : [...values, value];
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
  onToggle: (value: string) => void;
  onClear: () => void;
  onClose: () => void;
};

function SelectionModal({
  title,
  isOpen,
  options,
  selected,
  onToggle,
  onClear,
  onClose,
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
        </div>
        <footer>
          <button type="button" className="outlined" onClick={onClear}>
            Сбросить
          </button>
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
