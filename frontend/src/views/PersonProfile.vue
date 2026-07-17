<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import client from '@/api/client'
import { usePeopleStore } from '@/stores/people'
import Avatar from '@/components/Avatar.vue'

const props = defineProps({ id: { type: [String, Number], required: true } })
const store = usePeopleStore()
const router = useRouter()

const person = ref(null)
const notes = ref([])
const interactions = ref([])
const card = ref(null)
const myReminders = ref([])
const loading = ref(true)
const tab = ref('overview')

const tabs = ['overview', 'notes', 'interactions', 'reminders']

onMounted(async () => {
  try {
    person.value = await store.get(props.id)
    const [n, i, c, rem] = await Promise.all([
      store.notes(props.id),
      store.interactions(props.id),
      store.contextCard(props.id),
      client.get('/api/reminders').then((r) => r.data),
    ])
    notes.value = n
    interactions.value = i
    card.value = c
    myReminders.value = rem.filter((x) => x.person_id === Number(props.id))
  } finally {
    loading.value = false
  }
})

const lastInteraction = computed(() => interactions.value[0] || null)
const pinned = computed(() => notes.value.filter((n) => n.pinned))
const facts = computed(() => {
  const f = []
  if (person.value?.relationship_type) f.push({ icon: '🤝', t: person.value.relationship_type })
  pinned.value.forEach((n) => f.push({ icon: '📌', t: n.content }))
  notes.value.filter((n) => !n.pinned).slice(0, 4).forEach((n) => f.push({ icon: '•', t: n.content }))
  if (person.value?.birthday) f.push({ icon: '🎂', t: 'Birthday on ' + fmt(person.value.birthday) })
  if (person.value?.location_label) f.push({ icon: '📍', t: person.value.location_label })
  return f
})

function fmt(dt) {
  if (!dt) return '—'
  return new Date(dt).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
}

async function remove() {
  if (!confirm('Remove this person?')) return
  await store.remove(props.id)
  router.push({ name: 'people' })
}
</script>

<template>
  <div v-if="loading" class="spinner">Loading…</div>
  <div v-else-if="person">
    <header class="bar">
      <button class="icon-btn" @click="router.back()">←</button>
      <button class="icon-btn" @click="remove">⋯</button>
    </header>

    <div class="hero">
      <div class="av-wrap">
        <Avatar :name="person.name" :size="96" />
        <span class="heart">💜</span>
      </div>
      <h1>{{ person.name }}</h1>
      <p class="sub">
        {{ person.relationship_type || 'Contact' }} ·
        <span :class="['prio', person.priority]">{{ person.priority.replace('_', ' ') }} Priority</span>
      </p>
    </div>

    <div class="quick">
      <RouterLink :to="{ name: 'log-interaction', params: { id: person.id } }" class="q"><span>💬</span>Message</RouterLink>
      <RouterLink :to="{ name: 'log-interaction', params: { id: person.id } }" class="q"><span>📞</span>Call</RouterLink>
      <RouterLink :to="{ name: 'add-note', params: { id: person.id } }" class="q"><span>📝</span>Add Note</RouterLink>
      <RouterLink :to="{ name: 'log-interaction', params: { id: person.id } }" class="q"><span>⋯</span>More</RouterLink>
    </div>

    <div class="tabs">
      <button v-for="t in tabs" :key="t" :class="{ active: tab === t }" @click="tab = t">
        {{ t.charAt(0).toUpperCase() + t.slice(1) }}
      </button>
    </div>

    <!-- Overview -->
    <template v-if="tab === 'overview'">
      <div class="card">
        <h3>About {{ person.name.split(' ')[0] }}</h3>
        <ul class="facts">
          <li v-for="(f, i) in facts" :key="i"><span class="fi">{{ f.icon }}</span>{{ f.t }}</li>
        </ul>
        <p v-if="!facts.length" class="muted">No details yet — add a note.</p>
      </div>

      <div class="card" v-if="lastInteraction">
        <div class="li-head">
          <h3>Last Interaction</h3>
          <span class="muted small">{{ fmt(lastInteraction.occurred_at) }}</span>
        </div>
        <p>{{ lastInteraction.summary || 'Interaction logged.' }}</p>
      </div>

      <div class="card suggest">
        <h3>💡 Suggested Next Step</h3>
        <p>{{ card.suggested_question }}</p>
      </div>
    </template>

    <!-- Notes -->
    <template v-else-if="tab === 'notes'">
      <RouterLink :to="{ name: 'add-note', params: { id: person.id } }" class="btn soft mb">+ Add note</RouterLink>
      <div v-for="n in notes" :key="n.id" class="card note">
        <p><span v-if="n.pinned">📌 </span>{{ n.content }}</p>
        <span v-if="n.category" class="pill">{{ n.category.replace('_', ' ') }}</span>
      </div>
      <p v-if="!notes.length" class="muted empty">No notes yet.</p>
    </template>

    <!-- Interactions -->
    <template v-else-if="tab === 'interactions'">
      <RouterLink :to="{ name: 'log-interaction', params: { id: person.id } }" class="btn soft mb">+ Log interaction</RouterLink>
      <div v-for="i in interactions" :key="i.id" class="card">
        <div class="li-head">
          <span class="chan">{{ i.channel }}</span>
          <span class="muted small">{{ fmt(i.occurred_at) }}</span>
        </div>
        <p v-if="i.summary">{{ i.summary }}</p>
        <p v-if="i.follow_up" class="muted small">↪ {{ i.follow_up }}</p>
      </div>
      <p v-if="!interactions.length" class="muted empty">Nothing logged yet.</p>
    </template>

    <!-- Reminders -->
    <template v-else>
      <div v-for="(r, i) in myReminders" :key="i" class="card warm">
        <strong>{{ r.kind === 'birthday' ? '🎂' : '🔔' }} {{ r.message }}</strong>
      </div>
      <p v-if="!myReminders.length" class="muted empty">No active reminders — you're in good shape.</p>
    </template>
  </div>
