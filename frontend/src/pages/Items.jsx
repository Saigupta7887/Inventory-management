import { useEffect, useState } from 'react'
import { api, photoUrl } from '../api'

const STATUSES = ['available', 'lent_out', 'lost', 'needs_repair']
const STATUS_LABEL = { available: 'Available', lent_out: 'Lent out', lost: 'Lost', needs_repair: 'Needs repair' }

export default function Items() {
  const [items, setItems] = useState([])
  const [locations, setLocations] = useState([])
  const [categories, setCategories] = useState([])
  const [filter, setFilter] = useState('')
  const [adding, setAdding] = useState(false)
  const [form, setForm] = useState({ name: '', category_id: '', location_id: '' })

  function load() {
    api.get('/items').then(setItems)
  }
  useEffect(() => {
    load()
    api.get('/locations').then(setLocations)
    api.get('/categories').then(setCategories)
  }, [])

  const locName = (id) => locations.find((l) => l.id === id)?.name
  const catName = (id) => categories.find((c) => c.id === id)?.name

  async function addItem(e) {
    e.preventDefault()
    await api.post('/items', {
      name: form.name,
      category_id: form.category_id || null,
      location_id: form.location_id || null,
    })
    setForm({ name: '', category_id: '', location_id: '' })
    setAdding(false)
    load()
  }

  async function changeStatus(item, status) {
    let lent_to = item.lent_to
    if (status === 'lent_out') lent_to = prompt('Lent to whom?', item.lent_to || '') || ''
    await api.patch(`/items/${item.id}`, { status, lent_to })
    load()
  }

  async function move(item, location_id) {
    await api.patch(`/items/${item.id}`, { location_id: location_id || null })
    load()
  }

  async function remove(item) {
    if (!confirm(`Delete "${item.name}"?`)) return
    await api.del(`/items/${item.id}`)
    load()
  }

  const shown = filter ? items.filter((i) => i.status === filter) : items

  return (
    <div>
      <div className="head-row">
        <h2>My tools ({items.length})</h2>
        <button className="btn primary" onClick={() => setAdding(!adding)}>{adding ? 'Close' : '+ Add tool'}</button>
      </div>

      {adding && (
        <form className="card inline-form" onSubmit={addItem}>
          <input placeholder="Tool name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
          <select value={form.category_id} onChange={(e) => setForm({ ...form, category_id: e.target.value })}>
            <option value="">Category…</option>
            {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
          <select value={form.location_id} onChange={(e) => setForm({ ...form, location_id: e.target.value })}>
            <option value="">Location…</option>
            {locations.map((l) => <option key={l.id} value={l.id}>{l.name}</option>)}
          </select>
          <button className="btn primary">Add</button>
        </form>
      )}

      <div className="filters">
        <button className={!filter ? 'chip active' : 'chip'} onClick={() => setFilter('')}>All</button>
        {STATUSES.map((s) => (
          <button key={s} className={filter === s ? 'chip active' : 'chip'} onClick={() => setFilter(s)}>{STATUS_LABEL[s]}</button>
        ))}
      </div>

      {shown.length === 0 && <div className="card empty">No tools yet. Try the 📷 Scan page to add some fast.</div>}

      <div className="cards">
        {shown.map((item) => (
          <div key={item.id} className="item-card">
            {item.primary_photo_id && <img className="thumb" src={photoUrl(item.primary_photo_id)} alt="" />}
            <div className="item-body">
              <div className="result-name">{item.name}</div>
              <div className="muted small">{catName(item.category_id) || 'Uncategorized'}</div>
              <div className="loc small">📍 {locName(item.location_id) || 'No location'}</div>
              <div className="controls">
                <select value={item.status} onChange={(e) => changeStatus(item, e.target.value)}>
                  {STATUSES.map((s) => <option key={s} value={s}>{STATUS_LABEL[s]}</option>)}
                </select>
                <select value={item.location_id || ''} onChange={(e) => move(item, e.target.value)}>
                  <option value="">No location</option>
                  {locations.map((l) => <option key={l.id} value={l.id}>{l.name}</option>)}
                </select>
                <button className="link-btn danger" onClick={() => remove(item)}>Delete</button>
              </div>
              {item.status === 'lent_out' && item.lent_to && <div className="badge">Lent to {item.lent_to}</div>}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
