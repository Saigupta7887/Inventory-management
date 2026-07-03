import { useState } from 'react'
import { useAuth } from '../auth'
import { Logo, IconCamera, IconSearch, IconBox } from '../icons'

export default function Login() {
  const { login, signup } = useAuth()
  const [mode, setMode] = useState('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function submit(e) {
    e.preventDefault()
    setError('')
    setBusy(true)
    try {
      if (mode === 'login') await login(email, password)
      else await signup(email, password, name)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="auth-split">
      <aside className="auth-hero">
        <div className="auth-hero-inner">
          <div className="hero-brand"><Logo size={40} /> <span>ToolFinder</span></div>
          <h1 className="hero-title">Never buy the same tool twice.</h1>
          <p className="hero-sub">Snap a photo of any drawer, shelf or pegboard. AI catalogs every tool and remembers exactly where it lives — so you find it in seconds.</p>
          <ul className="hero-feats">
            <li><span className="hf-ic"><IconCamera width={18} height={18} /></span> Photo-to-inventory with AI vision</li>
            <li><span className="hf-ic"><IconSearch width={18} height={18} /></span> Ask "where is my hammer?"</li>
            <li><span className="hf-ic"><IconBox width={18} height={18} /></span> One tidy home for every tool</li>
          </ul>
        </div>
      </aside>

      <div className="auth-panel">
        <div className="auth-card">
          <h2 className="auth-h">{mode === 'login' ? 'Welcome back' : 'Create your account'}</h2>
          <p className="muted auth-p">{mode === 'login' ? 'Log in to your tool library.' : 'Start cataloging in under a minute.'}</p>

          <div className="tabs">
            <button className={mode === 'login' ? 'active' : ''} onClick={() => setMode('login')}>Log in</button>
            <button className={mode === 'signup' ? 'active' : ''} onClick={() => setMode('signup')}>Sign up</button>
          </div>

          <form onSubmit={submit}>
            {mode === 'signup' && (
              <input placeholder="Your name" value={name} onChange={(e) => setName(e.target.value)} required />
            )}
            <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required />
            <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required />
            {error && <div className="error">{error}</div>}
            <button className="btn primary block" disabled={busy}>
              {busy ? 'One moment…' : mode === 'login' ? 'Log in' : 'Create account'}
            </button>
          </form>

          <div className="hint">Demo admin · <code>admin@example.com</code> · <code>admin1234</code></div>
        </div>
      </div>
    </div>
  )
}
