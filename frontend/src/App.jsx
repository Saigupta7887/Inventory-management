import { NavLink, Navigate, Route, Routes, useNavigate } from 'react-router-dom'
import { useAuth } from './auth'
import { Logo, IconGrid, IconCamera, IconSearch, IconBox, IconPin, IconSpark, IconLogout, IconGuide } from './icons'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Locations from './pages/Locations'
import Items from './pages/Items'
import Scan from './pages/Scan'
import Search from './pages/Search'
import Guide from './pages/Guide'
import Admin from './pages/Admin'

function Nav() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const link = (to, Icon, label, end) => (
    <NavLink to={to} end={end}>
      <Icon width={17} height={17} /> <span>{label}</span>
    </NavLink>
  )
  return (
    <nav className="nav">
      <div className="brand"><Logo size={28} /> <span>ToolFinder</span></div>
      <div className="nav-links">
        {link('/', IconGrid, 'Dashboard', true)}
        {link('/scan', IconCamera, 'Scan')}
        {link('/search', IconSearch, 'Find')}
        {link('/guide', IconGuide, 'How-to')}
        {link('/items', IconBox, 'Items')}
        {link('/locations', IconPin, 'Locations')}
        {user?.role === 'admin' && link('/admin', IconSpark, 'Admin')}
      </div>
      <div className="nav-user">
        <span className="avatar">{(user?.display_name || '?').slice(0, 1).toUpperCase()}</span>
        <button className="link-btn logout" onClick={() => { logout(); navigate('/login') }} title="Log out">
          <IconLogout width={18} height={18} />
        </button>
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
      <Route path="/guide" element={<Protected><Guide /></Protected>} />
      <Route path="/items" element={<Protected><Items /></Protected>} />
      <Route path="/locations" element={<Protected><Locations /></Protected>} />
      <Route path="/admin" element={<Protected><Admin /></Protected>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
