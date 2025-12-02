'use client';

import { useState, useEffect } from 'react';

interface WalletInfo {
  address: string;
  balance: number;
  network: string;
  connected: boolean;
}

interface WalletConnectorProps {
  onConnect?: (wallet: WalletInfo) => void;
  onDisconnect?: () => void;
}

export function WalletConnector({ onConnect, onDisconnect }: WalletConnectorProps) {
  const [wallet, setWallet] = useState<WalletInfo | null>(null);
  const [showConnector, setShowConnector] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Check if wallet is already connected
    const savedWallet = localStorage.getItem('defi-wallet');
    if (savedWallet) {
      try {
        const parsed = JSON.parse(savedWallet);
        setWallet(parsed);
      } catch (error) {
        console.error('Failed to load wallet info:', error);
      }
    }
  }, []);

  const connectWallet = async (walletType: 'metamask' | 'walletconnect' | 'coinbase') => {
    setLoading(true);
    
    // Simulate wallet connection
    setTimeout(() => {
      const mockWallet: WalletInfo = {
        address: `0x${Math.random().toString(16).substr(2, 40)}`,
        balance: Math.random() * 10 + 0.1,
        network: 'Ethereum',
        connected: true
      };
      
      setWallet(mockWallet);
      localStorage.setItem('defi-wallet', JSON.stringify(mockWallet));
      setShowConnector(false);
      setLoading(false);
      
      if (onConnect) {
        onConnect(mockWallet);
      }
    }, 1500);
  };

  const disconnectWallet = () => {
    setWallet(null);
    localStorage.removeItem('defi-wallet');
    setShowConnector(false);
    
    if (onDisconnect) {
      onDisconnect();
    }
  };

  const formatAddress = (address: string) => {
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  };

  const copyAddress = () => {
    if (wallet) {
      navigator.clipboard.writeText(wallet.address);
      // You could add a toast notification here
    }
  };

  if (wallet) {
    return (
      <div className="wallet-connector">
        <div className="wallet-info">
          <div className="wallet-address" onClick={copyAddress}>
            <span className="address-text">{formatAddress(wallet.address)}</span>
            <span className="copy-icon">📋</span>
          </div>
          <div className="wallet-balance">
            {wallet.balance.toFixed(4)} ETH
          </div>
          <div className="wallet-network">
            {wallet.network}
          </div>
        </div>
        <button className="disconnect-btn" onClick={disconnectWallet}>
          Disconnect
        </button>
      </div>
    );
  }

  return (
    <div className="wallet-connector">
      <button 
        className="connect-btn"
        onClick={() => setShowConnector(true)}
      >
        🔗 Connect Wallet
      </button>

      {showConnector && (
        <div className="wallet-connector-modal">
          <div className="connector-overlay" onClick={() => setShowConnector(false)}>
            <div className="connector-content" onClick={(e) => e.stopPropagation()}>
              <div className="connector-header">
                <h3>Connect Your Wallet</h3>
                <button 
                  className="close-btn"
                  onClick={() => setShowConnector(false)}
                >
                  ×
                </button>
              </div>

              <div className="connector-options">
                <div className="wallet-option">
                  <div className="wallet-icon">🦊</div>
                  <div className="wallet-info">
                    <h4>MetaMask</h4>
                    <p>Connect using MetaMask browser extension</p>
                  </div>
                  <button 
                    className="connect-option-btn"
                    onClick={() => connectWallet('metamask')}
                    disabled={loading}
                  >
                    {loading ? 'Connecting...' : 'Connect'}
                  </button>
                </div>

                <div className="wallet-option">
                  <div className="wallet-icon">🔗</div>
                  <div className="wallet-info">
                    <h4>WalletConnect</h4>
                    <p>Connect using WalletConnect protocol</p>
                  </div>
                  <button 
                    className="connect-option-btn"
                    onClick={() => connectWallet('walletconnect')}
                    disabled={loading}
                  >
                    {loading ? 'Connecting...' : 'Connect'}
                  </button>
                </div>

                <div className="wallet-option">
                  <div className="wallet-icon">🔵</div>
                  <div className="wallet-info">
                    <h4>Coinbase Wallet</h4>
                    <p>Connect using Coinbase Wallet</p>
                  </div>
                  <button 
                    className="connect-option-btn"
                    onClick={() => connectWallet('coinbase')}
                    disabled={loading}
                  >
                    {loading ? 'Connecting...' : 'Connect'}
                  </button>
                </div>
              </div>

              <div className="connector-footer">
                <p>By connecting, you agree to our Terms of Service and Privacy Policy</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
