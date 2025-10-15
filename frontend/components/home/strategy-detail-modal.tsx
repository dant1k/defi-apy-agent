import { useEffect, useMemo, useState } from "react";
import { fetchStrategyDetails } from "../../lib/api";
import type { AggregatedStrategy, StrategyDetail, TvlPoint } from "./types";
import { formatLabel, formatNumber, formatPercent } from "./formatters";

const CHART_WIDTH = 360;
const CHART_HEIGHT = 180;

type StrategyDetailModalProps = {
  apiBaseUrl: string;
  strategy: AggregatedStrategy;
  onClose: () => void;
};

export function StrategyDetailModal({ apiBaseUrl, strategy, onClose }: StrategyDetailModalProps): JSX.Element {
  const [details, setDetails] = useState<StrategyDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    async function loadDetails() {
      try {
        const payload = await fetchStrategyDetails(apiBaseUrl, strategy.id, controller.signal);
        setDetails(payload);
      } catch (err) {
        if (!controller.signal.aborted) {
          const message = err instanceof Error ? err.message : "Не удалось загрузить детали";
          setError(message);
        }
      }
    }
    loadDetails();
    return () => controller.abort();
  }, [apiBaseUrl, strategy.id]);

  const history = details?.history ?? [];
  const chartPath = useMemo(() => buildChartPath(history), [history]);
  const isLoadingDetails = !details && !error;

  return (
    <div className="modal-backdrop" role="dialog" aria-modal="true">
      <div className="modal strategy-detail-modal">
        <header className="modal-header">
          <div>
            <h3>{strategy.name}</h3>
            <p>
              {formatLabel(strategy.protocol)} · {formatLabel(strategy.chain)} · {strategy.token_pair}
            </p>
          </div>
          <button type="button" onClick={onClose} aria-label="Закрыть">
            ×
          </button>
        </header>

        {error && <div className="error-card">⚠️ {error}</div>}

        <section className="detail-grid">
          <div>
            <span className="metric-label">APY</span>
            <span className="metric-value big">{formatPercent(strategy.apy)}</span>
          </div>
          <div>
            <span className="metric-label">TVL</span>
            <span className="metric-value big">{formatNumber(strategy.tvl_usd, 0)} $</span>
          </div>
          <div>
            <span className="metric-label">Рост TVL 24ч</span>
            <span className={`metric-value ${strategy.tvl_growth_24h >= 0 ? "positive" : "negative"}`}>
              {formatPercent(strategy.tvl_growth_24h)}
            </span>
          </div>
          <div>
            <span className="metric-label">AI Score</span>
            <span className="metric-value big">
              {strategy.ai_score !== null && strategy.ai_score !== undefined ? strategy.ai_score.toFixed(2) : "—"}
            </span>
          </div>
        </section>

        {strategy.ai_comment && <div className="ai-comment-box">🤖 {strategy.ai_comment}</div>}

        <section className="detail-chart">
          <h4>TVL за последние 24 часа</h4>
          {isLoadingDetails ? (
            <p className="muted">Загружаем историю TVL…</p>
          ) : history.length > 1 ? (
            <svg viewBox={`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`} width="100%" height="160">
              <defs>
                <linearGradient id="tvlGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#86f7ff" stopOpacity="0.45" />
                  <stop offset="100%" stopColor="#86f7ff" stopOpacity="0" />
                </linearGradient>
              </defs>
              <path d={chartPath.area} fill="url(#tvlGradient)" />
              <path d={chartPath.line} fill="none" stroke="#86f7ff" strokeWidth={2} strokeLinejoin="round" />
              {chartPath.points.map((point) => (
                <circle key={point.key} cx={point.x} cy={point.y} r={2.2} fill="#86f7ff" />
              ))}
            </svg>
          ) : (
            <p className="muted">Недостаточно данных для графика.</p>
          )}
        </section>

        {strategy.url && (
          <a className="strategy-cta" href={strategy.url} target="_blank" rel="noopener noreferrer">
            Перейти к стратегии
          </a>
        )}
      </div>
    </div>
  );
}

function buildChartPath(history: TvlPoint[]): {
  line: string;
  area: string;
  points: Array<{ key: string; x: number; y: number }>;
} {
  if (history.length === 0) {
    return { line: "", area: "", points: [] };
  }
  const values = history.map((item) => Number(item.v) || 0);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = Math.max(max - min, 1);
  const horizontalPadding = 14;
  const verticalPadding = 16;
  const width = CHART_WIDTH - horizontalPadding * 2;
  const height = CHART_HEIGHT - verticalPadding * 2;

  const points = history.map((item, index) => {
    const value = Number(item.v) || 0;
    const normalized = (value - min) / range;
    const x = horizontalPadding + (history.length > 1 ? (index / (history.length - 1)) * width : width / 2);
    const y = verticalPadding + (1 - normalized) * height;
    return {
      key: `${item.t}-${index}`,
      x,
      y,
    };
  });

  const linePath = points
    .map((point, index) => `${index === 0 ? "M" : "L"} ${point.x.toFixed(2)} ${point.y.toFixed(2)}`)
    .join(" ");
  const baseY = verticalPadding + height;
  const areaPath = `${linePath} L ${points[points.length - 1].x.toFixed(2)} ${baseY.toFixed(2)} L ${points[0].x.toFixed(2)} ${baseY.toFixed(2)} Z`;

  return { line: linePath, area: areaPath, points };
}
