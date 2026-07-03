import { useState } from 'react'
import { api, photoUrl } from '../api'

const STATUS_LABEL = {
  available: '🟢 Available', lent_out: '🟡 Lent out', lost: '🔴 Lost', needs_repair: '🛠️ Needs repair',
}

export default function Search() {
  const [q, setQ] = useState('')
  const [results, setResults] = useState(null)
  const [busy, setBusy] = useState(false)

  async function run(e) {
    e.preventDefault()
    setBusy(true)
    try {
      const r = await api.get(`/search?q=${encodeURIComponent(q)}`)
      setResults(r)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div>
      <h2>🔍 Find a tool</h2>
      <p className="muted">Ask in plain language, e.g. <em>"where is my hammer?"</em></p>
      <form onSubmit={run} className="search-bar">
        <input placeholder="where is my…" value={q} onChange={(e) => setQ(e.target.value)} autoFocus />
        <button className="btn primary" disabled={busy}>{busy ? '…' : 'Search'}</button>
      </form>

      {results && results.length === 0 && (
        <div className="card empty">
          <p>No matching tool found. 🎉 You probably don't own one — safe to buy it.</p>
        </div>
      )}

      <div className="cards">
        {results && results.map((r) => (
          <div key={r.item.id} className="result-card">
            {r.photo_id && <img className="thumb" src={photoUrl(r.photo_id)} alt="" />}
            <div className="result-body">
              <div className="result-name">{r.item.name}</div>
              <div className="muted">{r.category_name || 'Uncategorized'}</div>
              <div className="loc">📍 {r.location_name || 'No location set'}</div>
              <div className="status">{STATUS_LABEL[r.item.status] || r.item.status}
                {r.item.status === 'lent_out' && r.item.lent_to ? ` — ${r.item.lent_to}` : ''}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
