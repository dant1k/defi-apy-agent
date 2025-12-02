'use client';

import { useState, useEffect } from 'react';

interface Alert {
  id: string;
  type: 'apy_spike' | 'tvl_drop' | 'new_opportunity' | 'risk_warning' | 'trending';
  title: string;
  message: string;
  strategy: string;
  value: number;
  change: number;
  timestamp: Date;
  severity: 'low' | 'medium' | 'high';
  action?: string;
}

interface AIAlertsProps {
  strategies: any[];
}

export function AIAlerts({ strategies }: AIAlertsProps) {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [showAll, setShowAll] = useState(false);

  useEffect(() => {
    // Generate mock alerts based on strategies
    const generateAlerts = (): Alert[] => {
      const mockAlerts: Alert[] = [];
      
      strategies.slice(0, 5).forEach((strategy, index) => {
        // APY Spike Alert
        if (strategy.apy > 15) {
          mockAlerts.push({
            id: `apy-${index}`,
            type: 'apy_spike',
            title: 'APY Spike Detected',
            message: `${strategy.name} shows exceptional yield potential`,
            strategy: strategy.name,
            value: strategy.apy,
            change: Math.random() * 5 + 2,
            timestamp: new Date(Date.now() - Math.random() * 3600000), // Last hour
            severity: 'high',
            action: 'Consider allocation'
          });
        }

        // TVL Drop Alert
        if (strategy.tvl_growth_24h < -5) {
          mockAlerts.push({
            id: `tvl-${index}`,
            type: 'tvl_drop',
            title: 'TVL Decline Warning',
            message: `${strategy.name} experiencing liquidity outflow`,
            strategy: strategy.name,
            value: strategy.tvl_usd,
            change: strategy.tvl_growth_24h,
            timestamp: new Date(Date.now() - Math.random() * 7200000), // Last 2 hours
            severity: 'medium',
            action: 'Monitor closely'
          });
        }

        // New Opportunity Alert
        if (strategy.ai_score > 80) {
          mockAlerts.push({
            id: `opp-${index}`,
            type: 'new_opportunity',
            title: 'New Opportunity',
            message: `AI recommends ${strategy.name} for optimal returns`,
            strategy: strategy.name,
            value: strategy.ai_score,
            change: 0,
            timestamp: new Date(Date.now() - Math.random() * 1800000), // Last 30 min
            severity: 'low',
            action: 'Review strategy'
          });
        }
      });

      // Add some trending alerts
      mockAlerts.push({
        id: 'trend-1',
        type: 'trending',
            title: 'Trending Strategy',
        message: 'AI Vaults gaining momentum across protocols',
        strategy: 'AI Vaults',
        value: 12.5,
        change: 8.2,
        timestamp: new Date(Date.now() - Math.random() * 900000), // Last 15 min
        severity: 'medium',
        action: 'Explore category'
      });

      return mockAlerts.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
    };

    const mockAlerts = generateAlerts();
    setAlerts(mockAlerts);
  }, [strategies]);

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'apy_spike': return '↑';
      case 'tvl_drop': return '↓';
      case 'new_opportunity': return '●';
      case 'risk_warning': return '!';
      case 'trending': return '→';
      default: return '•';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return '#f56565';
      case 'medium': return '#ed8936';
      case 'low': return '#48bb78';
      default: return '#a0aec0';
    }
  };

  const formatTimeAgo = (timestamp: Date) => {
    const now = new Date();
    const diff = now.getTime() - timestamp.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    
    if (minutes < 60) {
      return `${minutes}m ago`;
    } else if (hours < 24) {
      return `${hours}h ago`;
    } else {
      return timestamp.toLocaleDateString();
    }
  };

  const displayedAlerts = showAll ? alerts : alerts.slice(0, 3);

  if (alerts.length === 0) {
    return (
      <div className="ai-alerts">
        <div className="alerts-header">
          <h3>AI Alerts</h3>
        </div>
        <div className="no-alerts">
          <p>No alerts at the moment. AI is monitoring the market...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="ai-alerts">
        <div className="alerts-header">
          <h3>AI Alerts</h3>
          <div className="alerts-badge">{alerts.length}</div>
          {alerts.length > 3 && (
            <button 
              className="show-all-btn"
              onClick={() => setShowAll(!showAll)}
            >
              {showAll ? 'Show Less' : `Show All (${alerts.length})`}
            </button>
          )}
        </div>

      <div className="alerts-list">
        {displayedAlerts.map(alert => (
          <div 
            key={alert.id} 
            className={`alert-item ${alert.severity}`}
            style={{ borderLeftColor: getSeverityColor(alert.severity) }}
          >
            <div className="alert-icon">
              {getAlertIcon(alert.type)}
            </div>
            
            <div className="alert-content">
              <div className="alert-header">
                <h4>{alert.title}</h4>
                <span className="alert-time">{formatTimeAgo(alert.timestamp)}</span>
              </div>
              
              <p className="alert-message">{alert.message}</p>
              
              <div className="alert-details">
                <span className="alert-strategy">{alert.strategy}</span>
                {alert.change !== 0 && (
                  <span className={`alert-change ${alert.change > 0 ? 'positive' : 'negative'}`}>
                    {alert.change > 0 ? '+' : ''}{alert.change.toFixed(1)}%
                  </span>
                )}
              </div>
              
              {alert.action && (
                <div className="alert-action">
                  <button className="action-btn">
                    {alert.action}
                  </button>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="alerts-footer">
        <p>AI continuously monitors 500+ strategies across 20+ protocols</p>
      </div>
    </div>
  );
}
