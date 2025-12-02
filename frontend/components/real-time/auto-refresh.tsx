'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface AutoRefreshProps {
  onRefresh: () => Promise<void>;
  interval?: number; // in milliseconds
  enabled?: boolean;
}

export function AutoRefresh({ onRefresh, interval = 120000, enabled = true }: AutoRefreshProps) {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [nextUpdate, setNextUpdate] = useState<Date>(new Date(Date.now() + interval));
  const [timeLeft, setTimeLeft] = useState(interval);

  useEffect(() => {
    if (!enabled) return;

    const refreshData = async () => {
      setIsRefreshing(true);
      try {
        await onRefresh();
        setLastUpdate(new Date());
        setNextUpdate(new Date(Date.now() + interval));
        setTimeLeft(interval);
      } catch (error) {
        console.error('Auto-refresh failed:', error);
      } finally {
        setIsRefreshing(false);
      }
    };

    // Initial refresh
    refreshData();

    // Set up interval
    const intervalId = setInterval(refreshData, interval);

    // Set up countdown timer
    const countdownId = setInterval(() => {
      setTimeLeft(prev => {
        if (prev <= 1000) {
          return interval;
        }
        return prev - 1000;
      });
    }, 1000);

    return () => {
      clearInterval(intervalId);
      clearInterval(countdownId);
    };
  }, [onRefresh, interval, enabled]);

  const formatTime = (ms: number) => {
    const minutes = Math.floor(ms / 60000);
    const seconds = Math.floor((ms % 60000) / 1000);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const progress = ((interval - timeLeft) / interval) * 100;

  return (
    <motion.div 
      className="flex items-center space-x-4 text-sm"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.5 }}
    >
      <div className="flex items-center space-x-2">
        <motion.div
          className="w-3 h-3 rounded-full"
          animate={isRefreshing ? {
            scale: [1, 1.2, 1],
            opacity: [0.5, 1, 0.5]
          } : {
            scale: 1,
            opacity: enabled ? 1 : 0.3
          }}
          transition={{
            duration: 1,
            repeat: isRefreshing ? Infinity : 0,
            ease: "easeInOut"
          }}
          style={{
            backgroundColor: enabled ? (isRefreshing ? '#22d3ee' : '#10b981') : '#6b7280'
          }}
        />
        <span className={`${enabled ? 'text-white' : 'text-gray-500'}`}>
          {isRefreshing ? 'Updating...' : enabled ? 'Auto-refresh' : 'Auto-refresh off'}
        </span>
      </div>

      {enabled && (
        <div className="flex items-center space-x-2">
          <div className="w-16 h-2 bg-gray-700 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-cyan-500 to-fuchsia-500"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 1, ease: "linear" }}
            />
          </div>
          <span className="text-gray-400 font-mono text-xs">
            {formatTime(timeLeft)}
          </span>
        </div>
      )}

      <motion.button
        onClick={async () => {
          if (isRefreshing) return;
          setIsRefreshing(true);
          try {
            await onRefresh();
            setLastUpdate(new Date());
            setNextUpdate(new Date(Date.now() + interval));
            setTimeLeft(interval);
          } catch (error) {
            console.error('Manual refresh failed:', error);
          } finally {
            setIsRefreshing(false);
          }
        }}
        disabled={isRefreshing}
        className="px-3 py-1 text-xs bg-cyan-600/20 text-cyan-400 rounded hover:bg-cyan-600/30 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        {isRefreshing ? 'Refreshing...' : 'Refresh Now'}
      </motion.button>

      <AnimatePresence>
        {lastUpdate && (
          <motion.div
            className="text-xs text-gray-500"
            initial={{ opacity: 0, x: 10 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -10 }}
            key={lastUpdate.getTime()}
          >
            Last: {lastUpdate.toLocaleTimeString()}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

