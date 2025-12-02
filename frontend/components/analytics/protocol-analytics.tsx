'use client';

import { useState, useEffect } from 'react';

interface ProtocolData {
  name: string;
  tvl: number;
  apy: number;
  strategies: number;
  chains: string[];
  risk_score: number;
  growth_24h: number;
  growth_7d: number;
}

interface ProtocolAnalyticsProps {
  strategies: any[];
}

export function ProtocolAnalytics({ strategies }: ProtocolAnalyticsProps) {
  const [protocolData, setProtocolData] = useState<ProtocolData[]>([]);
  const [selectedProtocol, setSelectedProtocol] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState<'tvl' | 'apy' | 'strategies' | 'growth'>('tvl');

  useEffect(() => {
    if (!strategies || strategies.length === 0) return;

    // Group strategies by protocol
    const protocolMap = new Map<string, any[]>();
    strategies.forEach(strategy => {
      const protocol = strategy.protocol || 'Unknown';
      if (!protocolMap.has(protocol)) {
        protocolMap.set(protocol, []);
      }
      protocolMap.get(protocol)!.push(strategy);
    });

    // Calculate protocol metrics
    const protocols: ProtocolData[] = Array.from(protocolMap.entries()).map(([name, protocolStrategies]) => {
      const totalTvl = protocolStrategies.reduce((sum, s) => sum + (s.tvl_usd || 0), 0);
      const avgApy = protocolStrategies.reduce((sum, s) => sum + (s.apy || 0), 0) / protocolStrategies.length;
      const chains = [...new Set(protocolStrategies.map(s => s.chain).filter(Boolean))];
      const riskScore = protocolStrategies.reduce((sum, s) => sum + (s.risk_score || 0), 0) / protocolStrategies.length;
      
      // Mock growth data (in real app, this would come from historical data)
      const growth24h = Math.random() * 20 - 10; // -10% to +10%
      const growth7d = Math.random() * 50 - 25; // -25% to +25%

      return {
        name,
        tvl: totalTvl,
        apy: avgApy,
        strategies: protocolStrategies.length,
        chains,
        risk_score: riskScore,
        growth_24h: growth24h,
        growth_7d: growth7d
      };
    });

    // Sort protocols
    protocols.sort((a, b) => {
      switch (sortBy) {
        case 'tvl': return b.tvl - a.tvl;
        case 'apy': return b.apy - a.apy;
        case 'strategies': return b.strategies - a.strategies;
        case 'growth': return b.growth_24h - a.growth_24h;
        default: return b.tvl - a.tvl;
      }
    });

    setProtocolData(protocols);
  }, [strategies, sortBy]);

  const formatTvl = (tvl: number) => {
    if (tvl >= 1000000000) {
      return `$${(tvl / 1000000000).toFixed(1)}B`;
    } else if (tvl >= 1000000) {
      return `$${(tvl / 1000000).toFixed(1)}M`;
    } else {
      return `$${(tvl / 1000).toFixed(0)}K`;
    }
  };

  const getRiskColor = (risk: number) => {
    if (risk < 3) return 'text-green-400';
    if (risk < 6) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getGrowthColor = (growth: number) => {
    return growth >= 0 ? 'text-green-400' : 'text-red-400';
  };

  return (
    <div className="card-genora">
      <div className="flex justify-between items-center mb-6">
        <h2 className="font-orbitron text-2xl font-bold text-[var(--neonAqua)]">
          Protocol Analytics
        </h2>
        <div className="flex space-x-2">
          <select 
            value={sortBy} 
            onChange={(e) => setSortBy(e.target.value as any)}
            className="px-3 py-1 bg-[var(--graphiteGray)] border border-[var(--neonAqua)] rounded text-white text-sm"
          >
            <option value="tvl">Sort by TVL</option>
            <option value="apy">Sort by APY</option>
            <option value="strategies">Sort by Strategies</option>
            <option value="growth">Sort by Growth</option>
          </select>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-[var(--neonAqua)]/20">
              <th className="text-left py-3 px-4 font-orbitron text-[var(--neonAqua)]">Protocol</th>
              <th className="text-right py-3 px-4 font-orbitron text-[var(--neonAqua)]">TVL</th>
              <th className="text-right py-3 px-4 font-orbitron text-[var(--neonAqua)]">Avg APY</th>
              <th className="text-right py-3 px-4 font-orbitron text-[var(--neonAqua)]">Strategies</th>
              <th className="text-right py-3 px-4 font-orbitron text-[var(--neonAqua)]">Risk Score</th>
              <th className="text-right py-3 px-4 font-orbitron text-[var(--neonAqua)]">24h Growth</th>
              <th className="text-right py-3 px-4 font-orbitron text-[var(--neonAqua)]">7d Growth</th>
              <th className="text-center py-3 px-4 font-orbitron text-[var(--neonAqua)]">Chains</th>
            </tr>
          </thead>
          <tbody>
            {protocolData.slice(0, 20).map((protocol, index) => (
              <tr 
                key={protocol.name}
                className={`border-b border-white/10 hover:bg-[var(--neonAqua)]/5 cursor-pointer ${
                  selectedProtocol === protocol.name ? 'bg-[var(--neonAqua)]/10' : ''
                }`}
                onClick={() => setSelectedProtocol(selectedProtocol === protocol.name ? null : protocol.name)}
              >
                <td className="py-3 px-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-gradient-to-br from-[var(--neonAqua)] to-[var(--cyberViolet)] rounded-full flex items-center justify-center text-white font-bold text-sm">
                      {protocol.name.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <div className="font-spacemono font-semibold text-white">{protocol.name}</div>
                      <div className="text-xs text-white/60">#{index + 1}</div>
                    </div>
                  </div>
                </td>
                <td className="text-right py-3 px-4 font-spacemono text-white">
                  {formatTvl(protocol.tvl)}
                </td>
                <td className="text-right py-3 px-4 font-spacemono text-[var(--profitGreen)]">
                  {protocol.apy.toFixed(2)}%
                </td>
                <td className="text-right py-3 px-4 font-spacemono text-white">
                  {protocol.strategies}
                </td>
                <td className="text-right py-3 px-4">
                  <span className={`font-spacemono ${getRiskColor(protocol.risk_score)}`}>
                    {protocol.risk_score.toFixed(1)}
                  </span>
                </td>
                <td className="text-right py-3 px-4">
                  <span className={`font-spacemono ${getGrowthColor(protocol.growth_24h)}`}>
                    {protocol.growth_24h >= 0 ? '+' : ''}{protocol.growth_24h.toFixed(1)}%
                  </span>
                </td>
                <td className="text-right py-3 px-4">
                  <span className={`font-spacemono ${getGrowthColor(protocol.growth_7d)}`}>
                    {protocol.growth_7d >= 0 ? '+' : ''}{protocol.growth_7d.toFixed(1)}%
                  </span>
                </td>
                <td className="text-center py-3 px-4">
                  <div className="flex flex-wrap justify-center gap-1">
                    {protocol.chains.slice(0, 3).map(chain => (
                      <span 
                        key={chain}
                        className="px-2 py-1 bg-[var(--graphiteGray)] text-xs text-white rounded"
                      >
                        {chain}
                      </span>
                    ))}
                    {protocol.chains.length > 3 && (
                      <span className="px-2 py-1 bg-[var(--graphiteGray)] text-xs text-white/60 rounded">
                        +{protocol.chains.length - 3}
                      </span>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {selectedProtocol && (
        <div className="mt-6 p-4 bg-[var(--graphiteGray)] rounded-lg border border-[var(--neonAqua)]/20">
          <h3 className="font-orbitron text-lg font-semibold text-[var(--neonAqua)] mb-3">
            {selectedProtocol} Details
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-spacemono font-bold text-white">
                {protocolData.find(p => p.name === selectedProtocol)?.strategies || 0}
              </div>
              <div className="text-sm text-white/60">Total Strategies</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-spacemono font-bold text-[var(--profitGreen)]">
                {protocolData.find(p => p.name === selectedProtocol)?.apy.toFixed(2) || '0.00'}%
              </div>
              <div className="text-sm text-white/60">Average APY</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-spacemono font-bold text-white">
                {protocolData.find(p => p.name === selectedProtocol)?.chains.length || 0}
              </div>
              <div className="text-sm text-white/60">Supported Chains</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-spacemono font-bold text-white">
                {formatTvl(protocolData.find(p => p.name === selectedProtocol)?.tvl || 0)}
              </div>
              <div className="text-sm text-white/60">Total TVL</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