</template>

<style scoped>
.bar { display: flex; justify-content: space-between; padding: 6px 0; }
.icon-btn { width: 38px; height: 38px; border-radius: 12px; background: var(--bg); font-size: 20px; color: var(--text); }
.hero { text-align: center; margin: 6px 0 18px; }
.av-wrap { position: relative; display: inline-block; }
.av-wrap .heart {
  position: absolute; bottom: 2px; right: 2px;
  background: #fff; border-radius: 50%; padding: 3px; font-size: 14px;
  box-shadow: var(--shadow);
}
.hero h1 { margin-top: 12px; }
.sub { margin-top: 6px; color: var(--muted); font-weight: 600; }
.prio { color: var(--high-fg); text-transform: capitalize; }
.prio.low { color: var(--low-fg); }
.prio.medium { color: var(--medium-fg); }

.quick { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 18px; }
.q {
  display: flex; flex-direction: column; align-items: center; gap: 5px;
  background: #fff; border: 1px solid var(--border); border-radius: 14px;
  padding: 12px 4px; font-size: 12px; font-weight: 600; color: var(--primary);
}
.q span { font-size: 18px; }

.tabs { display: flex; gap: 6px; border-bottom: 1.5px solid var(--border); margin-bottom: 16px; }
.tabs button {
  flex: 1; padding: 12px 4px; font-size: 14px; font-weight: 700; color: var(--muted);
  border-bottom: 2.5px solid transparent; margin-bottom: -1.5px;
}
.tabs button.active { color: var(--primary); border-color: var(--primary); }

.card { margin-bottom: 14px; }
.facts { list-style: none; padding: 0; margin: 10px 0 0; display: grid; gap: 10px; }
.facts li { display: flex; gap: 10px; font-size: 14px; }
.fi { width: 18px; }
.li-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.small { font-size: 12px; }
.suggest { background: var(--grad-soft); border-color: var(--primary-100); }
.note { display: flex; justify-content: space-between; align-items: flex-start; gap: 10px; }
.chan { font-weight: 700; text-transform: capitalize; color: var(--primary); }
.mb { margin-bottom: 14px; }
.empty { text-align: center; padding: 24px 0; }
</style>
