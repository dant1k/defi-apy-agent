'use client';

import { useState, useEffect } from 'react';

interface WatchlistItem {
  id: string;
  name: string;
  protocol: string;
  chain: string;
  apy: number;
  tvl: number;
  addedAt: Date;
  notes?: string;
}

interface WatchlistProps {
  strategies: any[];
}

export function Watchlist({ strategies }: WatchlistProps) {
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [selectedStrategy, setSelectedStrategy] = useState<any>(null);

  useEffect(() => {
    // Load watchlist from localStorage
    const saved = localStorage.getItem('defi-watchlist');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setWatchlist(parsed.map((item: any) => ({
          ...item,
          addedAt: new Date(item.addedAt)
        })));
      } catch (error) {
        console.error('Failed to load watchlist:', error);
      }
    }
  }, []);

  const saveWatchlist = (newWatchlist: WatchlistItem[]) => {
    setWatchlist(newWatchlist);
    localStorage.setItem('defi-watchlist', JSON.stringify(newWatchlist));
  };

  const addToWatchlist = (strategy: any) => {
    const newItem: WatchlistItem = {
      id: strategy.id,
      name: strategy.name,
      protocol: strategy.protocol,
      chain: strategy.chain,
      apy: strategy.apy,
      tvl: strategy.tvl_usd,
      addedAt: new Date()
    };

    const updated = [...watchlist, newItem];
    saveWatchlist(updated);
    setShowAddForm(false);
    setSelectedStrategy(null);
  };

  const removeFromWatchlist = (id: string) => {
    const updated = watchlist.filter(item => item.id !== id);
    saveWatchlist(updated);
  };

  const updateNotes = (id: string, notes: string) => {
    const updated = watchlist.map(item => 
      item.id === id ? { ...item, notes } : item
    );
    saveWatchlist(updated);
  };

  const isInWatchlist = (strategyId: string) => {
    return watchlist.some(item => item.id === strategyId);
  };

  return (
    <div className="watchlist">
      <div className="watchlist-header">
        <h3>⭐ Watchlist</h3>
        <div className="watchlist-actions">
          <button 
            className="add-btn"
            onClick={() => setShowAddForm(true)}
          >
            Add Strategy
          </button>
          <span className="watchlist-count">{watchlist.length}</span>
        </div>
      </div>

      {showAddForm && (
        <div className="add-strategy-form">
          <h4>Add Strategy to Watchlist</h4>
          <div className="strategy-selector">
            {strategies.slice(0, 10).map(strategy => (
              <div 
                key={strategy.id}
                className={`strategy-option ${isInWatchlist(strategy.id) ? 'in-watchlist' : ''}`}
                onClick={() => !isInWatchlist(strategy.id) && addToWatchlist(strategy)}
              >
                <div className="strategy-info">
                  <h5>{strategy.name}</h5>
                  <p>{strategy.protocol} • {strategy.chain}</p>
                  <span className="strategy-apy">{strategy.apy.toFixed(2)}% APY</span>
                </div>
                {isInWatchlist(strategy.id) ? (
                  <span className="added-badge">✓ Added</span>
                ) : (
                  <button className="add-strategy-btn">Add</button>
                )}
              </div>
            ))}
          </div>
          <button 
            className="cancel-btn"
            onClick={() => setShowAddForm(false)}
          >
            Cancel
          </button>
        </div>
      )}

      <div className="watchlist-items">
        {watchlist.length === 0 ? (
          <div className="empty-watchlist">
            <p>No strategies in your watchlist yet.</p>
            <p>Add strategies to track their performance!</p>
          </div>
        ) : (
          watchlist.map(item => (
            <div key={item.id} className="watchlist-item">
              <div className="item-header">
                <div className="item-info">
                  <h5>{item.name}</h5>
                  <p>{item.protocol} • {item.chain}</p>
                </div>
                <button 
                  className="remove-btn"
                  onClick={() => removeFromWatchlist(item.id)}
                >
                  ×
                </button>
              </div>
              
              <div className="item-metrics">
                <div className="metric">
                  <span className="metric-label">APY</span>
                  <span className="metric-value">{item.apy.toFixed(2)}%</span>
                </div>
                <div className="metric">
                  <span className="metric-label">TVL</span>
                  <span className="metric-value">${(item.tvl / 1000000).toFixed(1)}M</span>
                </div>
                <div className="metric">
                  <span className="metric-label">Added</span>
                  <span className="metric-value">{item.addedAt.toLocaleDateString()}</span>
                </div>
              </div>

              <div className="item-notes">
                <textarea
                  placeholder="Add notes about this strategy..."
                  value={item.notes || ''}
                  onChange={(e) => updateNotes(item.id, e.target.value)}
                  className="notes-input"
                />
              </div>
            </div>
          ))
        )}
      </div>

      {watchlist.length > 0 && (
        <div className="watchlist-summary">
          <h4>📊 Watchlist Summary</h4>
          <div className="summary-stats">
            <div className="summary-item">
              <span className="summary-label">Average APY</span>
              <span className="summary-value">
                {(watchlist.reduce((sum, item) => sum + item.apy, 0) / watchlist.length).toFixed(2)}%
              </span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Total TVL</span>
              <span className="summary-value">
                ${(watchlist.reduce((sum, item) => sum + item.tvl, 0) / 1000000).toFixed(1)}M
              </span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Protocols</span>
              <span className="summary-value">
                {new Set(watchlist.map(item => item.protocol)).size}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
