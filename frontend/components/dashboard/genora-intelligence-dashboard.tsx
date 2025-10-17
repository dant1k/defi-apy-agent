'use client';

// Simple Card components
const Card = ({ children, className = "" }: { children: React.ReactNode; className?: string }) => (
  <div className={`bg-gradient-to-b from-black/70 to-black/40 border border-cyan-900/50 shadow-[0_0_30px_-10px_rgba(34,211,238,0.5)] rounded-lg ${className}`}>
    {children}
  </div>
);

const CardHeader = ({ children, className = "" }: { children: React.ReactNode; className?: string }) => (
  <div className={`p-6 pb-0 ${className}`}>
    {children}
  </div>
);

const CardTitle = ({ children, className = "" }: { children: React.ReactNode; className?: string }) => (
  <h3 className={`text-lg font-semibold ${className}`}>
    {children}
  </h3>
);

const CardContent = ({ children, className = "" }: { children: React.ReactNode; className?: string }) => (
  <div className={`p-6 pt-0 ${className}`}>
    {children}
  </div>
);

const Button = ({ children, className = "", onClick, ...props }: { children: React.ReactNode; className?: string; onClick?: () => void; [key: string]: any }) => (
  <button 
    className={`px-4 py-2 rounded font-medium transition-colors ${className}`}
    onClick={onClick}
    {...props}
  >
    {children}
  </button>
);
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, AreaChart, Area, BarChart, Bar } from "recharts";
import { motion, useMotionValue, useTransform } from "framer-motion";
import { useEffect, useState, useRef } from "react";
import { Sparkles, TrendingUp, TrendingDown, Activity, Zap } from "lucide-react";

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

interface MarketInsights {
  timeframe: string;
  total_strategies: number;
  total_tvl: number;
  average_apy: number;
  top_protocols: Array<{
    protocol: string;
    count: number;
    total_tvl: number;
  }>;
  top_chains: Array<{
    chain: string;
    count: number;
    total_tvl: number;
  }>;
  market_trends: {
    apy_trend: string;
    tvl_trend: string;
    new_strategies: number;
    dominant_chains: string[];
  };
  ai_insights: string[];
}

