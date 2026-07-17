// Thin fetch wrapper. Talks to the backend through the Vite /api proxy.
const BASE = '/api'

export function getToken() {
  return localStorage.getItem('token')
}
export function setToken(t) {
  if (t) localStorage.setItem('token', t)
  else localStorage.removeItem('token')
}

// Short-lived, read-only token used only in image URLs (keeps the session
// token out of URLs / logs / history).
export function getMediaToken() {
  return localStorage.getItem('media_token')
}
export function setMediaToken(t) {
  if (t) localStorage.setItem('media_token', t)
  else localStorage.removeItem('media_token')
}
export async function refreshMediaToken() {
  try {
    const { access_token } = await api.post('/auth/media-token')
    setMediaToken(access_token)
    return access_token
  } catch {
    return null
  }
}

async function request(method, path, { body, form } = {}) {
  const headers = {}
  const token = getToken()
  if (token) headers.Authorization = `Bearer ${token}`
  let payload
  if (form) {
    payload = form // FormData; browser sets multipart headers
  } else if (body !== undefined) {
    headers['Content-Type'] = 'application/json'
    payload = JSON.stringify(body)
  }
  const res = await fetch(BASE + path, { method, headers, body: payload })
  if (res.status === 204) return null
  const text = await res.text()
  const data = text ? JSON.parse(text) : null
  if (!res.ok) {
    const detail = data && data.detail ? data.detail : res.statusText
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail))
  }
  return data
}

export const api = {
  get: (p) => request('GET', p),
  post: (p, body) => request('POST', p, { body }),
  patch: (p, body) => request('PATCH', p, { body }),
  del: (p) => request('DELETE', p),
  upload: (p, form) => request('POST', p, { form }),
}

// URL for showing a photo in an <img>. Uses the short-lived media token.
export function photoUrl(photoId) {
  return `${BASE}/photos/${photoId}/file?t=${encodeURIComponent(getMediaToken() || '')}`
}

// Small thumbnail variant — much lighter for grids and cards.
export function thumbUrl(photoId) {
  return `${BASE}/photos/${photoId}/thumb?t=${encodeURIComponent(getMediaToken() || '')}`
}
