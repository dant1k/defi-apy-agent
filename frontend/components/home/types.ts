export type AggregatedStrategy = {
  id: string;
  name: string;
  protocol: string;
  chain: string;
  apy: number;
  tvl_usd: number;
  tvl_growth_24h: number;
  risk_index: number | null;
  score?: number | null;
  ai_score?: number | null;
  ai_comment?: string | null;
  token_pair?: string | null;
  url?: string | null;
  icon_url?: string | null;
  source?: string | null;
  updated_at?: string | null;
};

export type StrategiesResponse = {
  updated_at: string | null;
  total: number;
  limit: number;
  offset: number;
  items: AggregatedStrategy[];
};

export type FiltersState = {
  chain: string;
  protocol: string;
  token?: string;
  minTvl: number;
  minApy: number;
  sort: "ai_score_desc" | "apy_desc" | "tvl_desc" | "tvl_growth_desc";
};

export type TvlPoint = {
  t: string;
  v: number;
};

export type StrategyDetail = {
  strategy: AggregatedStrategy;
  history: TvlPoint[];
};
