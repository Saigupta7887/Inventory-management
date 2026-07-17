// Browser notifications for reminders. True scheduled push (when the app is
// closed) needs a push server or the native app; this surfaces reminders while
// the app is open, plus an in-app bell panel. The plumbing is structured so a
// native/push backend can slot in later.

const ENABLED_KEY = 'bondly_notify'
const LAST_KEY = 'bondly_notify_last' // ISO date string, throttles to once/day

export function notifySupported() {
  return typeof window !== 'undefined' && 'Notification' in window
}

export function notifyEnabled() {
  return localStorage.getItem(ENABLED_KEY) === '1' && permission() === 'granted'
}

export function permission() {
  return notifySupported() ? Notification.permission : 'denied'
}

export async function enableNotifications() {
  if (!notifySupported()) return 'unsupported'
  let p = Notification.permission
  if (p === 'default') p = await Notification.requestPermission()
  if (p === 'granted') localStorage.setItem(ENABLED_KEY, '1')
  return p
}

export function disableNotifications() {
  localStorage.removeItem(ENABLED_KEY)
}

function show(title, body) {
  try {
    new Notification(title, {
      body,
      icon: '/icons/icon-192.png',
      badge: '/icons/icon-192.png',
      tag: 'bondly-reminders',
    })
  } catch {
    /* ignore */
  }
}

/**
 * Given today's reminders, surface a summary notification — at most once per
 * calendar day so it never nags.
 */
export function maybeNotifyReminders(reminders) {
  if (!notifyEnabled() || !reminders?.length) return
  const today = new Date().toDateString()
  if (localStorage.getItem(LAST_KEY) === today) return
  localStorage.setItem(LAST_KEY, today)

  const n = reminders.length
  const first = reminders[0]
  const body =
    n === 1
      ? first.message
      : `${first.message} …and ${n - 1} more ${n - 1 === 1 ? 'person' : 'people'} to reconnect with.`
  show(n === 1 ? 'Bondly reminder' : `${n} people need attention`, body)
}
