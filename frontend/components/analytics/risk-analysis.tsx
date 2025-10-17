'use client';

import { useState, useEffect } from 'react';

interface RiskMetrics {
  low: number;
  medium: number;
  high: number;
  total: number;
}

interface RiskAnalysisProps {
  strategies: any[];
}

export function RiskAnalysis({ strategies }: RiskAnalysisProps) {
  const [riskMetrics, setRiskMetrics] = useState<RiskMetrics>({ low: 0, medium: 0, high: 0, total: 0 });
  const [riskDistribution, setRiskDistribution] = useState<{ risk: string; count: number; percentage: number; tvl: number }[]>([]);
  const [selectedRisk, setSelectedRisk] = useState<string | null>(null);

  useEffect(() => {
    if (!strategies || strategies.length === 0) return;

    // Calculate risk distribution
    const riskCounts = { low: 0, medium: 0, high: 0 };
    const riskTvl = { low: 0, medium: 0, high: 0 };

    strategies.forEach(strategy => {
      const riskScore = strategy.risk_score || 5; // Default to medium risk
      const tvl = strategy.tvl_usd || 0;
      
      if (riskScore < 3) {
        riskCounts.low++;
        riskTvl.low += tvl;
      } else if (riskScore < 7) {
        riskCounts.medium++;
        riskTvl.medium += tvl;
      } else {
        riskCounts.high++;
        riskTvl.high += tvl;
      }
    });

    const total = strategies.length;
    setRiskMetrics({ ...riskCounts, total });

    // Create distribution data
    const distribution = [
      {
        risk: 'Low Risk',
        count: riskCounts.low,
        percentage: (riskCounts.low / total) * 100,
        tvl: riskTvl.low,
        color: 'text-green-400',
        bgColor: 'bg-green-400/20',
        borderColor: 'border-green-400/50'
      },
      {
        risk: 'Medium Risk',
        count: riskCounts.medium,
        percentage: (riskCounts.medium / total) * 100,
        tvl: riskTvl.medium,
        color: 'text-yellow-400',
        bgColor: 'bg-yellow-400/20',
        borderColor: 'border-yellow-400/50'
      },
      {
        risk: 'High Risk',
        count: riskCounts.high,
        percentage: (riskCounts.high / total) * 100,
        tvl: riskTvl.high,
        color: 'text-red-400',
        bgColor: 'bg-red-400/20',
        borderColor: 'border-red-400/50'
      }
    ];

    setRiskDistribution(distribution);
  }, [strategies]);

  const formatTvl = (tvl: number) => {
    if (tvl >= 1000000000) {
      return `$${(tvl / 1000000000).toFixed(1)}B`;
    } else if (tvl >= 1000000) {
      return `$${(tvl / 1000000).toFixed(1)}M`;
    } else {
      return `$${(tvl / 1000).toFixed(0)}K`;
    }
  };

  const getRiskIcon = (risk: string) => {
    switch (risk) {
      case 'Low Risk': return '🟢';
      case 'Medium Risk': return '🟡';
      case 'High Risk': return '🔴';
      default: return '⚪';
    }
  };

  const getRiskDescription = (risk: string) => {
    switch (risk) {
      case 'Low Risk': return 'Conservative strategies with stable returns';
      case 'Medium Risk': return 'Balanced strategies with moderate volatility';
      case 'High Risk': return 'Aggressive strategies with high potential returns';
      default: return '';
    }
  };

  return (
    <div className="card-genora">
      <div className="flex justify-between items-center mb-6">
        <h2 className="font-orbitron text-2xl font-bold text-[var(--neonAqua)]">
          Risk Analysis
        </h2>
        <div className="text-sm text-white/60">
          Based on {riskMetrics.total} strategies
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {riskDistribution.map((item, index) => (
          <div 
            key={index}
            className={`card-genora cursor-pointer transition-all duration-200 hover:scale-105 ${
              selectedRisk === item.risk ? 'ring-2 ring-[var(--neonAqua)]' : ''
            }`}
            onClick={() => setSelectedRisk(selectedRisk === item.risk ? null : item.risk)}
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <span className="text-2xl">{getRiskIcon(item.risk)}</span>
                <h3 className="font-orbitron text-lg font-semibold text-white">
                  {item.risk}
                </h3>
              </div>
              <div className={`text-2xl font-spacemono font-bold ${item.color}`}>
                {item.percentage.toFixed(1)}%
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="font-spacemono text-2xl font-bold text-white">
                  {item.count}
                </span>
                <span className="text-sm text-white/60">strategies</span>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="font-spacemono text-lg font-semibold text-white">
                  {formatTvl(item.tvl)}
                </span>
                <span className="text-sm text-white/60">TVL</span>
              </div>

              <div className="w-full bg-[var(--graphiteGray)] rounded-full h-2">
                <div 
                  className={`h-2 rounded-full transition-all duration-500 ${item.bgColor.replace('/20', '')}`}
                  style={{ width: `${item.percentage}%` }}
                ></div>
              </div>

              <p className="text-xs text-white/60 mt-2">
                {getRiskDescription(item.risk)}
              </p>
            </div>
          </div>
        ))}
      </div>

      {selectedRisk && (
        <div className="mt-6 p-4 bg-[var(--graphiteGray)] rounded-lg border border-[var(--neonAqua)]/20">
          <h3 className="font-orbitron text-lg font-semibold text-[var(--neonAqua)] mb-3">
            {selectedRisk} Strategies Details
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-spacemono font-bold text-white">
                {riskDistribution.find(r => r.risk === selectedRisk)?.count || 0}
              </div>
              <div className="text-sm text-white/60">Total Strategies</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-spacemono font-bold text-white">
                {formatTvl(riskDistribution.find(r => r.risk === selectedRisk)?.tvl || 0)}
              </div>
              <div className="text-sm text-white/60">Total TVL</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-spacemono font-bold text-white">
                {riskDistribution.find(r => r.risk === selectedRisk)?.percentage.toFixed(1) || '0.0'}%
              </div>
              <div className="text-sm text-white/60">Market Share</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-spacemono font-bold text-white">
                {formatTvl((riskDistribution.find(r => r.risk === selectedRisk)?.tvl || 0) / (riskDistribution.find(r => r.risk === selectedRisk)?.count || 1))}
              </div>
              <div className="text-sm text-white/60">Avg TVL per Strategy</div>
            </div>
          </div>
        </div>
      )}

      <div className="mt-6 p-4 bg-[var(--graphiteGray)] rounded-lg border border-[var(--neonAqua)]/20">
        <h3 className="font-orbitron text-lg font-semibold text-[var(--neonAqua)] mb-3">
          Risk Assessment Summary
        </h3>
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="font-inter text-white/80">Overall Risk Level</span>
            <span className={`font-spacemono font-semibold ${
              riskMetrics.low > riskMetrics.high ? 'text-green-400' : 
              riskMetrics.high > riskMetrics.low ? 'text-red-400' : 'text-yellow-400'
            }`}>
              {riskMetrics.low > riskMetrics.high ? 'Low' : 
               riskMetrics.high > riskMetrics.low ? 'High' : 'Medium'}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="font-inter text-white/80">Diversification Score</span>
            <span className="font-spacemono font-semibold text-white">
              {Math.min(100, Math.max(0, 100 - Math.abs(riskMetrics.low - riskMetrics.high) * 10))}%
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="font-inter text-white/80">Risk-Adjusted Returns</span>
            <span className="font-spacemono font-semibold text-[var(--profitGreen)]">
              {riskMetrics.low > riskMetrics.high ? 'High' : 
               riskMetrics.high > riskMetrics.low ? 'Low' : 'Medium'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
