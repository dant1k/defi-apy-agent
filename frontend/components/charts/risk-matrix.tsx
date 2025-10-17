'use client';

import { useState, useEffect } from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

interface RiskData {
  name: string;
  tvl: number;
  volatility: number;
  apy: number;
  risk: 'low' | 'medium' | 'high';
  protocol: string;
  chain: string;
}

interface RiskMatrixProps {
  strategies: any[];
}

// Mock data generator
function generateRiskData(strategies: any[]): RiskData[] {
  return strategies.slice(0, 20).map((strategy, index) => {
    const volatility = Math.random() * 30 + 5; // 5-35% volatility
    const tvl = strategy.tvl_usd || Math.random() * 5000000 + 100000;
    const apy = strategy.apy || Math.random() * 20 + 2;
    
    let risk: 'low' | 'medium' | 'high' = 'low';
    if (volatility > 20 || apy > 15) risk = 'high';
    else if (volatility > 12 || apy > 8) risk = 'medium';
    
    return {
      name: strategy.name || `Strategy ${index + 1}`,
      tvl,
      volatility,
      apy,
      risk,
      protocol: strategy.protocol || 'Unknown',
      chain: strategy.chain || 'Ethereum'
    };
  });
}

export function RiskMatrix({ strategies }: RiskMatrixProps) {
  const [data, setData] = useState<RiskData[]>([]);
  const [selectedRisk, setSelectedRisk] = useState<'all' | 'low' | 'medium' | 'high'>('all');

  useEffect(() => {
    setData(generateRiskData(strategies));
  }, [strategies]);

  const filteredData = selectedRisk === 'all' 
    ? data 
    : data.filter(item => item.risk === selectedRisk);

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'low': return '#48bb78';
      case 'medium': return '#ed8936';
      case 'high': return '#f56565';
      default: return '#a0aec0';
    }
  };

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="risk-tooltip">
          <h4>{data.name}</h4>
          <p><strong>Protocol:</strong> {data.protocol}</p>
          <p><strong>Chain:</strong> {data.chain}</p>
          <p><strong>APY:</strong> {data.apy.toFixed(2)}%</p>
          <p><strong>TVL:</strong> ${(data.tvl / 1000000).toFixed(1)}M</p>
          <p><strong>Volatility:</strong> {data.volatility.toFixed(1)}%</p>
          <p><strong>Risk:</strong> <span style={{ color: getRiskColor(data.risk) }}>{data.risk.toUpperCase()}</span></p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="risk-matrix">
      <div className="risk-header">
        <h3>Risk Matrix</h3>
        <div className="risk-filters">
          <button 
            className={`risk-filter ${selectedRisk === 'all' ? 'active' : ''}`}
            onClick={() => setSelectedRisk('all')}
          >
            All
          </button>
          <button 
            className={`risk-filter low ${selectedRisk === 'low' ? 'active' : ''}`}
            onClick={() => setSelectedRisk('low')}
          >
            Low Risk
          </button>
          <button 
            className={`risk-filter medium ${selectedRisk === 'medium' ? 'active' : ''}`}
            onClick={() => setSelectedRisk('medium')}
          >
            Medium Risk
          </button>
          <button 
            className={`risk-filter high ${selectedRisk === 'high' ? 'active' : ''}`}
            onClick={() => setSelectedRisk('high')}
          >
            High Risk
          </button>
        </div>
      </div>

      <div className="risk-chart-container">
        <ResponsiveContainer width="100%" height={400}>
          <ScatterChart data={filteredData}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(111, 165, 255, 0.1)" />
            <XAxis 
              type="number" 
              dataKey="volatility" 
              name="Volatility"
              stroke="#a0aec0"
              fontSize={12}
              label={{ value: 'Volatility (%)', position: 'insideBottom', offset: -5, style: { textAnchor: 'middle', fill: '#a0aec0' } }}
            />
            <YAxis 
              type="number" 
              dataKey="tvl" 
              name="TVL"
              stroke="#a0aec0"
              fontSize={12}
              tickFormatter={(value) => `$${(value / 1000000).toFixed(0)}M`}
              label={{ value: 'TVL (USD)', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle', fill: '#a0aec0' } }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Scatter dataKey="apy" fill="#6fa5ff">
              {filteredData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={getRiskColor(entry.risk)} />
              ))}
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
      </div>

      <div className="risk-legend">
        <div className="legend-item">
          <div className="legend-color" style={{ backgroundColor: '#48bb78' }}></div>
          <span>Low Risk (Stable, Proven)</span>
        </div>
        <div className="legend-item">
          <div className="legend-color" style={{ backgroundColor: '#ed8936' }}></div>
          <span>Medium Risk (Moderate Volatility)</span>
        </div>
        <div className="legend-item">
          <div className="legend-color" style={{ backgroundColor: '#f56565' }}></div>
          <span>High Risk (High Volatility/Reward)</span>
        </div>
      </div>

      <div className="risk-insights">
        <h4>💡 AI Insights</h4>
        <div className="insights-grid">
          <div className="insight-card">
            <h5>Optimal Zone</h5>
            <p>Strategies in the green zone offer the best risk-adjusted returns with proven track records.</p>
          </div>
          <div className="insight-card">
            <h5>High Reward Zone</h5>
            <p>Orange and red dots represent higher potential returns but with increased volatility.</p>
          </div>
          <div className="insight-card">
            <h5>TVL Stability</h5>
            <p>Higher TVL generally indicates more stable and liquid strategies.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
