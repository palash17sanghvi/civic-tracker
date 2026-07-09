import { useEffect, useState } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000/api'

function partyClass(party) {
  if (!party) return 'party-independent'
  const p = party.toLowerCase()
  if (p.includes('democrat')) return 'party-democratic'
  if (p.includes('republican')) return 'party-republican'
  if (p.includes('libertarian')) return 'party-libertarian'
  return 'party-independent'
}

function formatMoney(value, compact = false) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
    notation: compact ? 'compact' : 'standard',
  }).format(value)
}

function useApi(path) {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    fetch(`${API_BASE}${path}`)
      .then((res) => {
        if (!res.ok) throw new Error(`Request failed (${res.status})`)
        return res.json()
      })
      .then((json) => {
        if (!cancelled) {
          setData(json)
          setLoading(false)
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err.message)
          setLoading(false)
        }
      })
    return () => {
      cancelled = true
    }
  }, [path])

  return { data, error, loading }
}

function Skeleton({ rows = 5 }) {
  return (
    <div className="group">
      {Array.from({ length: rows }).map((_, i) => (
        <div className="skeleton-row" key={i}>
          <div className="skeleton-bar" style={{ width: 26, height: 26, borderRadius: 8 }} />
          <div style={{ flex: 1 }}>
            <div className="skeleton-bar" style={{ width: '55%', marginBottom: 6 }} />
            <div className="skeleton-bar" style={{ width: '30%', height: 8 }} />
          </div>
          <div className="skeleton-bar" style={{ width: 60 }} />
        </div>
      ))}
    </div>
  )
}

function Section({ title, count, children }) {
  return (
    <div className="section">
      <div className="section-header">
        <div className="section-title">{title}</div>
        {count != null && <div className="section-count">{count}</div>}
      </div>
      {children}
    </div>
  )
}

function TopFundraisers() {
  const { data, error, loading } = useApi('/insights/top-fundraisers/')

  if (loading) return <Skeleton />
  if (error) return <div className="state error">Couldn't load fundraising data.</div>

  return (
    <div className="group">
      {data.map((m, i) => (
        <div className="row" key={i}>
          <div className="row-left">
            <div className="rank-badge">{i + 1}</div>
            <div className="row-text">
              <div className="row-name">
                {m.first_name} {m.last_name}
              </div>
              <span className={`party-tag ${partyClass(m.party)}`}>{m.party}</span>
            </div>
          </div>
          <div className="row-right">
            <div className="row-value">{formatMoney(m.donor__total_receipts, true)}</div>
            <div className="row-value-sub">
              {m.bills_sponsored} bill{m.bills_sponsored === 1 ? '' : 's'}
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

function PartyAverages() {
  const { data, error, loading } = useApi('/insights/party-averages/')

  if (loading)
    return (
      <div className="stat-grid">
        {Array.from({ length: 3 }).map((_, i) => (
          <div className="stat-card" key={i}>
            <div className="skeleton-bar" style={{ width: '50%', height: 10 }} />
            <div className="skeleton-bar" style={{ width: '70%', height: 20, margin: '8px 0' }} />
            <div className="skeleton-bar" style={{ width: '40%', height: 8 }} />
          </div>
        ))}
      </div>
    )
  if (error) return <div className="state error">Couldn't load party data.</div>

  return (
    <div className="stat-grid">
      {data.map((p, i) => (
        <div className="stat-card" key={i}>
          <span className={`party-tag ${partyClass(p.member__party)}`}>
            {p.member__party}
          </span>
          <div className="value">{formatMoney(p.avg_receipts, true)}</div>
          <div className="row-sub">{p.num_members} members avg.</div>
        </div>
      ))}
    </div>
  )
}

function TopSponsors() {
  const { data, error, loading } = useApi('/insights/top-sponsors/')

  if (loading) return <Skeleton />
  if (error) return <div className="state error">Couldn't load sponsorship data.</div>

  return (
    <div className="group">
      {data.map((m, i) => (
        <div className="row" key={i}>
          <div className="row-left">
            <div className="rank-badge">{i + 1}</div>
            <div className="row-text">
              <div className="row-name">
                {m.first_name} {m.last_name}
              </div>
              <span className={`party-tag ${partyClass(m.party)}`}>{m.party}</span>
            </div>
          </div>
          <div className="row-right">
            <div className="row-value">{m.bills_sponsored}</div>
            <div className="row-value-sub">bill{m.bills_sponsored === 1 ? '' : 's'}</div>
          </div>
        </div>
      ))}
    </div>
  )
}

export default function App() {
  const [lastUpdated, setLastUpdated] = useState(null)

  useEffect(() => {
    setLastUpdated(new Date())
  }, [])

  return (
    <div className="app">
      <div className="navbar">
        <div className="navbar-title">Civic tracker</div>
        <div className="navbar-sub">
          <span className="live-dot" aria-hidden="true" />
          {lastUpdated
            ? `Updated ${lastUpdated.toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit',
              })}`
            : 'Loading…'}
        </div>
      </div>

      <div className="content">
        <Section title="Top fundraisers">
          <TopFundraisers />
        </Section>

        <Section title="Average fundraising by party">
          <PartyAverages />
        </Section>

        <Section title="Most active sponsors">
          <TopSponsors />
        </Section>

        <div className="footer-note">Congress and FEC data, refreshed every 6 hours</div>
      </div>
    </div>
  )
}
