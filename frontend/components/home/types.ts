export type RiskLevel = "низкий" | "средний" | "высокий";

export type Strategy = {
  platform?: string;
  chain?: string;
  symbol?: string;
  tokens?: string[];
  apy?: number;
  apy_7d?: number | null;
  risk_level?: RiskLevel;
  risk_description?: string;
  lockup_days?: number;
  tvl_usd?: number;
  score?: number;
  pool_url?: string | null;
  protocol_url?: string | null;
  action_url?: string | null;
};

export type OkResponse = {
  status: "ok";
  token: string;
  best_strategy: Strategy;
  alternatives: Strategy[];
  all_strategies?: Strategy[];
  statistics?: { matched?: number; considered?: number };
  warnings?: string[];
};

export type EmptyResponse = {
  status: "empty";
  token?: string;
  warnings?: string[];
};

export type ErrorResponse = {
  status: "error";
  message: string;
  warnings?: string[];
};

export type ApiResponse = OkResponse | EmptyResponse | ErrorResponse;

export type TokenOption = {
  value: string;
  label: string;
  slug?: string;
};

export type StrategyCacheEntry = {
  data: ApiResponse;
  updatedAt: number;
};
