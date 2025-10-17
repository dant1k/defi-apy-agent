'use client';

import { useState, useEffect } from 'react';
import { 
  LineChart, 
  Line, 
  AreaChart, 
  Area, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  ScatterChart,
  Scatter
} from 'recharts';

interface AdvancedChartsProps {
  strategies: any[];
}

export function AdvancedCharts({ strategies }: AdvancedChartsProps) {
  const [chartData, setChartData] = useState<any[]>([]);
  const [timeframe, setTimeframe] = useState<'24h' | '7d' | '30d'>('24h');
  const [chartType, setChartType] = useState<'line' | 'area' | 'bar' | 'pie' | 'scatter'>('line');

  useEffect(() => {
    if (!strategies || strategies.length === 0) return;

    // Generate mock historical data based on current strategies
    const generateHistoricalData = () => {
      const data = [];
      const days = timeframe === '24h' ? 24 : timeframe === '7d' ? 7 : 30;
      const intervals = timeframe === '24h' ? 24 : timeframe === '7d' ? 7 : 30;
      
      for (let i = 0; i < intervals; i++) {
        const baseTvl = strategies.reduce((sum, s) => sum + (s.tvl_usd || 0), 0);
        const baseApy = strategies.reduce((sum, s) => sum + (s.apy || 0), 0) / strategies.length;
        
        // Add some volatility to make it look realistic
        const tvlVariation = 0.8 + Math.random() * 0.4; // 80-120% of base
        const apyVariation = 0.9 + Math.random() * 0.2; // 90-110% of base
        
        data.push({
          time: timeframe === '24h' ? `${i}:00` : `Day ${i + 1}`,
          tvl: baseTvl * tvlVariation,
          apy: baseApy * apyVariation,
          strategies: strategies.length + Math.floor(Math.random() * 20 - 10),
          volume: baseTvl * tvlVariation * (0.1 + Math.random() * 0.2),
          timestamp: new Date(Date.now() - (intervals - i) * (timeframe === '24h' ? 3600000 : 86400000))
        });
      }
      
      return data;
    };

    setChartData(generateHistoricalData());
  }, [strategies, timeframe]);

  const formatTvl = (value: number) => {
    if (value >= 1000000000) {
      return `$${(value / 1000000000).toFixed(1)}B`;
    } else if (value >= 1000000) {
      return `$${(value / 1000000).toFixed(1)}M`;
    } else {
      return `$${(value / 1000).toFixed(0)}K`;
    }
  };

  const formatApy = (value: number) => {
    return `${value.toFixed(2)}%`;
  };

  const COLORS = ['#00F6FF', '#8B5CF6', '#10B981', '#F59E0B', '#EF4444'];

  const renderChart = () => {
    switch (chartType) {
      case 'line':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="time" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1F2937', 
                  border: '1px solid #374151',
                  borderRadius: '8px',
                  color: '#F9FAFB'
                }}
                formatter={(value: any, name: string) => [
                  name === 'tvl' ? formatTvl(value) : 
                  name === 'apy' ? formatApy(value) : 
                  name === 'volume' ? formatTvl(value) : value,
                  name.toUpperCase()
                ]}
              />
              <Line 
                type="monotone" 
                dataKey="tvl" 
                stroke="#00F6FF" 
                strokeWidth={3}
                dot={{ fill: '#00F6FF', strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6, stroke: '#00F6FF', strokeWidth: 2 }}
              />
              <Line 
                type="monotone" 
                dataKey="apy" 
                stroke="#8B5CF6" 
                strokeWidth={3}
                dot={{ fill: '#8B5CF6', strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6, stroke: '#8B5CF6', strokeWidth: 2 }}
              />
            </LineChart>
          </ResponsiveContainer>
        );

      case 'area':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <AreaChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="time" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1F2937', 
                  border: '1px solid #374151',
                  borderRadius: '8px',
                  color: '#F9FAFB'
                }}
                formatter={(value: any, name: string) => [
                  name === 'tvl' ? formatTvl(value) : 
                  name === 'apy' ? formatApy(value) : 
                  name === 'volume' ? formatTvl(value) : value,
                  name.toUpperCase()
                ]}
              />
              <Area 
                type="monotone" 
                dataKey="tvl" 
                stackId="1"
                stroke="#00F6FF" 
                fill="url(#tvlGradient)"
                strokeWidth={2}
              />
              <Area 
                type="monotone" 
                dataKey="volume" 
                stackId="2"
                stroke="#8B5CF6" 
                fill="url(#volumeGradient)"
                strokeWidth={2}
              />
              <defs>
                <linearGradient id="tvlGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#00F6FF" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#00F6FF" stopOpacity={0.1}/>
                </linearGradient>
                <linearGradient id="volumeGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0.1}/>
                </linearGradient>
              </defs>
            </AreaChart>
          </ResponsiveContainer>
        );

      case 'bar':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="time" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1F2937', 
                  border: '1px solid #374151',
                  borderRadius: '8px',
                  color: '#F9FAFB'
                }}
                formatter={(value: any, name: string) => [
                  name === 'tvl' ? formatTvl(value) : 
                  name === 'apy' ? formatApy(value) : 
                  name === 'volume' ? formatTvl(value) : value,
                  name.toUpperCase()
                ]}
              />
              <Bar dataKey="tvl" fill="#00F6FF" radius={[4, 4, 0, 0]} />
              <Bar dataKey="volume" fill="#8B5CF6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        );

      case 'pie':
        const pieData = [
          { name: 'Ethereum', value: strategies.filter(s => s.chain === 'Ethereum').length, color: '#627EEA' },
          { name: 'BSC', value: strategies.filter(s => s.chain === 'BSC').length, color: '#F3BA2F' },
          { name: 'Polygon', value: strategies.filter(s => s.chain === 'Polygon').length, color: '#8247E5' },
          { name: 'Arbitrum', value: strategies.filter(s => s.chain === 'Arbitrum').length, color: '#28A0F0' },
          { name: 'Other', value: strategies.filter(s => !['Ethereum', 'BSC', 'Polygon', 'Arbitrum'].includes(s.chain)).length, color: '#6B7280' }
        ].filter(item => item.value > 0);

        return (
          <ResponsiveContainer width="100%" height={400}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={120}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1F2937', 
                  border: '1px solid #374151',
                  borderRadius: '8px',
                  color: '#F9FAFB'
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        );

      case 'scatter':
        const scatterData = strategies.slice(0, 50).map(strategy => ({
          tvl: strategy.tvl_usd || 0,
          apy: strategy.apy || 0,
          risk: strategy.risk_score || 5,
          name: strategy.name
        }));

        return (
          <ResponsiveContainer width="100%" height={400}>
            <ScatterChart data={scatterData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis 
                type="number" 
                dataKey="tvl" 
                name="TVL" 
                stroke="#9CA3AF"
                tickFormatter={formatTvl}
              />
              <YAxis 
                type="number" 
                dataKey="apy" 
                name="APY" 
                stroke="#9CA3AF"
                tickFormatter={formatApy}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1F2937', 
                  border: '1px solid #374151',
                  borderRadius: '8px',
                  color: '#F9FAFB'
                }}
                formatter={(value: any, name: string) => [
                  name === 'tvl' ? formatTvl(value) : 
                  name === 'apy' ? formatApy(value) : value,
                  name.toUpperCase()
                ]}
                labelFormatter={(label) => `Strategy: ${label}`}
              />
              <Scatter 
                dataKey="apy" 
                fill="#00F6FF"
                r={6}
              />
            </ScatterChart>
          </ResponsiveContainer>
        );

      default:
        return null;
    }
  };

  return (
    <div className="card-genora">
      <div className="flex justify-between items-center mb-6">
        <h2 className="font-orbitron text-2xl font-bold text-[var(--neonAqua)]">
          Advanced Analytics Charts
        </h2>
        <div className="flex space-x-2">
          {(['24h', '7d', '30d'] as const).map((period) => (
            <button
              key={period}
              onClick={() => setTimeframe(period)}
              className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                timeframe === period
                  ? 'bg-[var(--neonAqua)] text-black'
                  : 'bg-[var(--graphiteGray)] text-white/70 hover:text-white'
              }`}
            >
              {period}
            </button>
          ))}
        </div>
      </div>

      <div className="flex justify-center mb-6">
        <div className="flex space-x-2 bg-[var(--graphiteGray)] p-1 rounded-lg">
          {(['line', 'area', 'bar', 'pie', 'scatter'] as const).map((type) => (
            <button
              key={type}
              onClick={() => setChartType(type)}
              className={`px-4 py-2 rounded text-sm font-medium transition-colors capitalize ${
                chartType === type
                  ? 'bg-[var(--neonAqua)] text-black'
                  : 'text-white/70 hover:text-white hover:bg-white/10'
              }`}
            >
              {type}
            </button>
          ))}
        </div>
      </div>

      <div className="bg-[var(--graphiteGray)] rounded-lg p-4">
        {renderChart()}
      </div>

      <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="text-center">
          <div className="text-2xl font-spacemono font-bold text-[var(--neonAqua)]">
            {chartData.length > 0 ? formatTvl(chartData[chartData.length - 1]?.tvl || 0) : '$0'}
          </div>
          <div className="text-sm text-white/60">Current TVL</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-spacemono font-bold text-[var(--profitGreen)]">
            {chartData.length > 0 ? formatApy(chartData[chartData.length - 1]?.apy || 0) : '0%'}
          </div>
          <div className="text-sm text-white/60">Average APY</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-spacemono font-bold text-white">
            {chartData.length > 0 ? chartData[chartData.length - 1]?.strategies || 0 : 0}
          </div>
          <div className="text-sm text-white/60">Active Strategies</div>
        </div>
      </div>
    </div>
  );
}
