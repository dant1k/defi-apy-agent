'use client'

import { useEffect, useState } from 'react'
import { LineChart, Line, ResponsiveContainer } from 'recharts'
import Link from 'next/link'

type Strategy = {
  id: string
  protocol: string
  name: string
  chain: string
  apy: number
  tvl_usd: number
  tvl_growth_24h?: number
  tvl_history?: number[]
  url: string
  icon_url?: string
  token_pair?: string
}

export default function TrendingPage() {
  const [strategies, setStrategies] = useState<Strategy[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadData = async () => {
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/strategies`)
      const data = await res.json()
      const items = Array.isArray(data?.items) ? data.items : []
      setStrategies(items.filter((s: any) => s.tvl_growth_24h > 10))
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
    const interval = setInterval(loadData, 30000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="app-shell">
      <header>
        <h1>🔥 Top Trending Pools</h1>
        <p>Fastest growing strategies (TVL +10%/24h)</p>
      </header>

      <nav className="nav-tabs">
        <Link href="/" className="nav-tab">All Strategies</Link>
        <Link href="/trending" className="nav-tab is-active">🔥 Top Trending</Link>
      </nav>

      {loading && <div className="empty-state">Loading...</div>}
      {error && <div className="error-card">Error: {error}</div>}

      {!loading && !error && (
        <div className="strategy-table">
          <div className="table-meta">
            Showing {strategies.length} pools • Auto refresh 30s
          </div>
          <table>
            <thead>
              <tr>
                <th>Protocol</th>
                <th>Pair</th>
                <th>APY</th>
                <th>TVL</th>
                <th>24h Growth</th>
                <th>Trend</th>
                <th>Chain</th>
                <th>Link</th>
              </tr>
            </thead>
            <tbody>
              {strategies.map((s) => {
                const color =
                  s.tvl_history && s.tvl_history.length > 1
                    ? s.tvl_history[s.tvl_history.length - 1] - s.tvl_history[0] >= 0
                      ? '#4ade80'
                      : '#ef4444'
                    : '#9ca3af'

                return (
                  <tr key={s.id}>
                    <td className="strategy-name">
                      {s.icon_url ? (
                        <img src={s.icon_url} alt={s.protocol} />
                      ) : (
                        <div className="strategy-avatar strategy-avatar--badge">
                          {s.protocol?.[0]?.toUpperCase() || '?'}
                        </div>
                      )}
                      <div>
                        <div className="strategy-card__name">{s.protocol}</div>
                        <div className="token-pair">{s.name}</div>
                      </div>
                    </td>
                    <td>{s.token_pair || '—'}</td>
                    <td>{s.apy?.toFixed(2)}%</td>
                    <td>${s.tvl_usd?.toLocaleString()}</td>
                    <td className="positive">{s.tvl_growth_24h?.toFixed(2)}%</td>
                    <td>
                      {s.tvl_history && s.tvl_history.length > 1 ? (
                        <div style={{ width: 100, height: 40 }}>
                          <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={s.tvl_history.map((v, i) => ({ i, v }))}>
                              <Line dataKey="v" stroke={color} strokeWidth={2} dot={false} />
                            </LineChart>
                          </ResponsiveContainer>
                        </div>
                      ) : (
                        '—'
                      )}
                    </td>
                    <td>{s.chain}</td>
                    <td>
                      <a href={s.url} target="_blank" rel="noopener noreferrer">Open</a>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}