'use client';

import { useState, useEffect, useRef } from 'react';

interface SearchResult {
  id: string;
  type: 'strategy' | 'protocol' | 'chain' | 'token';
  name: string;
  description: string;
  apy?: number;
  tvl?: number;
  icon?: string;
}

interface GlobalSearchProps {
  strategies: any[];
  onResultClick?: (result: SearchResult) => void;
}

export function GlobalSearch({ strategies, onResultClick }: GlobalSearchProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const searchRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (query.length < 2) {
      setResults([]);
      return;
    }

    const searchResults: SearchResult[] = [];

    // Search strategies
    strategies.forEach(strategy => {
      if (
        strategy.name?.toLowerCase().includes(query.toLowerCase()) ||
        strategy.protocol?.toLowerCase().includes(query.toLowerCase()) ||
        strategy.chain?.toLowerCase().includes(query.toLowerCase())
      ) {
        searchResults.push({
          id: strategy.id,
          type: 'strategy',
          name: strategy.name,
          description: `${strategy.protocol} on ${strategy.chain}`,
          apy: strategy.apy,
          tvl: strategy.tvl_usd,
        });
      }
    });

    // Search protocols
    const protocols = [...new Set(strategies.map(s => s.protocol))];
    protocols.forEach(protocol => {
      if (protocol?.toLowerCase().includes(query.toLowerCase())) {
        const protocolStrategies = strategies.filter(s => s.protocol === protocol);
        const avgApy = protocolStrategies.reduce((sum, s) => sum + (s.apy || 0), 0) / protocolStrategies.length;
        const totalTvl = protocolStrategies.reduce((sum, s) => sum + (s.tvl_usd || 0), 0);

        searchResults.push({
          id: `protocol-${protocol}`,
          type: 'protocol',
          name: protocol,
          description: `${protocolStrategies.length} strategies`,
          apy: avgApy,
          tvl: totalTvl,
        });
      }
    });

    // Search chains
    const chains = [...new Set(strategies.map(s => s.chain))];
    chains.forEach(chain => {
      if (chain?.toLowerCase().includes(query.toLowerCase())) {
        const chainStrategies = strategies.filter(s => s.chain === chain);
        const avgApy = chainStrategies.reduce((sum, s) => sum + (s.apy || 0), 0) / chainStrategies.length;
        const totalTvl = chainStrategies.reduce((sum, s) => sum + (s.tvl_usd || 0), 0);

        searchResults.push({
          id: `chain-${chain}`,
          type: 'chain',
          name: chain,
          description: `${chainStrategies.length} strategies`,
          apy: avgApy,
          tvl: totalTvl,
        });
      }
    });

    setResults(searchResults.slice(0, 8)); // Limit to 8 results
  }, [query, strategies]);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setQuery('');
        setSelectedIndex(-1);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if (!isOpen) return;

      switch (event.key) {
        case 'ArrowDown':
          event.preventDefault();
          setSelectedIndex(prev => (prev < results.length - 1 ? prev + 1 : 0));
          break;
        case 'ArrowUp':
          event.preventDefault();
          setSelectedIndex(prev => (prev > 0 ? prev - 1 : results.length - 1));
          break;
        case 'Enter':
          event.preventDefault();
          if (selectedIndex >= 0 && results[selectedIndex]) {
            handleResultClick(results[selectedIndex]);
          }
          break;
        case 'Escape':
          setIsOpen(false);
          setQuery('');
          setSelectedIndex(-1);
          break;
      }
    }

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, selectedIndex, results]);

  const handleResultClick = (result: SearchResult) => {
    if (onResultClick) {
      onResultClick(result);
    }
    setIsOpen(false);
    setQuery('');
    setSelectedIndex(-1);
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'strategy': return '📊';
      case 'protocol': return '🏛️';
      case 'chain': return '⛓️';
      case 'token': return '🪙';
      default: return '🔍';
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'strategy': return '#6fa5ff';
      case 'protocol': return '#86f7ff';
      case 'chain': return '#48bb78';
      case 'token': return '#ed8936';
      default: return '#a0aec0';
    }
  };

  return (
    <div className="global-search" ref={searchRef}>
      <div className="search-input-container">
        <div className="search-icon">🔍</div>
        <input
          ref={inputRef}
          type="text"
          placeholder="Search strategies, protocols, chains..."
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setIsOpen(true);
            setSelectedIndex(-1);
          }}
          onFocus={() => setIsOpen(true)}
          className="search-input"
        />
        {query && (
          <button 
            className="clear-btn"
            onClick={() => {
              setQuery('');
              setResults([]);
              setIsOpen(false);
              inputRef.current?.focus();
            }}
          >
            ×
          </button>
        )}
      </div>

      {isOpen && results.length > 0 && (
        <div className="search-results">
          <div className="results-header">
            <span>Search Results</span>
            <span className="results-count">{results.length}</span>
          </div>
          <div className="results-list">
            {results.map((result, index) => (
              <div
                key={result.id}
                className={`result-item ${index === selectedIndex ? 'selected' : ''}`}
                onClick={() => handleResultClick(result)}
                style={{ borderLeftColor: getTypeColor(result.type) }}
              >
                <div className="result-icon">
                  {getTypeIcon(result.type)}
                </div>
                <div className="result-content">
                  <div className="result-header">
                    <h4>{result.name}</h4>
                    <span className="result-type">{result.type}</span>
                  </div>
                  <p className="result-description">{result.description}</p>
                  {(result.apy || result.tvl) && (
                    <div className="result-metrics">
                      {result.apy && (
                        <span className="metric">
                          {result.apy.toFixed(2)}% APY
                        </span>
                      )}
                      {result.tvl && (
                        <span className="metric">
                          ${(result.tvl / 1000000).toFixed(1)}M TVL
                        </span>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
          <div className="search-footer">
            <span>Use ↑↓ to navigate, Enter to select, Esc to close</span>
          </div>
        </div>
      )}

      {isOpen && query.length >= 2 && results.length === 0 && (
        <div className="search-results">
          <div className="no-results">
            <p>No results found for "{query}"</p>
            <p>Try searching for strategies, protocols, or chains</p>
          </div>
        </div>
      )}
    </div>
  );
}
