'use client';

import { useState } from 'react';

interface StrategyExplainerProps {
  strategy: any;
  isOpen: boolean;
  onClose: () => void;
}

export function StrategyExplainer({ strategy, isOpen, onClose }: StrategyExplainerProps) {
  const [loading, setLoading] = useState(false);
  const [explanation, setExplanation] = useState<any>(null);

  const generateExplanation = async () => {
    setLoading(true);
    
    // Simulate AI analysis
    setTimeout(() => {
      const mockExplanation = {
        overview: `This ${strategy.protocol} strategy on ${strategy.chain} operates as a ${getStrategyType(strategy)} mechanism. It generates ${strategy.apy.toFixed(2)}% APY by ${getYieldSource(strategy)}.`,
        
        howItWorks: [
          "Users deposit assets into the protocol's liquidity pool",
          "The protocol automatically allocates funds across optimal strategies",
          "Yield is generated through lending, trading fees, or staking rewards",
          "Returns are compounded and distributed to participants"
        ],
        
        risks: [
          "Smart contract risk - potential bugs in protocol code",
          "Market risk - underlying asset price volatility",
          "Liquidity risk - difficulty withdrawing during high demand",
          "Regulatory risk - changing compliance requirements"
        ],
        
        benefits: [
          "Automated yield optimization",
          "Diversified exposure across multiple strategies",
          "Professional risk management",
          "Compound interest effects"
        ],
        
        recommendations: [
          "Start with a small allocation to test the strategy",
          "Monitor TVL growth and community sentiment",
          "Consider dollar-cost averaging for large positions",
          "Set up alerts for significant changes in APY or TVL"
        ],
        
        technicalDetails: {
          tvl: strategy.tvl_usd,
          apy: strategy.apy,
          riskScore: strategy.risk_index || 1.5,
          growth: strategy.tvl_growth_24h || 0,
          protocol: strategy.protocol,
          chain: strategy.chain
        }
      };
      
      setExplanation(mockExplanation);
      setLoading(false);
    }, 1500);
  };

  const getStrategyType = (strategy: any) => {
    const name = strategy.name?.toLowerCase() || '';
    if (name.includes('lending') || name.includes('borrow')) return 'lending';
    if (name.includes('lp') || name.includes('liquidity')) return 'liquidity provision';
    if (name.includes('vault') || name.includes('yield')) return 'yield farming';
    if (name.includes('stake') || name.includes('staking')) return 'staking';
    return 'yield optimization';
  };

  const getYieldSource = (strategy: any) => {
    const apy = strategy.apy || 0;
    if (apy > 20) return 'high-risk, high-reward trading strategies';
    if (apy > 10) return 'leveraged yield farming and arbitrage';
    if (apy > 5) return 'lending protocols and liquidity mining';
    return 'conservative lending and staking rewards';
  };

  const getRiskLevel = (riskScore: number) => {
    if (riskScore < 1.5) return { level: 'Low', color: '#48bb78' };
    if (riskScore < 2.5) return { level: 'Medium', color: '#ed8936' };
    return { level: 'High', color: '#f56565' };
  };

  if (!isOpen) return null;

  return (
    <div className="strategy-explainer-overlay" onClick={onClose}>
      <div className="strategy-explainer" onClick={(e) => e.stopPropagation()}>
        <div className="explainer-header">
          <h2>🤖 AI Strategy Explanation</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <div className="explainer-content">
          {!explanation && !loading && (
            <div className="explainer-prompt">
              <h3>{strategy.name}</h3>
              <p>Get AI-powered insights about this strategy</p>
              <button className="explain-btn" onClick={generateExplanation}>
                🧠 Explain This Strategy
              </button>
            </div>
          )}

          {loading && (
            <div className="explainer-loading">
              <div className="ai-spinner"></div>
              <p>AI is analyzing this strategy...</p>
            </div>
          )}

          {explanation && (
            <div className="explanation-content">
              <div className="strategy-overview">
                <h3>📋 Strategy Overview</h3>
                <p>{explanation.overview}</p>
              </div>

              <div className="explanation-grid">
                <div className="explanation-section">
                  <h4>⚙️ How It Works</h4>
                  <ul>
                    {explanation.howItWorks.map((step: string, index: number) => (
                      <li key={index}>{step}</li>
                    ))}
                  </ul>
                </div>

                <div className="explanation-section">
                  <h4>✅ Benefits</h4>
                  <ul>
                    {explanation.benefits.map((benefit: string, index: number) => (
                      <li key={index}>{benefit}</li>
                    ))}
                  </ul>
                </div>

                <div className="explanation-section">
                  <h4>⚠️ Risks</h4>
                  <ul>
                    {explanation.risks.map((risk: string, index: number) => (
                      <li key={index}>{risk}</li>
                    ))}
                  </ul>
                </div>

                <div className="explanation-section">
                  <h4>💡 Recommendations</h4>
                  <ul>
                    {explanation.recommendations.map((rec: string, index: number) => (
                      <li key={index}>{rec}</li>
                    ))}
                  </ul>
                </div>
              </div>

              <div className="technical-summary">
                <h4>📊 Technical Summary</h4>
                <div className="tech-grid">
                  <div className="tech-item">
                    <span className="tech-label">TVL</span>
                    <span className="tech-value">${(explanation.technicalDetails.tvl / 1000000).toFixed(1)}M</span>
                  </div>
                  <div className="tech-item">
                    <span className="tech-label">APY</span>
                    <span className="tech-value">{explanation.technicalDetails.apy.toFixed(2)}%</span>
                  </div>
                  <div className="tech-item">
                    <span className="tech-label">Risk Level</span>
                    <span 
                      className="tech-value"
                      style={{ color: getRiskLevel(explanation.technicalDetails.riskScore).color }}
                    >
                      {getRiskLevel(explanation.technicalDetails.riskScore).level}
                    </span>
                  </div>
                  <div className="tech-item">
                    <span className="tech-label">24h Growth</span>
                    <span className={`tech-value ${explanation.technicalDetails.growth > 0 ? 'positive' : 'negative'}`}>
                      {explanation.technicalDetails.growth > 0 ? '+' : ''}{explanation.technicalDetails.growth.toFixed(2)}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
