import { useState } from 'react'
import { api, thumbUrl } from '../api'
import { IconSearch, IconPin, IconCheck, IconPlus } from '../icons'

const STATUS_LABEL = {
  available: 'Available', lent_out: 'Lent out', lost: 'Lost', needs_repair: 'Needs repair',
}
const STATUS_DOT = {
  available: 'ok', lent_out: 'warn', lost: 'bad', needs_repair: 'warn',
}

export default function Search() {
  const [q, setQ] = useState('')
  const [result, setResult] = useState(null)
  const [busy, setBusy] = useState(false)

  async function run(e) {
    e.preventDefault()
    if (!q.trim()) return
    setBusy(true)
    try {
      const r = await api.get(`/items/check?q=${encodeURIComponent(q)}`)
      setResult(r)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div>
      <h2 className="page-h"><span className="page-ic"><IconSearch width={22} height={22} /></span> Find a tool</h2>
      <p className="muted">Before you buy, check if you already own it. Ask in plain language, e.g. <em>"do I own a hammer?"</em></p>

      <form onSubmit={run} className="search-bar">
        <input placeholder="Search a tool…  e.g. hammer, cordless drill" value={q} onChange={(e) => setQ(e.target.value)} autoFocus />
        <button className="btn primary" disabled={busy}>{busy ? 'Checking…' : 'Check'}</button>
      </form>

      {result && (
        <div className={`verdict ${result.owned ? 'owned' : 'buy'}`}>
          <span className="verdict-ic">
            {result.owned ? <IconCheck width={26} height={26} /> : <IconPlus width={26} height={26} />}
          </span>
          <div>
            <div className="verdict-title">
              {result.owned ? `You already own this` : `Safe to buy`}
            </div>
            <div className="verdict-msg">{result.message}</div>
          </div>
        </div>
      )}

      <div className="cards">
        {result && result.matches.map((m) => (
          <div key={m.id} className="result-card">
            {m.photo_id && <img className="thumb" src={thumbUrl(m.photo_id)} alt="" loading="lazy" />}
            <div className="result-body">
              <div className="result-name">{m.name}{m.quantity > 1 ? ` ×${m.quantity}` : ''}</div>
              <div className="loc"><IconPin width={14} height={14} /> {m.location_name || 'No location set'}</div>
              <div className="status"><span className={`dot ${STATUS_DOT[m.status] || ''}`} />{STATUS_LABEL[m.status] || m.status}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
