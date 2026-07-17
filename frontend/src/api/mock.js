// In-memory mock API used only for the hosted demo build (VITE_DEMO=1).
// It mirrors the FastAPI backend closely enough to click through the whole app
// — including the voice assistant — with no server. Not used in real builds.

const now = () => new Date()
const iso = (d) => d.toISOString()
const daysAgoISO = (n) => iso(new Date(Date.now() - n * 86400000))

const db = {
  seq: 1,
  user: {
    id: 1,
    email: 'demo@bondly.app',
    full_name: 'Susmitha G',
    provider: 'email',
    avatar_url: null,
    reminder_style: 'balanced',
    ai_suggestions_enabled: true,
    onboarded: true,
    created_at: iso(now()),
  },
  people: [],
  notes: [],
  interactions: [],
  errands: [],
  places: [],
  reminderStates: {}, // `${personId}:${kind}` -> {status, snoozed_until, completed_at}
}
const nextId = () => ++db.seq

function seed() {
  const P = [
    ['Sarah Johnson', 'friend', 'high', 7, '2000-11-12', 'coffee, hiking', 'San Francisco', 21, 37.7793, -122.4192],
    ['Nikhil Sharma', 'work', 'medium', 15, null, 'mentor, cricket', 'Bangalore', 15, null, null],
    ['Priya Mehta', 'friend', 'medium', 30, '1998-05-04', 'best friend', 'Mumbai', 32, null, null],
    ['Ananya Iyer', 'family', 'high', 14, null, 'cousin', 'Chennai', 45, null, null],
    ['Rohan Verma', 'friend', 'low', 60, '2001-05-02', 'college', 'Pune', 62, null, null],
    ['Michael Lee', 'mentor', 'medium', 30, null, 'design mentor', 'Seattle', 10, null, null],
  ]
  for (const [name, rel, prio, intv, bday, tags, loc, last, lat, lng] of P) {
    const id = nextId()
    const handle = name.toLowerCase().split(' ')[0]
    db.people.push({
      id, owner_id: 1, name, nickname: null, relationship_type: rel,
      phone: '+15550' + (100 + id), email: `${handle}@example.com`,
      birthday: bday, priority: prio, preferred_contact_method: null,
      reminder_interval_days: intv, tags, location_label: loc, latitude: lat, longitude: lng,
      last_interaction_at: daysAgoISO(last), created_at: daysAgoISO(120),
    })
    db.interactions.push({
      id: nextId(), person_id: id, channel: 'call', summary: 'Caught up about life',
      mood: 'positive', follow_up: null, occurred_at: daysAgoISO(last),
    })
  }
  const byName = (n) => db.people.find((p) => p.name.startsWith(n)).id
  const addNote = (pid, content, pinned) =>
    db.notes.push({ id: nextId(), person_id: pid, content, category: categorize(content), pinned, created_at: daysAgoISO(5) })
  addNote(byName('Sarah'), 'Product Manager at Amazon', true)
  addNote(byName('Sarah'), 'Loves matcha lattes', true)
  addNote(byName('Sarah'), 'Enjoys hiking and yoga', false)
  addNote(byName('Sarah'), 'Moving to Seattle in July', false)
  addNote(byName('Nikhil'), 'Preparing for interviews', false)
  addNote(byName('Priya'), 'Sister is getting married in December', true)
  db.errands.push({ id: nextId(), owner_id: 1, person_id: byName('Sarah'), title: 'Pick up matcha', place_type: 'grocery', note: 'Ceremonial grade', completed: false, created_at: iso(now()) })
  db.places.push({ id: nextId(), owner_id: 1, name: 'Corner Market', place_type: 'grocery', address: null, latitude: 37.7794, longitude: -122.4191, created_at: iso(now()) })
}

