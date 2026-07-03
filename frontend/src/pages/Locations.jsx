import { useEffect, useState } from 'react'
import { api } from '../api'

export default function Locations() {
  const [locations, setLocations] = useState([])
  const [items, setItems] = useState([])
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [error, setError] = useState('')

  function load() {
    api.get('/locations').then(setLocations)
    api.get('/items').then(setItems)
  }
  useEffect(load, [])

  const count = (id) => items.filter((i) => i.location_id === id).length

  async function add(e) {
    e.preventDefault()
    setError('')
    try {
      await api.post('/locations', { name, description })
      setName(''); setDescription('')
      load()
    } catch (err) { setError(err.message) }
  }

  async function remove(loc) {
    setError('')
    try {
      await api.del(`/locations/${loc.id}`)
      load()
    } catch (err) { setError(err.message) }
  }

  return (
    <div>
      <h2>Locations</h2>
      <p className="muted">Named places where you keep tools — "Garage Pegboard", "Kitchen Drawer 2", "Toolbox top tray".</p>

      <form className="card inline-form" onSubmit={add}>
        <input placeholder="Location name" value={name} onChange={(e) => setName(e.target.value)} required />
        <input placeholder="Description (optional)" value={description} onChange={(e) => setDescription(e.target.value)} />
        <button className="btn primary">+ Add location</button>
      </form>
      {error && <div className="error">{error}</div>}

      <div className="cards">
        {locations.map((l) => (
          <div key={l.id} className="loc-card">
            <div>
              <div className="result-name">{l.name}</div>
              {l.description && <div className="muted small">{l.description}</div>}
              <div className="badge">{count(l.id)} tool(s)</div>
            </div>
            <button className="link-btn danger" onClick={() => remove(l)}>Delete</button>
          </div>
        ))}
        {locations.length === 0 && <div className="card empty">No locations yet.</div>}
      </div>
    </div>
  )
}
