'use client';

interface AISuggestionsProps {
  strategies: any[];
}

export function AISuggestions({ strategies }: AISuggestionsProps) {
  const suggestions = [
    {
      id: '1',
      name: 'Compound USDC',
      apy: 8.5,
      risk: 'Low',
      reason: 'Stable yield with low volatility',
      chain: 'Ethereum',
      icon: '💰'
    },
    {
      id: '2',
      name: 'Uniswap V3 ETH/USDC',
      apy: 12.3,
      risk: 'Medium',
      reason: 'High liquidity with moderate risk',
      chain: 'Ethereum',
      icon: '🔄'
    },
    {
      id: '3',
      name: 'Aave USDT',
      apy: 6.8,
      risk: 'Low',
      reason: 'Conservative lending strategy',
      chain: 'Ethereum',
      icon: '💰'
    }
  ];

  return (
    <div className="card-genora mb-8">
      <h2 className="font-orbitron text-2xl font-bold text-[var(--neonAqua)] mb-6">
        AI Smart Suggestions
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {suggestions.map(suggestion => (
          <div key={suggestion.id} className="card-genora">
            <div className="flex justify-between items-start mb-3">
              <h3 className="font-orbitron text-lg font-semibold text-white">
                {suggestion.name}
              </h3>
              <span className={`px-2 py-1 rounded text-xs font-medium ${
                suggestion.risk === 'Low' ? 'bg-green-500/20 text-green-400' :
                suggestion.risk === 'Medium' ? 'bg-yellow-500/20 text-yellow-400' :
                'bg-red-500/20 text-red-400'
              }`}>
                {suggestion.risk}
              </span>
            </div>
            <div className="font-spacemono text-2xl font-bold text-[var(--profitGreen)] mb-2">
              {suggestion.apy}% APY
            </div>
            <p className="font-inter text-white/70 text-sm mb-2">{suggestion.reason}</p>
            <div className="font-inter text-white/50 text-xs">{suggestion.chain}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