// ---- logic mirrored from the backend --------------------------------------
const PREF = ['love', 'loves', 'likes', 'favorite', 'prefers', 'allergic']
const WORK = ['job', 'role', 'work', 'promotion', 'interview', 'startup', 'career']
const FOLLOW = ['preparing', 'planning', 'upcoming', 'next week', 'soon', 'will']
function categorize(t) {
  const s = t.toLowerCase()
  if (PREF.some((h) => s.includes(h))) return 'preference'
  if (WORK.some((h) => s.includes(h))) return 'work_update'
  if (FOLLOW.some((h) => s.includes(h))) return 'follow_up'
  return 'fact'
}
const daysSince = (p) => (p.last_interaction_at ? Math.floor((Date.now() - new Date(p.last_interaction_at)) / 86400000) : null)
function isOverdue(p) {
  const d = daysSince(p)
  if (d === null) return Math.floor((Date.now() - new Date(p.created_at)) / 86400000) >= p.reminder_interval_days
  return d >= p.reminder_interval_days
}
function daysUntilBirthday(p) {
  if (!p.birthday) return null
  const t = new Date(); t.setHours(0, 0, 0, 0)
  const [_, m, d] = p.birthday.split('-').map(Number)
  let next = new Date(t.getFullYear(), m - 1, d)
  if (next < t) next = new Date(t.getFullYear() + 1, m - 1, d)
  return Math.round((next - t) / 86400000)
}
const firstName = (p) => (p.nickname || p.name.split(' ')[0])
function suggestedQuestion(p) {
  const last = db.interactions.filter((i) => i.person_id === p.id).sort((a, b) => new Date(b.occurred_at) - new Date(a.occurred_at))[0]
  if (last?.follow_up) return `Ask ${firstName(p)}: ${last.follow_up}`
  if (last?.summary) return `Follow up with ${firstName(p)} about "${last.summary}".`
  return `Ask ${firstName(p)} how they've been lately.`
}
function draftMessage(p) {
  const last = db.interactions.filter((i) => i.person_id === p.id).sort((a, b) => new Date(b.occurred_at) - new Date(a.occurred_at))[0]
  if (last?.summary) return `Hey ${firstName(p)}, been thinking about our chat on ${last.summary}. How's it going?`
  return `Hey ${firstName(p)}! It's been a little while — how have you been?`
}
function reconnectMsg(p) {
  const d = daysSince(p)
  return d === null ? `You haven't logged any contact with ${firstName(p)} yet.` : `You haven't spoken to ${firstName(p)} in ${d} days.`
}
const haversine = (a, b, c, d) => {
  const R = 6371, r = (x) => (x * Math.PI) / 180
  const dl = r(c - a), dn = r(d - b)
  const x = Math.sin(dl / 2) ** 2 + Math.cos(r(a)) * Math.cos(r(c)) * Math.sin(dn / 2) ** 2
  return 2 * R * Math.asin(Math.sqrt(x))
}
const PLACE_TYPES = ['grocery', 'pharmacy', 'cafe', 'restaurant', 'gym', 'bookstore', 'other']

// ---- request router -------------------------------------------------------
const ok = (data, status = 200) => ({ data, status, statusText: 'OK', headers: {}, config: {} })
const person = (id) => db.people.find((p) => p.id === Number(id))
const errandOut = (e) => ({ ...e, person_name: e.person_id ? person(e.person_id)?.name : null })

