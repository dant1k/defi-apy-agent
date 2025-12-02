'use client';

import { useState, useEffect } from 'react';

interface AIScore {
  overall: number;
  breakdown: {
    apy: number;
    stability: number;
    liquidity: number;
    risk: number;
    growth: number;
  };
  explanation: string;
  recommendations: string[];
}

interface AIScoringProps {
  strategy: any;
}

export function AIScoring({ strategy }: AIScoringProps) {
  const [score, setScore] = useState<AIScore | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate AI analysis
    setTimeout(() => {
      const mockScore: AIScore = {
        overall: strategy.ai_score || Math.random() * 40 + 60, // 60-100 range
        breakdown: {
          apy: Math.min(100, (strategy.apy || 0) * 5), // APY * 5, capped at 100
          stability: Math.max(20, 100 - (strategy.risk_index || 1) * 20), // Inverse of risk
          liquidity: Math.min(100, (strategy.tvl_usd || 0) / 10000000 * 100), // TVL-based
          risk: Math.max(0, 100 - (strategy.risk_index || 1) * 30), // Risk assessment
          growth: Math.max(0, (strategy.tvl_growth_24h || 0) * 2 + 50) // Growth factor
        },
        explanation: generateExplanation(strategy),
        recommendations: generateRecommendations(strategy)
      };
      setScore(mockScore);
      setLoading(false);
    }, 800);
  }, [strategy]);

  const generateExplanation = (strategy: any): string => {
    const apy = strategy.apy || 0;
    const tvl = strategy.tvl_usd || 0;
    const risk = strategy.risk_index || 1;
    
    if (apy > 15 && risk < 2) {
      return "Exceptional strategy with high yield and low risk. Strong fundamentals and proven track record make this an excellent choice for conservative investors seeking above-average returns.";
    } else if (apy > 10 && tvl > 1000000) {
      return "Solid strategy with good yield and substantial liquidity. Well-established protocol with consistent performance and manageable risk profile.";
    } else if (apy > 8) {
      return "Moderate strategy offering decent returns with acceptable risk. Suitable for investors with moderate risk tolerance looking for steady growth.";
    } else {
      return "Conservative strategy with lower but stable returns. Ideal for risk-averse investors prioritizing capital preservation over high yields.";
    }
  };

  const generateRecommendations = (strategy: any): string[] => {
    const recommendations = [];
    const apy = strategy.apy || 0;
    const tvl = strategy.tvl_usd || 0;
    const risk = strategy.risk_index || 1;

    if (apy > 15) {
      recommendations.push("Consider this for high-yield portfolio allocation");
    }
    if (tvl > 5000000) {
      recommendations.push("High liquidity makes it suitable for large positions");
    }
    if (risk < 1.5) {
      recommendations.push("Low risk profile - good for conservative investors");
    }
    if (strategy.tvl_growth_24h > 5) {
      recommendations.push("Growing TVL indicates increasing confidence");
    }
    if (recommendations.length === 0) {
      recommendations.push("Monitor for potential improvements in yield or risk metrics");
    }

    return recommendations;
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return '#48bb78';
    if (score >= 60) return '#ed8936';
    return '#f56565';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 90) return 'Excellent';
    if (score >= 80) return 'Very Good';
    if (score >= 70) return 'Good';
    if (score >= 60) return 'Fair';
    return 'Poor';
  };

  if (loading) {
    return (
      <div className="ai-scoring">
        <div className="ai-loading">
          <div className="ai-spinner"></div>
          <p>AI is analyzing this strategy...</p>
        </div>
      </div>
    );
  }

  if (!score) return null;

  return (
    <div className="ai-scoring">
      <div className="ai-header">
        <h3>🤖 AI Analysis</h3>
        <div className="overall-score">
          <div 
            className="score-circle"
            style={{ 
              background: `conic-gradient(${getScoreColor(score.overall)} ${score.overall * 3.6}deg, rgba(111, 165, 255, 0.1) 0deg)` 
            }}
          >
            <div className="score-inner">
              <span className="score-value">{score.overall.toFixed(0)}</span>
              <span className="score-label">{getScoreLabel(score.overall)}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="score-breakdown">
        <h4>Score Breakdown</h4>
        <div className="breakdown-grid">
          {Object.entries(score.breakdown).map(([key, value]) => (
            <div key={key} className="breakdown-item">
              <div className="breakdown-header">
                <span className="breakdown-label">{key.charAt(0).toUpperCase() + key.slice(1)}</span>
                <span className="breakdown-value">{value.toFixed(0)}</span>
              </div>
              <div className="breakdown-bar">
                <div 
                  className="breakdown-fill"
                  style={{ 
                    width: `${value}%`,
                    backgroundColor: getScoreColor(value)
                  }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="ai-explanation">
        <h4>💡 AI Explanation</h4>
        <p>{score.explanation}</p>
      </div>

      <div className="ai-recommendations">
        <h4>📋 Recommendations</h4>
        <ul>
          {score.recommendations.map((rec, index) => (
            <li key={index}>{rec}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
