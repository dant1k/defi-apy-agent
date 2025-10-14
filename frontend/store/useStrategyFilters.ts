import { create } from "zustand";
import { RiskLevel } from "../components/home/types";

export type SortOption = "apy" | "tvl" | "novelty";
export type GrowthFilter = "none" | "apy_growth_gt_5";

type StrategyFiltersState = {
  token: string;
  riskLevel: RiskLevel;
  includeWrappers: boolean;
  sortBy: SortOption;
  growthFilter: GrowthFilter;
  onlyNew: boolean;
  onlyTop: boolean;
  autoFetchEnabled: boolean;
  requestId: number;
  setToken: (token: string) => void;
  setRiskLevel: (riskLevel: RiskLevel) => void;
  setIncludeWrappers: (include: boolean) => void;
  toggleIncludeWrappers: () => void;
  setSortBy: (sort: SortOption) => void;
  setGrowthFilter: (filter: GrowthFilter) => void;
  setOnlyNew: (value: boolean) => void;
  setOnlyTop: (value: boolean) => void;
  setAutoFetchEnabled: (value: boolean) => void;
  triggerFetch: () => void;
};

export const useStrategyFilters = create<StrategyFiltersState>((set, get) => ({
  token: "ETH",
  riskLevel: "средний",
  includeWrappers: true,
  sortBy: "apy",
  growthFilter: "none",
  onlyNew: false,
  onlyTop: false,
  autoFetchEnabled: true,
  requestId: 0,
  setToken: (token: string) =>
    set((state) => {
      const normalized = token.trim().toUpperCase();
      return {
        token: normalized,
      requestId: state.autoFetchEnabled ? state.requestId + 1 : state.requestId,
      };
    }),
  setRiskLevel: (riskLevel: RiskLevel) =>
    set((state) => ({
      riskLevel,
      requestId: state.autoFetchEnabled ? state.requestId + 1 : state.requestId,
    })),
  setIncludeWrappers: (include: boolean) =>
    set((state) => ({
      includeWrappers: include,
      requestId: state.autoFetchEnabled ? state.requestId + 1 : state.requestId,
    })),
  toggleIncludeWrappers: () =>
    set((state) => {
      const next = !state.includeWrappers;
      return {
        includeWrappers: next,
        requestId: state.autoFetchEnabled ? state.requestId + 1 : state.requestId,
      };
    }),
  setSortBy: (sort: SortOption) =>
    set(() => ({
      sortBy: sort,
    })),
  setGrowthFilter: (filter: GrowthFilter) =>
    set(() => ({
      growthFilter: filter,
    })),
  setOnlyNew: (value: boolean) =>
    set(() => ({
      onlyNew: value,
    })),
  setOnlyTop: (value: boolean) =>
    set(() => ({
      onlyTop: value,
    })),
  setAutoFetchEnabled: (value: boolean) =>
    set((state) => ({
      autoFetchEnabled: value,
      requestId: value ? state.requestId + 1 : state.requestId,
    })),
  triggerFetch: () =>
    set((state) => ({
      requestId: state.requestId + 1,
    })),
}));
