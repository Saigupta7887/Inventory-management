import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import { useAuth } from '../auth'

export default function Dashboard() {
  const { user } = useAuth()
  const [items, setItems] = useState([])
  const [locations, setLocations] = useState([])

  useEffect(() => {
    api.get('/items').then(setItems).catch(() => {})
    api.get('/locations').then(setLocations).catch(() => {})
  }, [])

  const byStatus = items.reduce((acc, i) => ({ ...acc, [i.status]: (acc[i.status] || 0) + 1 }), {})

  return (
    <div>
      <h2>Welcome back, {user?.display_name} 👋</h2>
      <p className="muted">Your personal tool inventory. Snap, find, and stop buying duplicates.</p>

      <div className="stats">
        <div className="stat"><div className="stat-num">{items.length}</div><div>Tools</div></div>
        <div className="stat"><div className="stat-num">{locations.length}</div><div>Locations</div></div>
        <div className="stat"><div className="stat-num">{byStatus.available || 0}</div><div>Available</div></div>
        <div className="stat"><div className="stat-num">{byStatus.lent_out || 0}</div><div>Lent out</div></div>
      </div>

      <div className="quick">
        <Link to="/scan" className="quick-card">
          <div className="dz-icon">📷</div><h3>Scan a location</h3>
          <p className="muted small">Photograph a desk or drawer and let AI list the tools.</p>
        </Link>
        <Link to="/search" className="quick-card">
          <div className="dz-icon">🔍</div><h3>Find a tool</h3>
          <p className="muted small">Ask "where is my hammer?" and get the location.</p>
        </Link>
        <Link to="/items" className="quick-card">
          <div className="dz-icon">🧰</div><h3>Manage inventory</h3>
          <p className="muted small">Add, move, lend, or retire tools by hand.</p>
        </Link>
      </div>
    </div>
  )
}
