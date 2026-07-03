import { NavLink, Navigate, Route, Routes, useNavigate } from 'react-router-dom'
import { useAuth } from './auth'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Locations from './pages/Locations'
import Items from './pages/Items'
import Scan from './pages/Scan'
import Search from './pages/Search'
import Admin from './pages/Admin'

function Nav() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  return (
    <nav className="nav">
      <div className="brand">🔧 ToolFinder</div>
      <div className="nav-links">
        <NavLink to="/" end>Dashboard</NavLink>
        <NavLink to="/scan">📷 Scan</NavLink>
        <NavLink to="/search">🔍 Find</NavLink>
        <NavLink to="/items">Items</NavLink>
        <NavLink to="/locations">Locations</NavLink>
        {user?.role === 'admin' && <NavLink to="/admin">Admin</NavLink>}
      </div>
      <div className="nav-user">
        <span>{user?.display_name}</span>
        <button className="link-btn" onClick={() => { logout(); navigate('/login') }}>Log out</button>
      </div>
    </nav>
  )
}

function Protected({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="center muted">Loading…</div>
  if (!user) return <Navigate to="/login" replace />
  return (
    <>
      <Nav />
      <main className="container">{children}</main>
    </>
  )
}

export default function App() {
  const { user } = useAuth()
  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to="/" replace /> : <Login />} />
      <Route path="/" element={<Protected><Dashboard /></Protected>} />
      <Route path="/scan" element={<Protected><Scan /></Protected>} />
      <Route path="/search" element={<Protected><Search /></Protected>} />
      <Route path="/items" element={<Protected><Items /></Protected>} />
      <Route path="/locations" element={<Protected><Locations /></Protected>} />
      <Route path="/admin" element={<Protected><Admin /></Protected>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
