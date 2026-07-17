// Helpers for Google + Apple sign-in on the web.
// Client IDs come from build-time env (see frontend/.env.example). When a
// provider's ID is absent, its button is hidden and the app still works.

export const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID || ''
export const appleClientId = import.meta.env.VITE_APPLE_CLIENT_ID || ''

export const googleConfigured = () => !!googleClientId
export const appleConfigured = () => !!appleClientId

const loaded = {}
function loadScript(src) {
  if (loaded[src]) return loaded[src]
  loaded[src] = new Promise((resolve, reject) => {
    const s = document.createElement('script')
    s.src = src
    s.async = true
    s.defer = true
    s.onload = resolve
    s.onerror = () => reject(new Error(`Failed to load ${src}`))
    document.head.appendChild(s)
  })
  return loaded[src]
}

/**
 * Render Google's official sign-in button into `el`. On success the callback
 * receives the ID-token credential string to POST to the backend.
 */
export async function renderGoogleButton(el, onCredential) {
  if (!googleConfigured()) return
  await loadScript('https://accounts.google.com/gsi/client')
  /* global google */
  google.accounts.id.initialize({
    client_id: googleClientId,
    callback: (resp) => onCredential(resp.credential),
  })
  google.accounts.id.renderButton(el, {
    theme: 'outline',
    size: 'large',
    width: el.clientWidth || 320,
    shape: 'pill',
    text: 'continue_with',
    logo_alignment: 'center',
  })
}

/**
 * Trigger Apple sign-in via a popup. Resolves with { identityToken, fullName }.
 */
export async function signInWithApple() {
  if (!appleConfigured()) throw new Error('Apple sign-in is not configured.')
  await loadScript(
    'https://appleid.cdn-apple.com/appleauth/static/jsapi/appleid/1/en_US/appleid.auth.js',
  )
  /* global AppleID */
  AppleID.auth.init({
    clientId: appleClientId,
    scope: 'name email',
    redirectURI: window.location.origin,
    usePopup: true,
  })
  const res = await AppleID.auth.signIn()
  const name = res.user
    ? [res.user.name?.firstName, res.user.name?.lastName].filter(Boolean).join(' ')
    : null
  return { identityToken: res.authorization.id_token, fullName: name }
}
