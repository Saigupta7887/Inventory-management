<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import client from '@/api/client'
import { usePeopleStore } from '@/stores/people'
import Avatar from '@/components/Avatar.vue'
import MessageSheet from '@/components/MessageSheet.vue'
import { telLink } from '@/lib/contactActions'

const router = useRouter()
const people = usePeopleStore()

const tab = ref('upcoming')
const upcoming = ref([])
const snoozed = ref([])
const completed = ref([])
const loading = ref(true)

const msgPerson = ref(null)
const msgDraft = ref('')

async function loadUpcoming() {
  upcoming.value = (await client.get('/api/reminders')).data
}
async function loadTab(t) {
  if (t === 'upcoming') await loadUpcoming()
  else if (t === 'snoozed') snoozed.value = (await client.get('/api/reminders/snoozed')).data
  else completed.value = (await client.get('/api/reminders/completed')).data
}

onMounted(async () => {
  try {
    await Promise.all([loadTab('upcoming'), loadTab('snoozed'), loadTab('completed')])
  } finally {
    loading.value = false
  }
})

async function switchTab(t) {
  tab.value = t
  await loadTab(t)
}

async function complete(r) {
  await client.post('/api/reminders/complete', { person_id: r.person_id, kind: r.kind })
  await Promise.all([loadTab('upcoming'), loadTab('completed'), loadTab('snoozed')])
}
async function snooze(r) {
  await client.post('/api/reminders/snooze', { person_id: r.person_id, kind: r.kind, days: 3 })
  await Promise.all([loadTab('upcoming'), loadTab('snoozed')])
}
async function message(r) {
  const [person, card] = await Promise.all([people.get(r.person_id), people.contextCard(r.person_id)])
  msgDraft.value = card.draft_message
  msgPerson.value = person
}
async function call(r) {
  const person = await people.get(r.person_id)
  if (person.phone) window.open(telLink(person.phone), '_blank')
  else message(r)
}

// Group upcoming into Today / This Week / Later.
const groups = computed(() => {
  const today = [], week = [], later = []
  for (const r of upcoming.value) {
    if (r.kind === 'birthday') {
      if ((r.days_until ?? 99) <= 1) today.push(r)
      else if ((r.days_until ?? 99) <= 7) week.push(r)
      else later.push(r)
    } else {
      const d = r.days_since ?? 0
      if (d >= 30) today.push(r)
      else if (d >= 14) week.push(r)
      else later.push(r)
    }
  }
  return { Today: today, 'This Week': week, Later: later }
})

function fmt(dt) {
  return dt ? new Date(dt).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }) : ''
}
function title(r) {
  return r.kind === 'birthday' ? `${r.person_name}'s Birthday` : `Check in on ${r.person_name}`
}
</script>

<template>
  <div>
    <header class="head">
      <h1>Reminders</h1>
      <span class="filt">⌕</span>
    </header>

    <div class="tabs">
      <button :class="{ active: tab === 'upcoming' }" @click="switchTab('upcoming')">Upcoming</button>
      <button :class="{ active: tab === 'snoozed' }" @click="switchTab('snoozed')">
        Snoozed<span v-if="snoozed.length" class="count">{{ snoozed.length }}</span>
      </button>
      <button :class="{ active: tab === 'completed' }" @click="switchTab('completed')">Completed</button>
    </div>

    <p v-if="loading" class="spinner">Loading…</p>

    <!-- Upcoming -->
    <template v-else-if="tab === 'upcoming'">
      <p v-if="!upcoming.length" class="muted empty">Nothing needs your attention. 🎉</p>
      <template v-for="(items, label) in groups" :key="label">
        <template v-if="items.length">
          <h3 class="group">{{ label }}</h3>
          <div v-for="(r, i) in items" :key="label + i" class="card warm rem">
            <div class="top" @click="router.push({ name: 'person', params: { id: r.person_id } })">
              <Avatar :name="r.person_name" :size="42" />
              <div class="grow">
                <strong>{{ title(r) }}</strong>
                <div class="muted small">{{ r.message }}</div>
              </div>
            </div>
            <div class="rowacts">
              <button class="ra" @click="message(r)">💬</button>
              <button class="ra" @click="call(r)">📞</button>
              <button class="ra zzz" @click="snooze(r)" title="Snooze 3 days">💤</button>
              <button class="ra check" @click="complete(r)" title="Mark done">✓</button>
            </div>
          </div>
        </template>
      </template>
    </template>

    <!-- Snoozed -->
    <template v-else-if="tab === 'snoozed'">
      <p v-if="!snoozed.length" class="muted empty">Nothing snoozed.</p>
      <div v-for="(r, i) in snoozed" :key="i" class="card rem">
        <div class="top" @click="router.push({ name: 'person', params: { id: r.person_id } })">
          <Avatar :name="r.person_name" :size="42" />
          <div class="grow">
            <strong>{{ title(r) }}</strong>
            <div class="muted small">Snoozed until {{ fmt(r.snoozed_until) }}</div>
          </div>
          <button class="ra check" @click.stop="complete(r)">✓</button>
        </div>
      </div>
    </template>

    <!-- Completed -->
    <template v-else>
      <p v-if="!completed.length" class="muted empty">Nothing completed yet.</p>
      <div v-for="(r, i) in completed" :key="i" class="card rem done">
        <div class="top">
          <Avatar :name="r.person_name" :size="42" />
          <div class="grow">
            <strong>{{ r.person_name }}</strong>
            <div class="muted small">{{ r.message }} · {{ fmt(r.completed_at) }}</div>
          </div>
          <span class="tick">✓</span>
        </div>
      </div>
    </template>

    <MessageSheet
      v-if="msgPerson"
      :person="msgPerson"
      :draft="msgDraft"
      @close="msgPerson = null"
      @logged="switchTab('upcoming')"
    />
  </div>
</template>

<style scoped>
.head { display: flex; align-items: center; justify-content: space-between; margin-top: 6px; }
.filt { color: var(--text); font-size: 20px; }
.tabs { display: flex; gap: 8px; margin: 16px 0 18px; }
.tabs button {
  padding: 9px 16px; border-radius: 999px; font-weight: 700; font-size: 14px;
  background: #f1eff7; color: var(--muted); display: flex; align-items: center; gap: 6px;
}
.tabs button.active { background: var(--primary); color: #fff; }
.count { background: rgba(255,255,255,0.3); border-radius: 999px; padding: 0 6px; font-size: 12px; }
.tabs button:not(.active) .count { background: var(--primary-100); color: var(--primary); }
.group { margin: 18px 2px 10px; }
.empty { text-align: center; padding: 40px 0; }
.rem { margin-bottom: 12px; }
.top { display: flex; align-items: center; gap: 12px; cursor: pointer; }
.top .grow { flex: 1; }
.top strong { font-size: 15px; }
.small { font-size: 13px; margin-top: 2px; }
.rowacts { display: flex; gap: 10px; margin-top: 12px; justify-content: flex-end; }
.ra {
  width: 40px; height: 40px; border-radius: 12px; background: #fff;
  font-size: 16px; box-shadow: var(--shadow);
}
.ra.check { background: var(--primary); color: #fff; }
.ra.zzz { background: var(--medium-bg); }
.done { opacity: 0.85; }
.tick { color: var(--low-fg); font-size: 20px; font-weight: 800; }
</style>
