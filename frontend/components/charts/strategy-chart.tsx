'use client';

import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';

interface ChartData {
  timestamp: string;
  apy: number;
  tvl: number;
  date: string;
}

interface StrategyChartProps {
  strategyId: string;
  strategyName: string;
  type: 'apy' | 'tvl' | 'both';
}

// Mock data generator for demonstration
function generateMockData(strategyId: string): ChartData[] {
  const data: ChartData[] = [];
  const now = new Date();
  
  for (let i = 23; i >= 0; i--) {
    const date = new Date(now.getTime() - i * 60 * 60 * 1000); // Last 24 hours
    const baseAPY = 8 + Math.sin(i * 0.3) * 2 + Math.random() * 1;
    const baseTVL = 1000000 + Math.sin(i * 0.2) * 200000 + Math.random() * 100000;
    
    data.push({
      timestamp: date.toISOString(),
      apy: Math.max(0, baseAPY),
      tvl: Math.max(100000, baseTVL),
      date: date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
    });
  }
  
  return data;
}

export function StrategyChart({ strategyId, strategyName, type }: StrategyChartProps) {
  const [data, setData] = useState<ChartData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setData(generateMockData(strategyId));
      setLoading(false);
    }, 500);
  }, [strategyId]);

  if (loading) {
    return (
      <div className="chart-container">
        <div className="chart-loading">Loading chart...</div>
      </div>
    );
  }

  const formatValue = (value: number, type: string) => {
    if (type === 'apy') {
      return `${value.toFixed(2)}%`;
    }
    if (type === 'tvl') {
      if (value >= 1000000) {
        return `$${(value / 1000000).toFixed(1)}M`;
      }
      return `$${(value / 1000).toFixed(0)}K`;
    }
    return value.toString();
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="chart-tooltip">
          <p className="tooltip-time">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="tooltip-value" style={{ color: entry.color }}>
              {entry.dataKey === 'apy' ? 'APY' : 'TVL'}: {formatValue(entry.value, entry.dataKey)}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="strategy-chart">
      <div className="chart-header">
        <h4>{strategyName}</h4>
        <div className="chart-type-buttons">
          <button 
            className={`chart-btn ${type === 'apy' ? 'active' : ''}`}
            onClick={() => window.location.href = `?type=apy&id=${strategyId}`}
          >
            APY
          </button>
          <button 
            className={`chart-btn ${type === 'tvl' ? 'active' : ''}`}
            onClick={() => window.location.href = `?type=tvl&id=${strategyId}`}
          >
            TVL
          </button>
          <button 
            className={`chart-btn ${type === 'both' ? 'active' : ''}`}
            onClick={() => window.location.href = `?type=both&id=${strategyId}`}
          >
            Both
          </button>
        </div>
      </div>

      <div className="chart-container">
        <ResponsiveContainer width="100%" height={300}>
          {type === 'both' ? (
            <AreaChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(111, 165, 255, 0.1)" />
              <XAxis 
                dataKey="date" 
                stroke="#a0aec0"
                fontSize={12}
              />
              <YAxis 
                yAxisId="apy"
                orientation="left"
                stroke="#6fa5ff"
                fontSize={12}
                tickFormatter={(value) => `${value}%`}
              />
              <YAxis 
                yAxisId="tvl"
                orientation="right"
                stroke="#86f7ff"
                fontSize={12}
                tickFormatter={(value) => `$${(value / 1000000).toFixed(1)}M`}
              />
              <Tooltip content={<CustomTooltip />} />
              <Area
                yAxisId="apy"
                type="monotone"
                dataKey="apy"
                stroke="#6fa5ff"
                fill="rgba(111, 165, 255, 0.1)"
                strokeWidth={2}
              />
              <Area
                yAxisId="tvl"
                type="monotone"
                dataKey="tvl"
                stroke="#86f7ff"
                fill="rgba(134, 247, 255, 0.1)"
                strokeWidth={2}
              />
            </AreaChart>
          ) : (
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(111, 165, 255, 0.1)" />
              <XAxis 
                dataKey="date" 
                stroke="#a0aec0"
                fontSize={12}
              />
              <YAxis 
                stroke={type === 'apy' ? '#6fa5ff' : '#86f7ff'}
                fontSize={12}
                tickFormatter={(value) => formatValue(value, type)}
              />
              <Tooltip content={<CustomTooltip />} />
              <Line
                type="monotone"
                dataKey={type}
                stroke={type === 'apy' ? '#6fa5ff' : '#86f7ff'}
                strokeWidth={3}
                dot={{ fill: type === 'apy' ? '#6fa5ff' : '#86f7ff', strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6, stroke: type === 'apy' ? '#6fa5ff' : '#86f7ff', strokeWidth: 2 }}
              />
            </LineChart>
          )}
        </ResponsiveContainer>
      </div>

      <div className="chart-stats">
        <div className="stat">
          <span className="stat-label">Current {type.toUpperCase()}</span>
          <span className="stat-value">
            {formatValue(data[data.length - 1]?.[type] || 0, type)}
          </span>
        </div>
        <div className="stat">
          <span className="stat-label">24h Change</span>
          <span className={`stat-change ${data[data.length - 1]?.[type] > data[0]?.[type] ? 'positive' : 'negative'}`}>
            {data.length > 1 ? 
              `${((data[data.length - 1][type] - data[0][type]) / data[0][type] * 100).toFixed(2)}%` : 
              '0%'
            }
          </span>
        </div>
      </div>
    </div>
  );
}
