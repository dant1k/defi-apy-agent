'use client';

import { useEffect, useState } from 'react';

interface Strategy {
  id: string;
  name: string;
  protocol: string;
  chain: string;
  apy: number;
  tvl_usd: number;
  risk_index: number;
  ai_score: number;
  ai_comment: string;
  token_pair: string;
  tvl_growth_24h: number;
}

export default function SimpleIntelligenceDashboard() {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Try different API URLs
        const apiUrls = [
          'http://localhost:8000',
          'http://127.0.0.1:8000',
          'http://0.0.0.0:8000'
        ];
        
        let success = false;
        for (const apiUrl of apiUrls) {
          try {
            console.log('Trying API URL:', apiUrl);
            const response = await fetch(`${apiUrl}/strategies?limit=10&sort=ai_score_desc`);
            
            if (response.ok) {
              const data = await response.json();
              console.log('Successfully loaded data:', data);
              setStrategies(data.items || []);
              success = true;
              break;
            } else {
              console.log('Failed with status:', response.status);
            }
          } catch (err) {
            console.log('Failed to connect to:', apiUrl, err);
          }
        }
        
        if (!success) {
          setError('Не удалось подключиться к API. Проверьте, что backend запущен на порту 8000.');
        }
        
      } catch (error) {
        console.error('Error loading data:', error);
        setError('Ошибка загрузки данных: ' + (error as Error).message);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  const formatTvl = (value: number) => {
    if (value >= 1000000000) {
      return `$${(value / 1000000000).toFixed(1)}B`;
    } else if (value >= 1000000) {
      return `$${(value / 1000000).toFixed(1)}M`;
    } else {
      return `$${(value / 1000).toFixed(0)}K`;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="text-center">
          <div className="text-4xl mb-4">🧠</div>
          <div className="text-xl text-cyan-400 mb-2">Genora Intelligence Dashboard</div>
          <div className="text-white/60">Загрузка данных...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="text-4xl mb-4">⚠️</div>
          <div className="text-xl text-red-400 mb-2">Ошибка подключения</div>
          <div className="text-white/60 mb-4">{error}</div>
          <button 
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-cyan-600 text-white rounded hover:bg-cyan-700"
          >
            Попробовать снова
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 to-fuchsia-500 bg-clip-text text-transparent mb-2">
            🧠 Genora Intelligence Dashboard
          </h1>
          <p className="text-white/60">AI-powered DeFi analytics with real-time data</p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-gradient-to-b from-black/70 to-black/40 border border-cyan-900/50 rounded-lg p-6">
            <div className="text-2xl font-bold text-cyan-400">{strategies.length}</div>
            <div className="text-white/60">Total Strategies</div>
          </div>
          <div className="bg-gradient-to-b from-black/70 to-black/40 border border-cyan-900/50 rounded-lg p-6">
            <div className="text-2xl font-bold text-fuchsia-400">
              {formatTvl(strategies.reduce((sum, s) => sum + s.tvl_usd, 0))}
            </div>
            <div className="text-white/60">Total TVL</div>
          </div>
          <div className="bg-gradient-to-b from-black/70 to-black/40 border border-cyan-900/50 rounded-lg p-6">
            <div className="text-2xl font-bold text-green-400">
              {strategies.length > 0 ? (strategies.reduce((sum, s) => sum + s.apy, 0) / strategies.length).toFixed(2) : 0}%
            </div>
            <div className="text-white/60">Average APY</div>
          </div>
          <div className="bg-gradient-to-b from-black/70 to-black/40 border border-cyan-900/50 rounded-lg p-6">
            <div className="text-2xl font-bold text-yellow-400">
              {strategies.length > 0 ? (strategies.reduce((sum, s) => sum + s.ai_score, 0) / strategies.length).toFixed(0) : 0}
            </div>
            <div className="text-white/60">Avg AI Score</div>
          </div>
        </div>

        {/* Top Strategies */}
        <div className="bg-gradient-to-b from-black/70 to-black/40 border border-cyan-900/50 rounded-lg p-6 mb-8">
          <h2 className="text-2xl font-bold text-cyan-400 mb-6">Top AI-Recommended Strategies</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {strategies.slice(0, 6).map((strategy) => (
              <div key={strategy.id} className="bg-black/40 border border-fuchsia-900/50 rounded-lg p-4">
                <div className="flex justify-between items-start mb-3">
                  <h3 className="text-lg font-semibold text-white">{strategy.protocol}</h3>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    strategy.risk_index < 3 ? 'bg-green-500/20 text-green-400' :
                    strategy.risk_index < 6 ? 'bg-yellow-500/20 text-yellow-400' :
                    'bg-red-500/20 text-red-400'
                  }`}>
                    Risk: {strategy.risk_index.toFixed(1)}
                  </span>
                </div>
                <div className="text-2xl font-bold text-fuchsia-400 mb-2">
                  {strategy.apy.toFixed(2)}% APY
                </div>
                <div className="text-sm text-white/70 mb-2">
                  {strategy.token_pair} • {strategy.chain}
                </div>
                <div className="text-sm text-cyan-300 mb-2">
                  TVL: {formatTvl(strategy.tvl_usd)}
                </div>
                <div className="text-xs text-white/50">
                  AI Score: {strategy.ai_score.toFixed(0)}/100
                </div>
                {strategy.ai_comment && (
                  <div className="text-xs text-white/60 mt-2 p-2 bg-black/20 rounded">
                    {strategy.ai_comment}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* API Info */}
        <div className="bg-gradient-to-b from-black/70 to-black/40 border border-cyan-900/50 rounded-lg p-6">
          <h2 className="text-xl font-bold text-cyan-400 mb-4">API Connection Status</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <div className="text-white/60">API URL:</div>
              <div className="text-white">http://localhost:8000</div>
            </div>
            <div>
              <div className="text-white/60">Status:</div>
              <div className="text-green-400">✅ Connected</div>
            </div>
            <div>
              <div className="text-white/60">Strategies Loaded:</div>
              <div className="text-white">{strategies.length}</div>
            </div>
            <div>
              <div className="text-white/60">Last Update:</div>
              <div className="text-white">{new Date().toLocaleString()}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
