import { useEffect, useState } from 'react'
import { api } from '../api'

export default function Admin() {
  const [analytics, setAnalytics] = useState(null)
  const [users, setUsers] = useState([])
  const [error, setError] = useState('')

  useEffect(() => {
    api.get('/admin/analytics').then(setAnalytics).catch((e) => setError(e.message))
    api.get('/admin/users').then(setUsers).catch(() => {})
  }, [])

  if (error) return <div className="error">{error}</div>
  if (!analytics) return <div className="muted">Loading…</div>

  return (
    <div>
      <h2>Admin dashboard</h2>

      <div className="stats">
        <div className="stat"><div className="stat-num">{analytics.total_users}</div><div>Users</div></div>
        <div className="stat"><div className="stat-num">{analytics.total_items}</div><div>Items</div></div>
        <div className="stat"><div className="stat-num">{analytics.total_locations}</div><div>Locations</div></div>
        <div className="stat"><div className="stat-num">{analytics.total_photos}</div><div>Photos</div></div>
      </div>

      <div className="admin-grid">
        <div className="card">
          <h3>Items by status</h3>
          <ul className="kv">
            {Object.entries(analytics.items_by_status).map(([k, v]) => (
              <li key={k}><span>{k}</span><b>{v}</b></li>
            ))}
            {Object.keys(analytics.items_by_status).length === 0 && <li className="muted">No items yet</li>}
          </ul>
        </div>

        <div className="card">
          <h3>Likely duplicates</h3>
          <ul className="kv">
            {analytics.likely_duplicates.map((d, i) => (
              <li key={i}><span>{d.name}</span><b>×{d.count}</b></li>
            ))}
            {analytics.likely_duplicates.length === 0 && <li className="muted">None detected</li>}
          </ul>
        </div>

        <div className="card">
          <h3>Most common tools</h3>
          <ul className="kv">
            {analytics.most_common_items.map((d, i) => (
              <li key={i}><span>{d.name}</span><b>{d.count}</b></li>
            ))}
            {analytics.most_common_items.length === 0 && <li className="muted">No data</li>}
          </ul>
        </div>
      </div>

      <div className="card">
        <h3>Users ({users.length})</h3>
        <table className="table">
          <thead><tr><th>Name</th><th>Email</th><th>Role</th></tr></thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id}><td>{u.display_name}</td><td>{u.email}</td><td><span className="badge">{u.role}</span></td></tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
