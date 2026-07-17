<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import client from '@/api/client'

const reminders = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const { data } = await client.get('/api/reminders')
    reminders.value = data
  } finally {
    loading.value = false
  }
})

const icon = (kind) => (kind === 'birthday' ? '🎂' : '🔔')
</script>

<template>
  <div>
    <h1>Reminders</h1>
    <p class="muted">Who to reach out to, and what's coming up.</p>

    <p v-if="loading" class="muted">Loading…</p>
    <p v-else-if="!reminders.length" class="muted">Nothing needs your attention right now. 🎉</p>

    <div class="grid list">
      <RouterLink
        v-for="(r, i) in reminders"
        :key="i"
        :to="{ name: 'person', params: { id: r.person_id } }"
        class="card item"
      >
        <div class="ic">{{ icon(r.kind) }}</div>
        <div class="body">
          <strong>{{ r.person_name }}</strong>
          <div class="muted">{{ r.message }}</div>
        </div>
        <span class="pill" :class="r.priority">{{ r.priority.replace('_', ' ') }}</span>
      </RouterLink>
    </div>
  </div>
</template>

<style scoped>
.list { margin-top: 18px; }
.item { display: flex; align-items: center; gap: 14px; }
.ic { font-size: 24px; }
.body { flex: 1; }
</style>
