import type { StrategiesResponse, StrategyDetail } from "../components/home/types";

function toQuery(params: Record<string, string | number | boolean | null | undefined | Array<string | number>>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value === null || value === undefined || value === "") continue;
    if (Array.isArray(value)) {
      value.forEach((v) => search.append(key, String(v)));
    } else {
      search.set(key, String(value));
    }
  }
  return search.toString();
}

async function handleJsonResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let detail: string | undefined;
    try {
      const payload = await response.json();
      detail = payload?.detail ?? payload?.message;
    } catch {
      // ignore
    }
    throw new Error(detail || `Request failed with ${response.status}`);
  }
  return (await response.json()) as T;
}

export async function fetchChains(apiBaseUrl: string, signal?: AbortSignal): Promise<string[]> {
  const res = await fetch(`${apiBaseUrl}/chains`, { signal, cache: "no-store" });
  const data = await handleJsonResponse<{ items: string[] }>(res);
  return data.items ?? [];
}

export async function fetchProtocols(apiBaseUrl: string, signal?: AbortSignal): Promise<string[]> {
  const res = await fetch(`${apiBaseUrl}/protocols`, { signal, cache: "no-store" });
  const data = await handleJsonResponse<{ items: string[] }>(res);
  return data.items ?? [];
}

export type AggregatorQuery = {
  chain?: string | null;
  protocol?: string | null;
  min_tvl?: number | null;
  min_apy?: number | null;
  sort?: string | null;
  limit?: number | null;
  offset?: number | null;
};

export async function fetchAggregatorStrategies(
  apiBaseUrl: string,
  query: AggregatorQuery,
  signal?: AbortSignal,
): Promise<StrategiesResponse> {
  const qs = toQuery({
    chain: query.chain ?? undefined,
    protocol: query.protocol ?? undefined,
    min_tvl: query.min_tvl ?? undefined,
    min_apy: query.min_apy ?? undefined,
    sort: query.sort ?? undefined,
    limit: query.limit ?? undefined,
    offset: query.offset ?? undefined,
  });
  const res = await fetch(`${apiBaseUrl}/strategies?${qs}`, { signal, cache: "no-store" });
  return handleJsonResponse<StrategiesResponse>(res);
}

export async function fetchStrategyDetails(
  apiBaseUrl: string,
  strategyId: string,
  signal?: AbortSignal,
): Promise<StrategyDetail> {
  // Декодируем ID, если он уже закодирован, чтобы избежать двойного кодирования
  let decodedId = strategyId;
  try {
    // Проверяем, закодирован ли ID (содержит %)
    if (strategyId.includes('%')) {
      decodedId = decodeURIComponent(strategyId);
    }
  } catch {
    // Если декодирование не удалось, используем оригинальный ID
    decodedId = strategyId;
  }
  
  // Кодируем ID только один раз
  const encodedId = encodeURIComponent(decodedId);
  const url = `${apiBaseUrl}/strategies/${encodedId}`;
  
  if (typeof window !== 'undefined') {
    console.log(`[API] Fetching strategy details: ${url}`);
    console.log(`[API] Original ID: ${strategyId}, Decoded: ${decodedId}, Encoded: ${encodedId}`);
  }
  
  const res = await fetch(url, { signal, cache: "no-store" });
  if (!res.ok) {
    const errorText = await res.text().catch(() => 'Unknown error');
    console.error(`[API] Strategy details error ${res.status}:`, errorText);
    throw new Error(`API error ${res.status}: ${errorText}`);
  }
  return res.json() as Promise<StrategyDetail>;
}

export type TokenListItem = { symbol: string; name?: string; slug?: string };

export async function fetchTopTokens(apiBaseUrl: string, limit = 100, signal?: AbortSignal): Promise<TokenListItem[]> {
  const res = await fetch(`${apiBaseUrl}/tokens?limit=${limit}`, { signal, cache: "no-store" });
  const data = await handleJsonResponse<{ tokens: TokenListItem[] }>(res);
  return data.tokens ?? [];
}

export type Timeframe = "24h" | "7d" | "30d" | "all";

export type AptosDexSummary = {
  name: string;
  slug: string;
  chain: string;
  tvl_usd: number;
  volume: Record<Timeframe, number>;
  fees: Record<Timeframe, number>;
};

