<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import client from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import { usePeopleStore } from '@/stores/people'
import Avatar from '@/components/Avatar.vue'
import MessageSheet from '@/components/MessageSheet.vue'
import { telLink } from '@/lib/contactActions'

const auth = useAuthStore()
const people = usePeopleStore()
const router = useRouter()

const data = ref(null)
const reconnect = ref(null) // { person, card }
const loading = ref(true)

const greeting = computed(() => {
  const h = new Date().getHours()
  if (h < 12) return 'Good morning'
  if (h < 18) return 'Good afternoon'
  return 'Good evening'
})
const firstName = computed(() => auth.user?.full_name?.split(' ')[0] || 'there')

onMounted(async () => {
  if (!auth.user) await auth.fetchMe().catch(() => {})
  try {
    const { data: dash } = await client.get('/api/dashboard')
    data.value = dash
    const top = dash.needs_attention[0]
    if (top) {
      const [person, card] = await Promise.all([
        people.get(top.person_id),
        people.contextCard(top.person_id),
      ])
      reconnect.value = { person, card, message: top.message }
    }
  } finally {
    loading.value = false
  }
})

const rest = computed(() =>
  (data.value?.needs_attention || []).slice(reconnect.value ? 1 : 0),
)

const showMessage = ref(false)
function callReconnect() {
  const p = reconnect.value?.person
  if (p?.phone) window.open(telLink(p.phone), '_blank')
  else showMessage.value = true
}

function fmtDays(d) {
  if (d === 0) return 'today'
  if (d === 1) return 'in 1 day'
  return `in ${d} days`
}
</script>

<template>
  <div>
    <header class="topbar">
      <div>
        <h1>{{ greeting }},<br />{{ firstName }} 👋</h1>
        <p class="muted sub">Here's what's important today.</p>
      </div>
      <RouterLink :to="{ name: 'reminders' }" class="bell">
        🔔<span v-if="data?.summary?.needs_attention_count" class="badge"></span>
      </RouterLink>
    </header>

    <p v-if="loading" class="spinner">Loading…</p>

    <template v-else>
      <!-- Reconnect Today -->
      <div class="section-head">
        <h2>Reconnect Today</h2>
        <RouterLink :to="{ name: 'reminders' }" class="see-all">See all ›</RouterLink>
      </div>

      <div v-if="reconnect" class="card warm reconnect">
        <div class="head">
          <Avatar :name="reconnect.person.name" :size="48" />
          <div>
            <strong>{{ reconnect.person.name }}</strong>
            <div class="muted small">{{ reconnect.message }}</div>
          </div>
        </div>
        <p class="suggest">✨ {{ reconnect.card.suggested_question }}</p>
        <div class="actions">
          <button class="act" @click="showMessage = true"><span>💬</span>Message</button>
          <button class="act" @click="callReconnect"><span>📞</span>Call</button>
          <RouterLink :to="{ name: 'add-note', params: { id: reconnect.person.id } }" class="act">
            <span>📝</span>Add Note
          </RouterLink>
        </div>
      </div>

      <MessageSheet
        v-if="showMessage && reconnect"
        :person="reconnect.person"
        :draft="reconnect.card.draft_message"
        @close="showMessage = false"
      />
      <p v-else class="muted empty">You're all caught up. 🎉</p>

      <!-- Nearby prompt -->
      <RouterLink :to="{ name: 'nearby' }" class="nearby-card">
        <span class="pin">📍</span>
        <div>
          <strong>Out & about?</strong>
          <div class="muted small">See errands &amp; people near you</div>
        </div>
        <span class="chev">›</span>
      </RouterLink>

      <!-- Needs Attention -->
      <div v-if="rest.length" class="section-head">
        <h2>Needs Attention</h2>
        <RouterLink :to="{ name: 'people' }" class="see-all">See all ›</RouterLink>
      </div>
      <RouterLink
        v-for="n in rest"
        :key="n.person_id"
        :to="{ name: 'person', params: { id: n.person_id } }"
        class="row"
      >
        <Avatar :name="n.name" :size="44" />
        <div class="grow">
          <strong>{{ n.name }}</strong>
          <div class="muted small">{{ n.message }}</div>
        </div>
        <span class="pill" :class="n.priority">{{ n.priority.replace('_', ' ') }}</span>
      </RouterLink>

      <!-- Upcoming Birthdays -->
      <div v-if="data.upcoming_events.length" class="section-head">
        <h2>Upcoming Birthdays</h2>
      </div>
      <RouterLink
        v-for="e in data.upcoming_events"
        :key="'b' + e.person_id"
        :to="{ name: 'person', params: { id: e.person_id } }"
        class="row"
      >
        <Avatar :name="e.name" :size="44" />
        <div class="grow">
          <strong>{{ e.name }}</strong>
          <div class="muted small">Birthday {{ fmtDays(e.days_until) }}</div>
        </div>
        <span class="cake">🎂</span>
      </RouterLink>
    </template>
  </div>
</template>

<style scoped>
.topbar { display: flex; justify-content: space-between; align-items: flex-start; margin-top: 8px; }
.sub { margin-top: 6px; font-size: 14px; }
.bell { position: relative; font-size: 22px; }
.badge {
  position: absolute; top: -2px; right: -2px;
  width: 9px; height: 9px; border-radius: 50%;
  background: var(--high-fg); border: 2px solid #fff;
}
.small { font-size: 13px; }
.empty { padding: 8px 4px 4px; }

.reconnect .head { display: flex; gap: 12px; align-items: center; }
.reconnect .head strong { font-size: 16px; }
.suggest {
  background: rgba(255,255,255,0.65);
  border-radius: 12px;
  padding: 10px 12px;
  font-weight: 600;
  font-size: 14px;
  margin: 12px 0;
}
.reconnect .actions { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
.act {
  display: flex; flex-direction: column; align-items: center; gap: 4px;
  background: #fff; border-radius: 12px; padding: 10px 4px;
  font-size: 12px; font-weight: 600; color: var(--primary);
}
.act span { font-size: 18px; }

.nearby-card {
  display: flex; align-items: center; gap: 12px;
  background: var(--grad-soft);
  border: 1px solid var(--primary-100);
  border-radius: var(--radius);
  padding: 14px 16px;
  margin-top: 14px;
}
.nearby-card .pin { font-size: 22px; }
.nearby-card strong { font-size: 15px; }
.nearby-card .chev { margin-left: auto; color: var(--muted); font-size: 22px; }

.row {
  display: flex; align-items: center; gap: 12px;
  padding: 12px 4px;
  border-bottom: 1px solid var(--border);
}
.row .grow { flex: 1; }
.row strong { font-size: 15px; }
.cake { font-size: 22px; }
</style>
