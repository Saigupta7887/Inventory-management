<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import client from '@/api/client'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const data = ref(null)
const loading = ref(true)

onMounted(async () => {
  if (!auth.user) await auth.fetchMe().catch(() => {})
  try {
    const res = await client.get('/api/dashboard')
    data.value = res.data
  } finally {
    loading.value = false
  }
})

function fmtDays(d) {
  if (d === 0) return 'today'
  if (d === 1) return 'tomorrow'
  return `in ${d} days`
}
</script>

<template>
  <div>
    <h1>Good to see you{{ auth.user?.full_name ? `, ${auth.user.full_name.split(' ')[0]}` : '' }} 👋</h1>
    <p class="muted">Here's what's happening with your relationships.</p>

    <p v-if="loading" class="muted">Loading…</p>

    <div v-else class="grid cols">
      <section class="card">
        <h2>🔔 Needs attention</h2>
        <p v-if="!data.needs_attention.length" class="muted">You're all caught up. 🎉</p>
        <ul class="list">
          <li v-for="n in data.needs_attention" :key="n.person_id">
            <RouterLink :to="{ name: 'person', params: { id: n.person_id } }">
              <strong>{{ n.name }}</strong>
            </RouterLink>
            <span class="pill" :class="n.priority">{{ n.priority.replace('_', ' ') }}</span>
            <div class="muted small">{{ n.message }}</div>
          </li>
        </ul>
      </section>

      <section class="card">
        <h2>🎂 Upcoming events</h2>
        <p v-if="!data.upcoming_events.length" class="muted">Nothing on the horizon.</p>
        <ul class="list">
          <li v-for="e in data.upcoming_events" :key="e.person_id">
            <RouterLink :to="{ name: 'person', params: { id: e.person_id } }">
              <strong>{{ e.name }}</strong>
            </RouterLink>
            <div class="muted small">Birthday {{ fmtDays(e.days_until) }}</div>
          </li>
        </ul>
      </section>

      <section class="card">
        <h2>🕑 Recent activity</h2>
        <p v-if="!data.recent_activity.length" class="muted">No interactions logged yet.</p>
        <ul class="list">
          <li v-for="a in data.recent_activity" :key="a.id">
            <span class="chip">{{ a.channel }}</span>
            <span>{{ a.summary || 'Interaction logged' }}</span>
            <div v-if="a.mood" class="muted small">Mood: {{ a.mood }}</div>
          </li>
        </ul>
      </section>

      <section class="card stat">
        <div class="big">{{ data.total_people }}</div>
        <div class="muted">people in your circle</div>
        <RouterLink :to="{ name: 'people' }" class="btn secondary" style="margin-top: 14px">
          Manage people
        </RouterLink>
      </section>
    </div>
  </div>
</template>

<style scoped>
.cols {
  grid-template-columns: 1fr 1fr;
  margin-top: 20px;
}
@media (max-width: 720px) {
  .cols {
    grid-template-columns: 1fr;
  }
}
.list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 14px;
}
.list li {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}
.small {
  font-size: 13px;
  flex-basis: 100%;
}
.chip {
  background: var(--primary-soft);
  color: var(--primary-dark);
  border-radius: 6px;
  padding: 2px 8px;
  font-size: 12px;
  font-weight: 600;
  text-transform: capitalize;
}
.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}
.big {
  font-size: 48px;
  font-weight: 800;
  color: var(--primary);
}
</style>
