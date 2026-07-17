import { defineStore } from 'pinia'
import client from '@/api/client'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('bondly_token') || null,
    user: null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
  },
  actions: {
    _setToken(token) {
      this.token = token
      localStorage.setItem('bondly_token', token)
    },
    async register(email, password, fullName) {
      const { data } = await client.post('/api/auth/register', {
        email,
        password,
        full_name: fullName,
      })
      this._setToken(data.access_token)
      this.user = data.user
      return data.user
    },
    async login(email, password) {
      // OAuth2 password flow expects form-encoded username/password.
      const form = new URLSearchParams()
      form.append('username', email)
      form.append('password', password)
      const { data } = await client.post('/api/auth/login', form)
      this._setToken(data.access_token)
      this.user = data.user
      return data.user
    },
    async fetchMe() {
      if (!this.token) return null
      const { data } = await client.get('/api/auth/me')
      this.user = data
      return data
    },
    async savePreferences(prefs) {
      const { data } = await client.patch('/api/auth/me', prefs)
      this.user = data
      return data
    },
    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('bondly_token')
    },
  },
})
