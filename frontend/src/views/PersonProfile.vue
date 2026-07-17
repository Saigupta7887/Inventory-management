<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { usePeopleStore } from '@/stores/people'

const props = defineProps({ id: { type: [String, Number], required: true } })
const store = usePeopleStore()
const router = useRouter()

const person = ref(null)
const notes = ref([])
const interactions = ref([])
const card = ref(null)
const loading = ref(true)

const noteText = ref('')
const notehis = ref(false)

const interaction = ref({ channel: 'call', summary: '', mood: 'positive', follow_up: '' })

async function loadAll() {
  const id = props.id
  person.value = await store.get(id)
  ;[notes.value, interactions.value, card.value] = await Promise.all([
    store.notes(id),
    store.interactions(id),
    store.contextCard(id),
  ])
}

onMounted(async () => {
  try {
    await loadAll()
  } finally {
    loading.value = false
  }
})

async function addNote() {
  if (!noteText.value.trim()) return
  await store.addNote(props.id, { content: noteText.value, pinned: notehis.value })
  noteText.value = ''
  notehis.value = false
  notes.value = await store.notes(props.id)
}

async function logInteraction() {
  await store.logInteraction(props.id, interaction.value)
  interaction.value = { channel: 'call', summary: '', mood: 'positive', follow_up: '' }
  ;[interactions.value, card.value, person.value] = await Promise.all([
    store.interactions(props.id),
    store.contextCard(props.id),
    store.get(props.id),
  ])
}

async function remove() {
  if (!confirm('Remove this person and all their notes?')) return
  await store.remove(props.id)
  router.push({ name: 'people' })
}

function fmt(dt) {
  if (!dt) return '—'
  return new Date(dt).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}
</script>

<template>
  <div v-if="loading" class="muted">Loading…</div>
  <div v-else-if="person">
    <RouterLink :to="{ name: 'people' }" class="muted back">← All people</RouterLink>

    <div class="header card">
      <div class="avatar">{{ person.name.charAt(0).toUpperCase() }}</div>
      <div class="who">
        <h1>{{ person.name }}<span v-if="person.nickname" class="muted"> · {{ person.nickname }}</span></h1>
        <div class="muted">
          {{ person.relationship_type || 'contact' }} ·
          <span class="pill" :class="person.priority">{{ person.priority.replace('_', ' ') }}</span>
        </div>
        <div class="muted small">
          Last contact: {{ fmt(person.last_interaction_at) }} · reminds every
          {{ person.reminder_interval_days }} days
        </div>
      </div>
      <button class="btn danger" @click="remove">Remove</button>
    </div>

    <div class="cols grid">
      <div class="stack">
        <!-- AI context card (Phase 6) -->
        <section class="card ai">
          <h2>✨ Context card</h2>
          <p class="suggest">{{ card.suggested_question }}</p>
          <div class="draft">
            <span class="label">Suggested message</span>
            <p>“{{ card.draft_message }}”</p>
          </div>
          <div v-if="card.pinned_notes?.length" class="pinned">
            <span class="label">Pinned</span>
            <ul>
              <li v-for="(n, i) in card.pinned_notes" :key="i">📌 {{ n }}</li>
            </ul>
          </div>
        </section>

        <!-- Notes (Phase 3) -->
        <section class="card">
          <h2>🧠 Notes</h2>
          <form class="noteform" @submit.prevent="addNote">
            <textarea
              v-model="noteText"
              class="textarea"
              rows="2"
              placeholder="Loves sushi · started a new job · allergic to peanuts…"
            ></textarea>
            <label class="pin"><input type="checkbox" v-model="notehis" /> Pin</label>
            <button class="btn" type="submit">Add</button>
          </form>
          <ul class="notes">
            <li v-for="n in notes" :key="n.id">
              <span v-if="n.pinned">📌 </span>{{ n.content }}
              <span v-if="n.category" class="tag">{{ n.category.replace('_', ' ') }}</span>
            </li>
          </ul>
          <p v-if="!notes.length" class="muted">No notes yet.</p>
        </section>
      </div>

      <div class="stack">
        <!-- Log interaction (Phase 4) -->
        <section class="card">
          <h2>💬 Log interaction</h2>
          <form @submit.prevent="logInteraction">
            <div class="row">
              <select v-model="interaction.channel" class="select">
                <option>call</option><option>text</option><option>meeting</option>
                <option>email</option><option>other</option>
              </select>
              <select v-model="interaction.mood" class="select">
                <option value="positive">😊 Positive</option>
                <option value="neutral">😐 Neutral</option>
                <option value="negative">🙁 Negative</option>
              </select>
            </div>
            <input v-model="interaction.summary" class="input" placeholder="What did you talk about?" />
            <input v-model="interaction.follow_up" class="input" placeholder="Follow-up (optional)" />
            <button class="btn" type="submit">Save interaction</button>
          </form>
        </section>

        <!-- History -->
        <section class="card">
          <h2>🕑 History</h2>
          <ul class="history">
            <li v-for="i in interactions" :key="i.id">
              <div class="hrow">
                <span class="chip">{{ i.channel }}</span>
                <span class="muted small">{{ fmt(i.occurred_at) }}</span>
              </div>
              <div v-if="i.summary">{{ i.summary }}</div>
              <div v-if="i.follow_up" class="muted small">↪ {{ i.follow_up }}</div>
            </li>
          </ul>
          <p v-if="!interactions.length" class="muted">Nothing logged yet.</p>
        </section>
      </div>
    </div>
  </div>
</template>

<style scoped>
.back { display: inline-block; margin-bottom: 12px; }
.header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 18px;
}
.avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: var(--primary-soft);
  color: var(--primary-dark);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  font-weight: 800;
}
.who { flex: 1; }
.who h1 { font-size: 24px; }
.small { font-size: 13px; }
.cols { grid-template-columns: 1fr 1fr; }
@media (max-width: 760px) { .cols { grid-template-columns: 1fr; } }
.stack { display: grid; gap: 16px; align-content: start; }
.ai { background: linear-gradient(160deg, #fbfaff, #f2eefe); border-color: #e6ddfb; }
.suggest { font-weight: 600; margin: 4px 0 14px; }
.draft p { margin: 4px 0 0; font-style: italic; color: var(--muted); }
.pinned ul { margin: 6px 0 0; padding-left: 2px; list-style: none; }
.pinned li { margin: 3px 0; }
.noteform { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
.noteform .textarea { flex: 1 1 100%; }
.pin { font-size: 13px; display: flex; gap: 4px; align-items: center; color: var(--muted); }
.notes { list-style: none; padding: 0; margin: 14px 0 0; display: grid; gap: 8px; }
.notes li {
  background: var(--bg);
  padding: 8px 12px;
  border-radius: 10px;
}
.tag {
  margin-left: 6px;
  font-size: 11px;
  background: var(--primary-soft);
  color: var(--primary-dark);
  padding: 1px 7px;
  border-radius: 999px;
  text-transform: capitalize;
}
.row { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 8px; }
form .input { margin-bottom: 8px; }
.history { list-style: none; padding: 0; margin: 0; display: grid; gap: 12px; }
.hrow { display: flex; gap: 8px; align-items: center; margin-bottom: 2px; }
.chip {
  background: var(--primary-soft);
  color: var(--primary-dark);
  border-radius: 6px;
  padding: 2px 8px;
  font-size: 12px;
  font-weight: 600;
  text-transform: capitalize;
}
</style>
