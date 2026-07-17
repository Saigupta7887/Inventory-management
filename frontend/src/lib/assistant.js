// "Hey Bondly" command engine. Takes a spoken/typed transcript, figures out
// the intent, performs it against the real stores/API, and returns a short
// spoken reply. Deliberately dependency-free heuristics (same spirit as the
// backend's ai.py) so it works offline and in the demo.

import client from '@/api/client'
import router from '@/router'
import { usePeopleStore } from '@/stores/people'
import { useLocationStore } from '@/stores/location'

const CHANNELS = {
  call: ['call', 'called', 'phone', 'rang'],
  text: ['text', 'texted', 'message', 'messaged', 'whatsapp'],
  meeting: ['met', 'meeting', 'saw', 'lunch', 'coffee with', 'hung out'],
  email: ['email', 'emailed', 'mailed'],
}
const PLACE_WORDS = {
  grocery: ['grocery', 'supermarket', 'groceries', 'store', 'market'],
  pharmacy: ['pharmacy', 'chemist', 'drugstore', 'medicine'],
  cafe: ['cafe', 'coffee shop', 'coffee'],
  restaurant: ['restaurant', 'dinner', 'lunch'],
  gym: ['gym', 'workout'],
  bookstore: ['bookstore', 'book shop', 'book store', 'books'],
}
const SCREENS = {
  home: 'home', dashboard: 'home', people: 'people', contacts: 'people',
  reminders: 'reminders', insights: 'insights', stats: 'insights',
  nearby: 'nearby', settings: 'settings',
}

const clean = (s) => s.toLowerCase().trim().replace(/[.?!]+$/, '')
const cap = (s) => s.charAt(0).toUpperCase() + s.slice(1)
const titleCase = (s) => s.replace(/\b\w/g, (c) => c.toUpperCase())

function stripWakeWord(t) {
  return t.replace(/^\s*(hey|hi|ok|okay)?\s*bondly[,\s]*/i, '').trim()
}

async function people() {
  const store = usePeopleStore()
  if (!store.people.length) await store.fetchAll()
  return store
}

function matchPerson(text, list) {
  const t = ' ' + text.toLowerCase() + ' '
  let best = null
  for (const p of list) {
    for (const cand of [p.name, p.nickname, p.name.split(' ')[0]].filter(Boolean)) {
      const c = cand.toLowerCase()
      if (t.includes(' ' + c + ' ') || t.includes(" " + c + "'s ")) {
        if (!best || c.length > best.key.length) best = { person: p, key: c }
      }
    }
  }
  return best?.person || null
}

function detect(map, text) {
  for (const [key, words] of Object.entries(map)) {
    if (words.some((w) => text.includes(w))) return key
  }
  return null
}

/**
 * Run a command. Returns { ok, say } — `say` is spoken + shown.
 */
