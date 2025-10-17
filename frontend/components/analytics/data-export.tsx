'use client';

import { useState } from 'react';

interface DataExportProps {
  strategies: any[];
  protocolData?: any[];
}

export function DataExport({ strategies, protocolData }: DataExportProps) {
  const [isExporting, setIsExporting] = useState(false);
  const [exportFormat, setExportFormat] = useState<'csv' | 'json' | 'xlsx'>('csv');

  const exportData = async (format: 'csv' | 'json' | 'xlsx') => {
    setIsExporting(true);
    
    try {
      let data: any;
      let filename: string;
      let mimeType: string;

      switch (format) {
        case 'csv':
          data = convertToCSV(strategies);
          filename = `genora-strategies-${new Date().toISOString().split('T')[0]}.csv`;
          mimeType = 'text/csv';
          break;
        case 'json':
          data = JSON.stringify(strategies, null, 2);
          filename = `genora-strategies-${new Date().toISOString().split('T')[0]}.json`;
          mimeType = 'application/json';
          break;
        case 'xlsx':
          // For XLSX, we'll create a simple CSV-like structure
          data = convertToCSV(strategies);
          filename = `genora-strategies-${new Date().toISOString().split('T')[0]}.xlsx`;
          mimeType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
          break;
        default:
          throw new Error('Unsupported format');
      }

      // Create and download file
      const blob = new Blob([data], { type: mimeType });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

    } catch (error) {
      console.error('Export failed:', error);
      alert('Export failed. Please try again.');
    } finally {
      setIsExporting(false);
    }
  };

  const convertToCSV = (data: any[]) => {
    if (!data || data.length === 0) return '';
    
    const headers = [
      'Name',
      'Protocol',
      'Chain',
      'Token Pair',
      'APY (%)',
      'TVL (USD)',
      'Risk Score',
      'AI Score',
      'URL'
    ];
    
    const rows = data.map(strategy => [
      strategy.name || '',
      strategy.protocol || '',
      strategy.chain || '',
      strategy.token_pair || '',
      strategy.apy || 0,
      strategy.tvl_usd || 0,
      strategy.risk_score || 0,
      strategy.ai_score || 0,
      strategy.url || ''
    ]);
    
    const csvContent = [headers, ...rows]
      .map(row => row.map(field => `"${field}"`).join(','))
      .join('\n');
    
    return csvContent;
  };

  const getExportIcon = (format: string) => {
    switch (format) {
      case 'csv': return '📊';
      case 'json': return '📄';
      case 'xlsx': return '📈';
      default: return '📁';
    }
  };

  const getExportDescription = (format: string) => {
    switch (format) {
      case 'csv': return 'Comma-separated values for Excel/Google Sheets';
      case 'json': return 'JSON format for developers and APIs';
      case 'xlsx': return 'Excel spreadsheet format';
      default: return '';
    }
  };

  return (
    <div className="card-genora">
      <div className="flex justify-between items-center mb-6">
        <h2 className="font-orbitron text-2xl font-bold text-[var(--neonAqua)]">
          Data Export
        </h2>
        <div className="text-sm text-white/60">
          {strategies.length} strategies available
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {(['csv', 'json', 'xlsx'] as const).map((format) => (
          <div 
            key={format}
            className={`card-genora cursor-pointer transition-all duration-200 hover:scale-105 ${
              exportFormat === format ? 'ring-2 ring-[var(--neonAqua)]' : ''
            }`}
            onClick={() => setExportFormat(format)}
          >
            <div className="text-center">
              <div className="text-3xl mb-2">{getExportIcon(format)}</div>
              <h3 className="font-orbitron text-lg font-semibold text-white mb-2">
                {format.toUpperCase()}
              </h3>
              <p className="font-inter text-white/60 text-sm mb-4">
                {getExportDescription(format)}
              </p>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  exportData(format);
                }}
                disabled={isExporting}
                className="w-full px-4 py-2 bg-[var(--neonAqua)] text-black font-semibold rounded hover:bg-[var(--neonAqua)]/80 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isExporting ? 'Exporting...' : `Export ${format.toUpperCase()}`}
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="p-4 bg-[var(--graphiteGray)] rounded-lg border border-[var(--neonAqua)]/20">
        <h3 className="font-orbitron text-lg font-semibold text-[var(--neonAqua)] mb-3">
          Export Information
        </h3>
        <div className="space-y-2 text-sm text-white/80">
          <div className="flex justify-between">
            <span>Total Strategies:</span>
            <span className="font-spacemono">{strategies.length}</span>
          </div>
          <div className="flex justify-between">
            <span>Total TVL:</span>
            <span className="font-spacemono">
              ${(strategies.reduce((sum, s) => sum + (s.tvl_usd || 0), 0) / 1000000).toFixed(1)}M
            </span>
          </div>
          <div className="flex justify-between">
            <span>Average APY:</span>
            <span className="font-spacemono">
              {(strategies.reduce((sum, s) => sum + (s.apy || 0), 0) / strategies.length).toFixed(2)}%
            </span>
          </div>
          <div className="flex justify-between">
            <span>Last Updated:</span>
            <span className="font-spacemono">{new Date().toLocaleString('ru-RU')}</span>
          </div>
        </div>
      </div>

      <div className="mt-4 p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
        <div className="flex items-start space-x-2">
          <div className="text-yellow-400 text-lg">⚠️</div>
          <div className="text-sm text-yellow-200">
            <p className="font-semibold mb-1">Data Usage Notice</p>
            <p>Exported data is for personal use only. Please respect the terms of service of data providers (DeFiLlama, etc.) and do not redistribute without permission.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