export default function GenoraIntelligenceDashboard() {
  const [loading, setLoading] = useState(true);
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [marketInsights, setMarketInsights] = useState<MarketInsights | null>(null);
  const [selectedTimeframe, setSelectedTimeframe] = useState('24h');
  const [chartType, setChartType] = useState<'line' | 'area' | 'bar'>('line');
  const audioRef = useRef(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        // Load strategies
        const strategiesResponse = await fetch('http://localhost:8000/strategies?limit=50&sort=ai_score_desc');
        const strategiesData = await strategiesResponse.json();
        setStrategies(strategiesData.items || []);

        // Load market insights
        const insightsResponse = await fetch('http://localhost:8000/mcp/market-insights');
        const insightsData = await insightsResponse.json();
        setMarketInsights(insightsData);

        setLoading(false);
      } catch (error) {
        console.error('Failed to load data:', error);
        setLoading(false);
      }
    };

    const timer = setTimeout(() => {
      loadData();
    }, 2000);

    const audio = new Audio('/sounds/mystic_pulse.mp3');
    audio.volume = 0.3;
    audio.play().catch(() => {});
    audioRef.current = audio;

    return () => {
      clearTimeout(timer);
      if (audioRef.current) {
        audioRef.current.pause();
      }
    };
  }, []);

  const playHoverResonance = () => {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(440, ctx.currentTime);
    gain.gain.setValueAtTime(0.05, ctx.currentTime);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.6);
    osc.stop(ctx.currentTime + 0.6);
  };

  const glowPulse = {
    initial: { opacity: 0.6, scale: 1 },
    animate: { opacity: [0.6, 1, 0.6], scale: [1, 1.05, 1] },
    transition: { duration: 3, repeat: Infinity }
  };

  const plasmaStream = {
    initial: { x: "-10%", opacity: 0 },
    animate: { x: ["-10%", "110%"], opacity: [0.3, 0.8, 0.3] },
    transition: { duration: 8, repeat: Infinity, ease: "linear" }
  };

  // 3D parallax grid background
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);
  const rotateX = useTransform(mouseY, [0, 1], [10, -10]);
  const rotateY = useTransform(mouseX, [0, 1], [-10, 10]);

  useEffect(() => {
    const handleMouseMove = (e) => {
      mouseX.set(e.clientX / window.innerWidth);
      mouseY.set(e.clientY / window.innerHeight);
    };
    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, [mouseX, mouseY]);

  // Generate chart data from real strategies
  const generateChartData = () => {
    if (!strategies.length) return [];
    
    const topStrategies = strategies.slice(0, 7);
    return topStrategies.map((strategy, index) => ({
      name: strategy.protocol.substring(0, 4),
      apy: strategy.apy,
      tvl: strategy.tvl_usd / 1000000, // Convert to millions
      risk: strategy.risk_index,
      ai_score: strategy.ai_score
    }));
  };

  const formatTvl = (value: number) => {
    if (value >= 1000000000) {
      return `$${(value / 1000000000).toFixed(1)}B`;
    } else if (value >= 1000000) {
      return `$${(value / 1000000).toFixed(1)}M`;
    } else {
      return `$${(value / 1000).toFixed(0)}K`;
    }
  };

  const getTopStrategies = () => {
    return strategies.slice(0, 3);
  };

  const getRiskColor = (risk: number) => {
    if (risk < 3) return 'text-green-400';
    if (risk < 6) return 'text-yellow-400';
    return 'text-red-400';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-black overflow-hidden relative">
        <motion.div
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: [0, 1, 0.8, 1], scale: [0.5, 1.2, 1] }}
          transition={{ duration: 3, ease: "easeInOut" }}
          className="relative"
        >
          <Sparkles className="text-cyan-400 w-24 h-24 animate-pulse drop-shadow-[0_0_20px_#22d3ee]" />
          <motion.div
            className="absolute inset-0 rounded-full bg-gradient-to-r from-cyan-500/40 to-fuchsia-500/40 blur-3xl"
            animate={{ scale: [1, 1.3, 1], opacity: [0.6, 0.9, 0.6] }}
            transition={{ duration: 4, repeat: Infinity }}
          />
        </motion.div>
      </div>
    );
  }

  const chartData = generateChartData();
  const topStrategies = getTopStrategies();

  return (
    <div className="min-h-screen bg-black text-white font-satoshi p-6 grid grid-cols-12 gap-6 relative overflow-hidden">
      {/* Animated 3D neural grid background */}
      <motion.div
        style={{ rotateX, rotateY }}
        className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(34,211,238,0.15)_0%,transparent_70%)] opacity-60"
      >
        <motion.div
          animate={{ backgroundPosition: ["0% 0%", "100% 100%", "0% 0%"] }}
          transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
          className="absolute inset-0 bg-[linear-gradient(45deg,rgba(34,211,238,0.2)_1px,transparent_1px),linear-gradient(-45deg,rgba(217,70,239,0.2)_1px,transparent_1px)] bg-[length:80px_80px] blur-sm"
        />
      </motion.div>

      {/* Plasma streams */}
      <motion.div {...plasmaStream} className="absolute top-1/3 left-0 h-[2px] w-[40%] bg-gradient-to-r from-cyan-500/0 via-cyan-500/70 to-transparent blur-md" />
      <motion.div {...plasmaStream} transition={{ ...plasmaStream.transition, duration: 10, delay: 2 }} className="absolute top-2/3 left-0 h-[2px] w-[50%] bg-gradient-to-r from-fuchsia-500/0 via-fuchsia-500/70 to-transparent blur-md" />
      <motion.div {...plasmaStream} transition={{ ...plasmaStream.transition, duration: 12, delay: 4 }} className="absolute top-1/2 left-0 h-[2px] w-[60%] bg-gradient-to-r from-cyan-400/0 via-fuchsia-500/50 to-transparent blur-md" />

      {/* Header */}
      <header className="col-span-12 flex justify-between items-center relative z-10">
        <motion.h1 {...glowPulse} className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-fuchsia-500 bg-clip-text text-transparent">
          GENORA Intelligence Dashboard
        </motion.h1>
        <div className="flex space-x-4">
          <Button 
            className="bg-gradient-to-r from-cyan-500 to-fuchsia-600 text-white border-none shadow-lg hover:opacity-80 transition-all"
            onClick={() => window.location.href = '/strategies'}
          >
            <Activity className="w-4 h-4 mr-2" />
            View All Strategies
          </Button>
          <Button 
            className="bg-gradient-to-r from-fuchsia-500 to-cyan-600 text-white border-none shadow-lg hover:opacity-80 transition-all"
            onClick={() => window.location.href = '/dashboard'}
          >
            <Zap className="w-4 h-4 mr-2" />
            AI Analytics
          </Button>
        </div>
      </header>

      {/* AI Feed */}
      <motion.div {...glowPulse} className="col-span-4 relative z-10">
        <Card className="bg-gradient-to-b from-black/70 to-black/40 border border-cyan-900/50 shadow-[0_0_30px_-10px_rgba(34,211,238,0.5)]">
          <CardHeader>
            <CardTitle className="text-cyan-400 flex items-center">
              <Sparkles className="w-5 h-5 mr-2" />
              AI Feed
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            {marketInsights?.ai_insights.map((insight, index) => (
              <motion.div 
                key={index}
                animate={{ opacity: [0.6, 1, 0.6] }} 
                transition={{ duration: 4, repeat: Infinity, delay: index * 0.5 }}
                className="p-2 bg-cyan-500/10 rounded border border-cyan-500/20"
              >
                🤖 {insight}
              </motion.div>
            ))}
            {topStrategies.map((strategy, index) => (
              <motion.div 
                key={strategy.id}
                animate={{ opacity: [1, 0.7, 1] }} 
                transition={{ duration: 3, repeat: Infinity, delay: index * 0.3 }}
                className="text-fuchsia-300 p-2 bg-fuchsia-500/10 rounded border border-fuchsia-500/20"
              >
                📈 {strategy.protocol}: {strategy.apy.toFixed(2)}% APY (Risk: {strategy.risk_index.toFixed(1)})
              </motion.div>
            ))}
          </CardContent>
        </Card>
      </motion.div>

      {/* Strategy Map */}
      <motion.div {...glowPulse} className="col-span-8 relative z-10">
        <Card className="bg-gradient-to-b from-black/70 to-black/40 border border-fuchsia-900/50 shadow-[0_0_30px_-10px_rgba(217,70,239,0.5)]">
          <CardHeader>
            <CardTitle className="text-fuchsia-400 flex items-center justify-between">
              <span>Strategy Performance Map</span>
              <div className="flex space-x-2">
                {(['line', 'area', 'bar'] as const).map((type) => (
                  <Button
                    key={type}
                    size="sm"
                    variant={chartType === type ? "default" : "outline"}
                    onClick={() => setChartType(type)}
                    className={chartType === type ? "bg-fuchsia-600" : "border-fuchsia-500/50"}
                  >
                    {type}
                  </Button>
                ))}
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              {chartType === 'line' && (
                <LineChart data={chartData}>
                  <XAxis dataKey="name" stroke="#666" />
                  <YAxis stroke="#666" />
                  <Tooltip contentStyle={{ backgroundColor: '#0a0a0a', border: '1px solid #22d3ee' }} />
                  <Line type="monotone" dataKey="apy" stroke="#22d3ee" strokeWidth={2} dot={{ fill: '#d946ef' }} />
                </LineChart>
              )}
              {chartType === 'area' && (
                <AreaChart data={chartData}>
                  <XAxis dataKey="name" stroke="#666" />
                  <YAxis stroke="#666" />
                  <Tooltip contentStyle={{ backgroundColor: '#0a0a0a', border: '1px solid #22d3ee' }} />
                  <Area type="monotone" dataKey="apy" stroke="#22d3ee" fill="url(#apyGradient)" />
                  <defs>
                    <linearGradient id="apyGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#22d3ee" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="#22d3ee" stopOpacity={0.1}/>
                    </linearGradient>
                  </defs>
                </AreaChart>
              )}
              {chartType === 'bar' && (
                <BarChart data={chartData}>
                  <XAxis dataKey="name" stroke="#666" />
                  <YAxis stroke="#666" />
                  <Tooltip contentStyle={{ backgroundColor: '#0a0a0a', border: '1px solid #22d3ee' }} />
                  <Bar dataKey="apy" fill="#d946ef" radius={[4, 4, 0, 0]} />
                </BarChart>
              )}
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </motion.div>

      {/* Market Overview */}
      <motion.div {...glowPulse} className="col-span-4 relative z-10">
        <Card className="bg-gradient-to-b from-black/70 to-black/40 border border-cyan-900/50 shadow-[0_0_25px_-8px_rgba(34,211,238,0.5)]">
          <CardHeader>
            <CardTitle className="text-cyan-400">Market Overview</CardTitle>
          </CardHeader>
          <CardContent className="text-sm space-y-2">
            {marketInsights?.top_chains.slice(0, 3).map((chain, index) => (
              <p key={index}>
                {chain.chain}: {formatTvl(chain.total_tvl)} ({chain.count} strategies)
              </p>
            ))}
            <motion.p animate={{ color: ["#22d3ee", "#d946ef", "#22d3ee"] }} transition={{ duration: 5, repeat: Infinity }}>
              Total TVL: {formatTvl(marketInsights?.total_tvl || 0)}
            </motion.p>
            <p>Total Strategies: {marketInsights?.total_strategies.toLocaleString()}</p>
            <p>Average APY: {marketInsights?.average_apy.toFixed(2)}%</p>
          </CardContent>
        </Card>
      </motion.div>

      {/* AI Portfolio */}
      <motion.div {...glowPulse} className="col-span-4 relative z-10">
        <Card className="bg-gradient-to-b from-black/70 to-black/40 border border-fuchsia-900/50 shadow-[0_0_25px_-8px_rgba(217,70,239,0.5)]">
          <CardHeader>
            <CardTitle className="text-fuchsia-400">AI Portfolio</CardTitle>
          </CardHeader>
          <CardContent className="text-sm space-y-2">
            <p>Top AI-Recommended Strategies:</p>
            {topStrategies.map((strategy, index) => (
              <div key={strategy.id} className="p-2 bg-fuchsia-500/10 rounded border border-fuchsia-500/20">
                <div className="flex justify-between items-center">
                  <span className="text-cyan-300">{strategy.protocol}</span>
                  <span className={getRiskColor(strategy.risk_index)}>
                    {strategy.risk_index.toFixed(1)} risk
                  </span>
                </div>
                <div className="text-fuchsia-300">
                  {strategy.apy.toFixed(2)}% APY • {strategy.chain}
                </div>
                <div className="text-xs text-gray-400">
                  {formatTvl(strategy.tvl_usd)} TVL
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </motion.div>

      {/* Comparison Lab */}
      <motion.div {...glowPulse} className="col-span-4 relative z-10">
        <Card className="bg-gradient-to-b from-black/70 to-black/40 border border-cyan-900/50 shadow-[0_0_25px_-8px_rgba(34,211,238,0.5)]">
          <CardHeader>
            <CardTitle className="text-cyan-400">Comparison Lab</CardTitle>
          </CardHeader>
          <CardContent className="text-sm space-y-2">
            {topStrategies.length >= 2 && (
              <>
                <p>{topStrategies[0].protocol} vs {topStrategies[1].protocol}:</p>
                <p>APY: {topStrategies[0].apy.toFixed(1)}% vs {topStrategies[1].apy.toFixed(1)}%</p>
                <p>Risk: {topStrategies[0].risk_index.toFixed(1)} vs {topStrategies[1].risk_index.toFixed(1)}</p>
                <p>TVL: {formatTvl(topStrategies[0].tvl_usd)} vs {formatTvl(topStrategies[1].tvl_usd)}</p>
                <p>AI Score: {topStrategies[0].ai_score.toFixed(0)} vs {topStrategies[1].ai_score.toFixed(0)}</p>
              </>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* AI Indices */}
      <motion.div {...glowPulse} className="col-span-12 relative z-10">
        <Card className="bg-gradient-to-b from-black/70 to-black/40 border border-fuchsia-900/50 shadow-[0_0_25px_-8px_rgba(217,70,239,0.5)]">
          <CardHeader>
            <CardTitle className="text-fuchsia-400">AI Indices</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-3 gap-6 text-center">
            <motion.div animate={{ scale: [1, 1.05, 1] }} transition={{ duration: 2, repeat: Infinity }}>
              <h4 className="text-cyan-300 font-bold">GYI (Genora Yield Index)</h4>
              <p>Average APY: {marketInsights?.average_apy.toFixed(1)}%</p>
              <p className="text-xs text-gray-400">{strategies.length} strategies analyzed</p>
            </motion.div>
            <motion.div animate={{ scale: [1, 1.05, 1] }} transition={{ duration: 2.5, repeat: Infinity }}>
              <h4 className="text-fuchsia-300 font-bold">AMI (AI Momentum Index)</h4>
              <p>TVL Growth: {marketInsights?.market_trends.tvl_trend}</p>
              <p className="text-xs text-gray-400">{marketInsights?.market_trends.new_strategies} new strategies</p>
            </motion.div>
            <motion.div animate={{ scale: [1, 1.05, 1] }} transition={{ duration: 3, repeat: Infinity }}>
              <h4 className="text-cyan-300 font-bold">RAY (Risk-Adjusted Yield)</h4>
              <p>Optimal Yield: {topStrategies[0]?.apy.toFixed(1)}%</p>
              <p className="text-xs text-gray-400">Best: {topStrategies[0]?.protocol}</p>
            </motion.div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Floating Genie Lamp symbol */}
      <motion.div
        animate={{ rotate: [0, 360], y: [0, -10, 0] }}
        transition={{ rotate: { duration: 30, repeat: Infinity, ease: "linear" }, y: { duration: 4, repeat: Infinity } }}
        onMouseEnter={playHoverResonance}
        className="fixed bottom-8 right-8 text-cyan-400 drop-shadow-[0_0_20px_#22d3ee] cursor-pointer"
      >
        <Sparkles className="w-10 h-10" />
      </motion.div>
    </div>
  );
}