export async function runCommand(raw) {
  const transcript = stripWakeWord(clean(raw || ''))
  if (!transcript) return { ok: false, say: "I didn't catch that. Try again?" }

  const store = await people()
  const list = store.people
  const person = matchPerson(transcript, list)

  // ---- Navigation ----
  const navMatch = transcript.match(/\b(?:open|go to|show|take me to)\s+(?:the\s+|my\s+)?(\w+)/)
  if (navMatch && SCREENS[navMatch[1]] && !person) {
    const name = SCREENS[navMatch[1]]
    router.push({ name })
    return { ok: true, say: `Opening ${navMatch[1]}.` }
  }

  // ---- Open a person's profile ----
  if (/\b(open|show|profile|pull up|go to)\b/.test(transcript) && person && !/\bnote\b/.test(transcript)) {
    router.push({ name: 'person', params: { id: person.id } })
    return { ok: true, say: `Here's ${person.name}.` }
  }

  // ---- Who needs attention / reconnect ----
  if (/\b(reconnect|needs? attention|out of touch|haven'?t (talked|spoken)|should i (reach|contact|call))\b/.test(transcript)) {
    const { data } = await client.get('/api/reminders')
    const names = data.filter((r) => r.kind !== 'birthday').slice(0, 3).map((r) => r.person_name)
    router.push({ name: 'reminders' })
    if (!names.length) return { ok: true, say: "You're all caught up — nobody's overdue." }
    return { ok: true, say: `You might reconnect with ${names.join(', ')}.` }
  }

  // ---- Birthdays ----
  if (/\bbirthday/.test(transcript)) {
    const { data } = await client.get('/api/dashboard')
    const ev = data.upcoming_events || []
    router.push({ name: 'reminders' })
    if (!ev.length) return { ok: true, say: 'No birthdays coming up soon.' }
    const e = ev[0]
    return { ok: true, say: `${e.name}'s birthday is in ${e.days_until} days.` }
  }

  // ---- Add errand ----
  if (/\b(errand|pick up|buy|grab|remind me to)\b/.test(transcript)) {
    const loc = useLocationStore()
    const placeType = detect(PLACE_WORDS, transcript) || 'grocery'
    let title = transcript
      .replace(/^.*?\b(pick up|buy|grab|remind me to)\b/, '')
      .replace(/\b(for|at|from|in)\b.*$/, '')
      .trim()
    if (person) title = title.replace(new RegExp(person.name.split(' ')[0], 'i'), '').trim()
    title = cap(title || 'Errand')
    await loc.createErrand({
      title,
      place_type: placeType,
      person_id: person ? person.id : null,
    })
    const who = person ? ` for ${person.name.split(' ')[0]}` : ''
    return { ok: true, say: `Added "${title}"${who} for when you're at a ${placeType}.` }
  }

  // ---- Add person ----
  const addPersonMatch = transcript.match(/\b(?:add|new)\s+(?:person|contact)?\s*([a-z]+(?:\s[a-z]+)?)(?:\s+as\s+(?:a\s+)?(\w+))?/)
  if (/\b(add|new)\b/.test(transcript) && /\b(person|contact|friend|as a)\b/.test(transcript) && addPersonMatch) {
    const name = titleCase(addPersonMatch[1].trim())
    const rel = addPersonMatch[2] || 'friend'
    const created = await store.create({ name, relationship_type: rel, priority: 'medium' })
    return { ok: true, say: `Added ${name} as a ${rel}.` }
  }

  // ---- Log interaction ----
  const channel = detect(CHANNELS, transcript)
  if (channel && person) {
    let summary = transcript
      .replace(new RegExp(`.*\\b(${CHANNELS[channel].join('|')})\\b`), '')
      .replace(new RegExp(`\\b(with|to)\\b\\s+${person.name.split(' ')[0]}`, 'i'), '')
      .replace(new RegExp(person.name.split(' ')[0], 'i'), '')
      .replace(/^\s*(about|that|and)\b/, '')
      .trim()
    await store.logInteraction(person.id, {
      channel,
      summary: summary ? cap(summary) : null,
      mood: 'positive',
    })
    return { ok: true, say: `Logged a ${channel} with ${person.name.split(' ')[0]}.` }
  }

  // ---- Add note ----
  if (/\b(note|remember|remind me that|jot)\b/.test(transcript)) {
    if (!person) {
      return { ok: false, say: 'Who is that note about? Try "note that Sarah loves matcha".' }
    }
    let content = transcript
      .replace(/^.*?\b(note that|note|remember that|remember|jot down|jot)\b/, '')
      .replace(new RegExp(`\\b(about|for)\\b\\s+${person.name.split(' ')[0]}`, 'i'), '')
      .trim()
    // Keep the person's name in the content if it reads naturally.
    content = cap(content || transcript)
    const note = await store.addNote(person.id, { content })
    const label = note.category ? ` (${note.category.replace('_', ' ')})` : ''
    return { ok: true, say: `Noted for ${person.name.split(' ')[0]}${label}.` }
  }

  // ---- Search fallback ----
  const searchMatch = transcript.match(/\b(?:who|search|find|which)\b\s+(.*)/)
  if (searchMatch) {
    const { data } = await client.get('/api/search', { params: { q: transcript } })
    const n = data.results.length
    router.push({ name: 'people' })
    if (!n) return { ok: true, say: `I couldn't find anyone matching that.` }
    const names = data.results.slice(0, 3).map((r) => r.name).join(', ')
    return { ok: true, say: `Found ${n}: ${names}.` }
  }

  return {
    ok: false,
    say: 'Try things like "note that Sarah loves matcha", "log a call with Nikhil", "who should I reconnect with", or "remind me to buy flowers for Priya".',
  }
}
