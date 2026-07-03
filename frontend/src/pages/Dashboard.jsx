import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import { useAuth } from '../auth'
import { IconBox, IconPin, IconCheck, IconArrow, IconCamera, IconSearch, IconWrench } from '../icons'

export default function Dashboard() {
  const { user } = useAuth()
  const [items, setItems] = useState([])
  const [locations, setLocations] = useState([])

  useEffect(() => {
    api.get('/items').then(setItems).catch(() => {})
    api.get('/locations').then(setLocations).catch(() => {})
  }, [])

  const byStatus = items.reduce((acc, i) => ({ ...acc, [i.status]: (acc[i.status] || 0) + 1 }), {})

  const stats = [
    { icon: IconBox, num: items.length, label: 'Tools' },
    { icon: IconPin, num: locations.length, label: 'Locations' },
    { icon: IconCheck, num: byStatus.available || 0, label: 'Available' },
    { icon: IconArrow, num: byStatus.lent_out || 0, label: 'Lent out' },
  ]
  const actions = [
    { to: '/scan', icon: IconCamera, title: 'Scan a location', desc: 'Photograph a desk or drawer and let AI list the tools.' },
    { to: '/search', icon: IconSearch, title: 'Find a tool', desc: 'Ask “where is my hammer?” and get the location.' },
    { to: '/items', icon: IconWrench, title: 'Manage inventory', desc: 'Add, move, lend, or retire tools by hand.' },
  ]

  return (
    <div>
      <div className="hero-banner">
        <div>
          <div className="eyebrow">Your workshop, organized</div>
          <h2>Welcome back, {user?.display_name?.split(' ')[0]}</h2>
          <p className="muted">Snap, find, and stop buying duplicates.</p>
        </div>
        <Link to="/scan" className="btn primary lg"><IconCamera width={18} height={18} /> Scan a location</Link>
      </div>

      <div className="stats">
        {stats.map((s) => (
          <div className="stat" key={s.label}>
            <span className="stat-ic"><s.icon width={20} height={20} /></span>
            <div className="stat-num">{s.num}</div>
            <div className="stat-label">{s.label}</div>
          </div>
        ))}
      </div>

      <div className="quick">
        {actions.map((a) => (
          <Link to={a.to} className="quick-card" key={a.to}>
            <span className="tile"><a.icon width={22} height={22} /></span>
            <h3>{a.title}</h3>
            <p className="muted small">{a.desc}</p>
            <span className="quick-go"><IconArrow width={18} height={18} /></span>
          </Link>
        ))}
      </div>
    </div>
  )
}
