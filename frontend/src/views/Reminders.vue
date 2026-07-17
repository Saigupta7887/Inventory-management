<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import client from '@/api/client'
import Avatar from '@/components/Avatar.vue'

const router = useRouter()
const reminders = ref([])
const loading = ref(true)
const tab = ref('upcoming')

onMounted(async () => {
  try {
    const { data } = await client.get('/api/reminders')
    reminders.value = data
  } finally {
    loading.value = false
  }
})

// Group into Today / This Week / Later by urgency signal.
const groups = computed(() => {
  const today = [], week = [], later = []
  for (const r of reminders.value) {
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
</script>

<template>
  <div>
    <header class="head">
      <h1>Reminders</h1>
      <span class="filt">⌕</span>
    </header>

    <div class="tabs">
      <button :class="{ active: tab === 'upcoming' }" @click="tab = 'upcoming'">Upcoming</button>
      <button :class="{ active: tab === 'snoozed' }" @click="tab = 'snoozed'">Snoozed</button>
      <button :class="{ active: tab === 'completed' }" @click="tab = 'completed'">Completed</button>
    </div>

    <p v-if="loading" class="spinner">Loading…</p>

    <template v-else-if="tab === 'upcoming'">
      <p v-if="!reminders.length" class="muted empty">Nothing needs your attention. 🎉</p>
      <template v-for="(items, label) in groups" :key="label">
        <template v-if="items.length">
          <h3 class="group">{{ label }}</h3>
          <div
            v-for="(r, i) in items"
            :key="label + i"
            class="card warm rem"
            @click="router.push({ name: 'person', params: { id: r.person_id } })"
          >
            <div class="top">
              <Avatar :name="r.person_name" :size="42" />
              <div class="grow">
                <strong>{{ r.kind === 'birthday' ? r.person_name + "'s Birthday" : 'Check in on ' + r.person_name }}</strong>
                <div class="muted small">{{ r.message }}</div>
              </div>
              <span class="star">⭐</span>
            </div>
            <div class="rowacts">
              <button class="ra">💬</button>
              <button class="ra">📞</button>
              <button class="ra check">✓</button>
            </div>
          </div>
        </template>
      </template>
    </template>

    <p v-else class="muted empty">Nothing here yet.</p>
  </div>
</template>

<style scoped>
.head { display: flex; align-items: center; justify-content: space-between; margin-top: 6px; }
.filt { color: var(--text); font-size: 20px; }
.tabs { display: flex; gap: 8px; margin: 16px 0 18px; }
.tabs button {
  padding: 9px 16px; border-radius: 999px; font-weight: 700; font-size: 14px;
  background: #f1eff7; color: var(--muted);
}
.tabs button.active { background: var(--primary); color: #fff; }
.group { margin: 18px 2px 10px; }
.empty { text-align: center; padding: 40px 0; }
.rem { margin-bottom: 12px; cursor: pointer; }
.top { display: flex; align-items: center; gap: 12px; }
.top .grow { flex: 1; }
.top strong { font-size: 15px; }
.small { font-size: 13px; margin-top: 2px; }
.star { font-size: 16px; }
.rowacts { display: flex; gap: 10px; margin-top: 12px; justify-content: flex-end; }
.ra {
  width: 40px; height: 40px; border-radius: 12px; background: #fff;
  font-size: 16px; box-shadow: var(--shadow);
}
.ra.check { background: var(--primary); color: #fff; }
</style>
