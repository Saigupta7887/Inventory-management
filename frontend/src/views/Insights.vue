<script setup>
import { onMounted, ref, computed } from 'vue'
import client from '@/api/client'

const data = ref(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await client.get('/api/insights')
    data.value = res.data
  } finally {
    loading.value = false
  }
})

const scoreColor = computed(() => {
  const s = data.value?.health_score ?? 0
  if (s >= 75) return 'var(--success)'
  if (s >= 45) return 'var(--warning)'
  return 'var(--danger)'
})
</script>

<template>
  <div>
    <h1>Insights</h1>
    <p class="muted">A pulse on your relationships.</p>

    <p v-if="loading" class="muted">Loading…</p>

    <div v-else class="grid cols">
      <section class="card score">
        <div class="ring" :style="{ '--c': scoreColor }">
          <span>{{ data.health_score }}</span>
        </div>
        <h3>Relationship health</h3>
        <p class="muted small">Based on how many people are overdue for a catch-up.</p>
      </section>

      <section class="card">
        <h2>👥 By relationship type</h2>
        <ul class="bars">
          <li v-for="(count, type) in data.people_by_type" :key="type">
            <span class="k">{{ type }}</span>
            <span class="bar"><i :style="{ width: Math.min(count * 24, 100) + '%' }"></i></span>
            <span class="v">{{ count }}</span>
          </li>
        </ul>
      </section>

      <section class="card">
        <h2>🔥 Most active</h2>
        <p v-if="!data.most_active.length" class="muted">No interactions logged yet.</p>
        <ul class="rows">
          <li v-for="m in data.most_active" :key="m.name">
            <span>{{ m.name }}</span><span class="muted">{{ m.count }} interactions</span>
          </li>
        </ul>
      </section>

      <section class="card">
        <h2>🌱 Needs reconnecting</h2>
        <p v-if="!data.neglected.length" class="muted">Everyone's up to date. 🎉</p>
        <ul class="rows">
          <li v-for="n in data.neglected" :key="n.name">
            <span>{{ n.name }}</span>
            <span class="muted">{{ n.days_since != null ? n.days_since + ' days' : 'no contact yet' }}</span>
          </li>
        </ul>
      </section>
    </div>
  </div>
</template>

<style scoped>
.cols { grid-template-columns: 1fr 1fr; margin-top: 18px; }
@media (max-width: 720px) { .cols { grid-template-columns: 1fr; } }
.score { text-align: center; }
.ring {
  width: 120px;
  height: 120px;
  margin: 4px auto 12px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: conic-gradient(var(--c) calc(v-bind('data.health_score') * 1%), var(--border) 0);
}
.ring span {
  width: 92px;
  height: 92px;
  border-radius: 50%;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30px;
  font-weight: 800;
  color: var(--c);
}
.small { font-size: 13px; }
.bars { list-style: none; padding: 0; margin: 0; display: grid; gap: 10px; }
.bars li { display: grid; grid-template-columns: 90px 1fr 28px; align-items: center; gap: 8px; }
.bars .k { text-transform: capitalize; font-size: 13px; color: var(--muted); }
.bar { background: var(--bg); border-radius: 999px; height: 10px; overflow: hidden; }
.bar i { display: block; height: 100%; background: var(--primary); border-radius: 999px; }
.bars .v { text-align: right; font-weight: 700; }
.rows { list-style: none; padding: 0; margin: 0; display: grid; gap: 10px; }
.rows li { display: flex; justify-content: space-between; }
</style>