function handle(method, path, body, params) {
  // Auth
  if (path === '/api/auth/providers') return ok({ google: false, apple: false })
  if (path === '/api/auth/register' || path === '/api/auth/login') return ok({ access_token: 'demo', token_type: 'bearer', user: db.user })
  if (path === '/api/auth/google' || path === '/api/auth/apple') return ok({ access_token: 'demo', token_type: 'bearer', user: db.user })
  if (path === '/api/auth/me') {
    if (method === 'patch') Object.assign(db.user, body)
    return ok(db.user)
  }

  // People
  if (path === '/api/people' && method === 'get') return ok(db.people)
  if (path === '/api/people' && method === 'post') {
    const p = { id: nextId(), owner_id: 1, nickname: null, phone: null, email: null, birthday: null, priority: 'medium', preferred_contact_method: null, reminder_interval_days: 30, tags: null, location_label: null, latitude: null, longitude: null, last_interaction_at: null, created_at: iso(now()), ...body }
    db.people.push(p); return ok(p, 201)
  }
  let m
  if ((m = path.match(/^\/api\/people\/(\d+)$/))) {
    const p = person(m[1])
    if (method === 'get') return ok(p)
    if (method === 'patch') { Object.assign(p, body); return ok(p) }
    if (method === 'delete') { db.people = db.people.filter((x) => x.id !== p.id); return ok(null, 204) }
  }
  if ((m = path.match(/^\/api\/people\/(\d+)\/notes$/))) {
    const pid = Number(m[1])
    if (method === 'get') return ok(db.notes.filter((n) => n.person_id === pid).sort((a, b) => b.pinned - a.pinned))
    if (method === 'post') {
      const n = { id: nextId(), person_id: pid, content: body.content, category: body.category || categorize(body.content), pinned: !!body.pinned, created_at: iso(now()) }
      db.notes.push(n); return ok(n, 201)
    }
  }
  if ((m = path.match(/^\/api\/people\/(\d+)\/interactions$/))) {
    const pid = Number(m[1])
    if (method === 'get') return ok(db.interactions.filter((i) => i.person_id === pid).sort((a, b) => new Date(b.occurred_at) - new Date(a.occurred_at)))
    if (method === 'post') {
      const when = body.occurred_at || iso(now())
      const i = { id: nextId(), person_id: pid, channel: body.channel || 'other', summary: body.summary || null, mood: body.mood || null, follow_up: body.follow_up || null, occurred_at: when }
      db.interactions.push(i); person(pid).last_interaction_at = when; return ok(i, 201)
    }
  }
  if ((m = path.match(/^\/api\/people\/(\d+)\/context-card$/))) {
    const p = person(m[1])
    const pinned = db.notes.filter((n) => n.person_id === p.id && n.pinned)
    return ok({ person_id: p.id, name: p.name, pinned_notes: pinned.map((n) => n.content), suggested_question: suggestedQuestion(p), draft_message: draftMessage(p) })
  }

  // Dashboard
  if (path === '/api/dashboard') {
    const na = db.people.filter(isOverdue).map((p) => ({ person_id: p.id, name: p.name, message: reconnectMsg(p), priority: p.priority }))
    const ev = db.people.map((p) => ({ person_id: p.id, name: p.name, days_until: daysUntilBirthday(p), type: 'birthday' })).filter((e) => e.days_until !== null && e.days_until <= 30).sort((a, b) => a.days_until - b.days_until)
    const recent = [...db.interactions].sort((a, b) => new Date(b.occurred_at) - new Date(a.occurred_at)).slice(0, 10)
    return ok({ total_people: db.people.length, needs_attention: na, upcoming_events: ev, recent_activity: recent, summary: { needs_attention_count: na.length, upcoming_events_count: ev.length } })
  }

  // Reminders
  const candidates = () => {
    const out = []
    for (const p of db.people) {
      if (isOverdue(p)) out.push({ person_id: p.id, person_name: p.name, kind: 'reconnect', message: reconnectMsg(p), priority: p.priority, days_since: daysSince(p) })
      const b = daysUntilBirthday(p)
      if (b !== null && b <= 14) out.push({ person_id: p.id, person_name: p.name, kind: 'birthday', message: b === 0 ? `${firstName(p)}'s birthday is today!` : `${firstName(p)}'s birthday is in ${b} days.`, priority: p.priority, days_until: b })
    }
    const rank = { very_high: 0, high: 1, medium: 2, low: 3 }
    out.sort((a, b) => (rank[a.priority] ?? 2) - (rank[b.priority] ?? 2))
    return out
  }
  const rstate = (pid, kind) => db.reminderStates[`${pid}:${kind}`]
  if (path === '/api/reminders' && method === 'get') {
    const nowMs = Date.now()
    return ok(candidates().filter((r) => {
      const s = rstate(r.person_id, r.kind)
      if (!s) return true
      if (s.status === 'completed') return false
      if (s.status === 'snoozed' && s.snoozed_until && new Date(s.snoozed_until) > nowMs) return false
      return true
    }))
  }
  if (path === '/api/reminders/snoozed') {
    const nowMs = Date.now()
    return ok(candidates().filter((r) => {
      const s = rstate(r.person_id, r.kind)
      return s && s.status === 'snoozed' && s.snoozed_until && new Date(s.snoozed_until) > nowMs
    }).map((r) => ({ ...r, snoozed_until: rstate(r.person_id, r.kind).snoozed_until })))
  }
  if (path === '/api/reminders/completed') {
    return ok(Object.entries(db.reminderStates)
      .filter(([, s]) => s.status === 'completed')
      .map(([key, s]) => { const [pid, kind] = key.split(':'); const p = person(Number(pid)); return p ? { person_id: p.id, person_name: p.name, kind, message: (kind === 'birthday' ? 'Birthday wishes sent' : 'Reconnected') + ' · ' + p.name, priority: p.priority, completed_at: s.completed_at } : null })
      .filter(Boolean))
  }
  if (path === '/api/reminders/snooze' && method === 'post') {
    const until = iso(new Date(Date.now() + Math.max(1, body.days || 3) * 86400000))
    db.reminderStates[`${body.person_id}:${body.kind}`] = { status: 'snoozed', snoozed_until: until, completed_at: null }
    return ok({ status: 'snoozed', snoozed_until: until })
  }
  if (path === '/api/reminders/complete' && method === 'post') {
    db.reminderStates[`${body.person_id}:${body.kind}`] = { status: 'completed', completed_at: iso(now()), snoozed_until: null }
    return ok({ status: 'completed' })
  }

  // Insights
  if (path === '/api/insights') {
    const status = (p) => { const d = daysSince(p), iv = p.reminder_interval_days || 30; if (d === null) return isOverdue(p) ? 'overdue' : 'healthy'; if (d >= iv * 2) return 'overdue'; if (d >= iv) return 'needs_attention'; return 'healthy' }
    const total = db.people.length || 1
    const cnt = { healthy: 0, needs_attention: 0, overdue: 0 }
    db.people.forEach((p) => cnt[status(p)]++)
    const bd = { healthy: Math.round(cnt.healthy / total * 100), needs_attention: Math.round(cnt.needs_attention / total * 100), overdue: Math.round(cnt.overdue / total * 100) }
    const weekAgo = Date.now() - 7 * 86400000
    const recent = db.interactions.filter((i) => new Date(i.occurred_at) >= weekAgo)
    const na = db.people.filter((p) => status(p) !== 'healthy').map((p) => ({ person_id: p.id, name: p.name, days_since: daysSince(p), priority: p.priority })).slice(0, 5)
    return ok({ health_score: bd.healthy, health_breakdown: bd, week: { people_contacted: new Set(recent.map((i) => i.person_id)).size, followups_completed: recent.filter((i) => i.follow_up).length, notes_added: db.notes.filter((n) => new Date(n.created_at) >= weekAgo).length }, people_by_type: {}, most_active: [], needs_attention: na, total_interactions: db.interactions.length })
  }

  // Search
  if (path === '/api/search') {
    const q = (params.q || '').toLowerCase()
    const stop = new Set(['who', 'what', 'likes', 'like', 'has', 'is', 'the', 'a', 'mentioned', 'about'])
    const kws = q.split(/\s+/).filter((w) => w.length > 1 && !stop.has(w))
    const hits = new Map()
    for (const kw of kws.length ? kws : [q]) {
      db.people.forEach((p) => { if ([p.name, p.nickname, p.tags].filter(Boolean).some((f) => f.toLowerCase().includes(kw))) hits.set(p.id, p) })
      db.notes.forEach((n) => { if (n.content.toLowerCase().includes(kw)) { const p = person(n.person_id); if (p) hits.set(p.id, p) } })
    }
    return ok({ query: params.q, keywords: kws, results: [...hits.values()].map((p) => ({ person_id: p.id, name: p.name, relationship_type: p.relationship_type, tags: p.tags })) })
  }

  // Errands / Places / Nearby
  if (path === '/api/errands' && method === 'get') return ok(db.errands.filter((e) => params.include_completed ? true : !e.completed).map(errandOut))
  if (path === '/api/errands' && method === 'post') { const e = { id: nextId(), owner_id: 1, person_id: body.person_id || null, title: body.title, place_type: body.place_type || 'other', note: body.note || null, completed: false, created_at: iso(now()) }; db.errands.push(e); return ok(errandOut(e), 201) }
  if ((m = path.match(/^\/api\/errands\/(\d+)$/)) && method === 'patch') { const e = db.errands.find((x) => x.id === Number(m[1])); Object.assign(e, body); return ok(errandOut(e)) }
  if (path === '/api/places' && method === 'get') return ok(db.places)
  if (path === '/api/places' && method === 'post') { const pl = { id: nextId(), owner_id: 1, address: null, latitude: null, longitude: null, place_type: 'other', created_at: iso(now()), ...body }; db.places.push(pl); return ok(pl, 201) }
  if (path === '/api/nearby/place-types') return ok(PLACE_TYPES)
  if (path === '/api/nearby/check-in') { const t = params.place_type; return ok({ place_type: t, errands: db.errands.filter((e) => e.place_type === t && !e.completed).map(errandOut), saved_places: db.places.filter((p) => p.place_type === t) }) }
  if (path === '/api/nearby') {
    const lat = Number(params.lat), lng = Number(params.lng), rad = Number(params.radius_km || 5)
    const np = db.places.filter((p) => p.latitude != null).map((p) => ({ place: p, distance_km: Math.round(haversine(lat, lng, p.latitude, p.longitude) * 100) / 100 })).filter((x) => x.distance_km <= rad).map((x) => ({ ...x, errands: db.errands.filter((e) => e.place_type === x.place.place_type && !e.completed).map(errandOut) })).sort((a, b) => a.distance_km - b.distance_km)
    const pe = db.people.filter((p) => p.latitude != null).map((p) => ({ person_id: p.id, name: p.name, location_label: p.location_label, distance_km: Math.round(haversine(lat, lng, p.latitude, p.longitude) * 100) / 100 })).filter((x) => x.distance_km <= rad).sort((a, b) => a.distance_km - b.distance_km)
    return ok({ location: { lat, lng }, radius_km: rad, nearby_places: np, nearby_people: pe, matched_place_types: [] })
  }

  return Promise.reject({ response: ok({ detail: 'Not found (demo)' }, 404) })
}

let seeded = false
export function mockAdapter(config) {
  if (!seeded) { seed(); seeded = true }
  const url = (config.url || '').split('?')[0]
  const method = (config.method || 'get').toLowerCase()
  let body = config.data
  if (typeof body === 'string') { try { body = JSON.parse(body) } catch { /* form */ } }
  const params = config.params || {}
  return Promise.resolve().then(() => {
    const res = handle(method, url, body, params)
    return { ...res, config }
  })
}
