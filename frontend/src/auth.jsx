import { createContext, useContext, useEffect, useState } from 'react'
import { api, setToken, getToken } from './api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  async function refresh() {
    if (!getToken()) {
      setUser(null)
      setLoading(false)
      return
    }
    try {
      const me = await api.get('/auth/me')
      setUser(me)
    } catch {
      setToken(null)
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    refresh()
  }, [])

  async function login(email, password) {
    const { access_token } = await api.post('/auth/login', { email, password })
    setToken(access_token)
    await refresh()
  }

  async function signup(email, password, display_name) {
    const { access_token } = await api.post('/auth/signup', { email, password, display_name })
    setToken(access_token)
    await refresh()
  }

  function logout() {
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