export type AptosPoolSummary = {
  id: string;
  dex_slug: string;
  address: string;
  token0: string;
  token1: string;
  pair: string;
  fee_tier: number;
  tvl_usd: number;
  volume: Record<Timeframe, number>;
  fees: Record<Timeframe, number>;
  apr_fee: number;
};

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") || 
  process.env.NEXT_PUBLIC_API_URL || 
  "http://localhost:8000";

async function fetchJson<T>(path: string, params?: URLSearchParams): Promise<T> {
  const url = new URL(path, API_BASE);
  if (params) url.search = params.toString();
  const fullUrl = url.toString();
  if (typeof window !== 'undefined') {
    console.log(`[API] Fetching: ${fullUrl}`);
  }
  const res = await fetch(fullUrl, { cache: "no-store" });
  if (!res.ok) {
    const errorText = await res.text().catch(() => 'Unknown error');
    throw new Error(`API error ${res.status}: ${errorText}`);
  }
  return res.json();
}

export async function getAptosDexes(opts: {
  sortBy?: "tvl" | "volume" | "fees";
  timeframe?: Timeframe;
  minTvl?: number;
}): Promise<AptosDexSummary[]> {
  const params = new URLSearchParams();
  if (opts.sortBy) params.set("sort_by", opts.sortBy);
  if (opts.timeframe) params.set("timeframe", opts.timeframe);
  if (opts.minTvl !== undefined) params.set("min_tvl", String(opts.minTvl));
  return fetchJson<AptosDexSummary[]>("/aptos/dexes", params);
}

export async function getAptosPools(opts: {
  dex?: string;
  pair?: string;
  sortBy?: "tvl" | "volume" | "fees" | "apr";
  timeframe?: Timeframe;
  minTvl?: number;
  minApr?: number;
}): Promise<AptosPoolSummary[]> {
  const params = new URLSearchParams();
  if (opts.dex) params.set("dex", opts.dex);
  if (opts.pair) params.set("pair", opts.pair);
  if (opts.sortBy) params.set("sort_by", opts.sortBy);
  if (opts.timeframe) params.set("timeframe", opts.timeframe);
  if (opts.minTvl !== undefined) params.set("min_tvl", String(opts.minTvl));
  if (opts.minApr !== undefined) params.set("min_apr", String(opts.minApr));
  return fetchJson<AptosPoolSummary[]>("/aptos/pools", params);
}

export async function getAptosPoolById(poolId: string): Promise<AptosPoolSummary | null> {
  try {
    return await fetchJson<AptosPoolSummary>(`/aptos/pools/${poolId}`);
  } catch (error) {
    console.error("Failed to fetch pool:", error);
    return null;
  }
}

// Legacy functions (kept for backward compatibility)
export async function fetchAptosDexes(params: {
  sortBy?: "tvl" | "volume" | "fees";
  timeframe?: Timeframe;
  minTvl?: number;
  signal?: AbortSignal;
}): Promise<any[]> {
  const search = new URLSearchParams();
  if (params.sortBy) search.set("sort_by", params.sortBy);
  if (params.timeframe) search.set("timeframe", params.timeframe);
  if (params.minTvl !== undefined) search.set("min_tvl", String(params.minTvl));

  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ?? "http://localhost:8000";
  const res = await fetch(`${apiBaseUrl}/aptos/dexes?${search.toString()}`, { 
    signal: params.signal, 
    cache: "no-store" 
  });
  return handleJsonResponse<any[]>(res);
}

export async function fetchAptosPools(params: {
  dex?: string;
  pair?: string;
  sortBy?: "tvl" | "volume" | "fees" | "apr";
  timeframe?: Timeframe;
  minTvl?: number;
  signal?: AbortSignal;
}): Promise<any[]> {
  const search = new URLSearchParams();
  if (params.dex) search.set("dex", params.dex);
  if (params.pair) search.set("pair", params.pair);
  if (params.sortBy) search.set("sort_by", params.sortBy);
  if (params.timeframe) search.set("timeframe", params.timeframe);
  if (params.minTvl !== undefined) search.set("min_tvl", String(params.minTvl));

  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ?? "http://localhost:8000";
  const res = await fetch(`${apiBaseUrl}/aptos/pools?${search.toString()}`, { 
    signal: params.signal, 
    cache: "no-store" 
  });
  return handleJsonResponse<any[]>(res);
}
