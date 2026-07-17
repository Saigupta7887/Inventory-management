<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import client from '@/api/client'
import Avatar from '@/components/Avatar.vue'

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

// Build a conic-gradient ring from the health breakdown.
const ring = computed(() => {
  const b = data.value?.health_breakdown || { healthy: 100, needs_attention: 0, overdue: 0 }
  const h = b.healthy
  const n = h + b.needs_attention
  return `conic-gradient(var(--low-fg) 0 ${h}%, var(--medium-fg) ${h}% ${n}%, var(--high-fg) ${n}% 100%)`
})
</script>

<template>
  <div>
    <header class="head">
      <h1>Insights</h1>
      <div class="period">This Week ▾</div>
    </header>

    <p v-if="loading" class="spinner">Loading…</p>

    <template v-else>
      <div class="card health">
        <h3>Relationship Health</h3>
        <div class="hbody">
          <div class="ring" :style="{ background: ring }">
            <div class="hole">
              <span class="pct">{{ data.health_score }}%</span>
              <span class="muted lbl">Healthy</span>
            </div>
          </div>
          <ul class="legend">
            <li><span class="d low"></span>Healthy <b>{{ data.health_breakdown.healthy }}%</b></li>
            <li><span class="d med"></span>Needs Attention <b>{{ data.health_breakdown.needs_attention }}%</b></li>
            <li><span class="d high"></span>Overdue <b>{{ data.health_breakdown.overdue }}%</b></li>
          </ul>
        </div>
      </div>

      <h3 class="section">You this week</h3>
      <div class="tiles">
        <div class="tile">
          <div class="num">{{ data.week.people_contacted }}</div>
          <div class="muted">People Contacted</div>
        </div>
        <div class="tile">
          <div class="num">{{ data.week.followups_completed }}</div>
          <div class="muted">Follow-ups</div>
        </div>
        <div class="tile">
          <div class="num">{{ data.week.notes_added }}</div>
          <div class="muted">Notes Added</div>
        </div>
      </div>

      <h3 class="section">People needing your attention</h3>
      <p v-if="!data.needs_attention.length" class="muted empty">Everyone's up to date. 🎉</p>
      <RouterLink
        v-for="p in data.needs_attention"
        :key="p.person_id"
        :to="{ name: 'person', params: { id: p.person_id } }"
        class="row"
      >
        <Avatar :name="p.name" :size="44" />
        <div class="grow">
          <strong>{{ p.name }}</strong>
          <div class="muted small">
            {{ p.days_since != null ? 'Last talked ' + p.days_since + ' days ago' : 'No contact yet' }}
          </div>
        </div>
        <span class="pill" :class="p.priority">{{ p.priority.replace('_', ' ') }}</span>
      </RouterLink>
    </template>
  </div>
</template>

<style scoped>
.head { display: flex; align-items: center; justify-content: space-between; margin-top: 6px; }
.period { font-size: 13px; font-weight: 700; color: var(--primary); background: var(--primary-050); padding: 8px 12px; border-radius: 10px; }
.health h3 { margin-bottom: 14px; }
.hbody { display: flex; align-items: center; gap: 18px; }
.ring {
  width: 120px; height: 120px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.hole {
  width: 88px; height: 88px; border-radius: 50%; background: #fff;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
}
.pct { font-size: 26px; font-weight: 800; }
.lbl { font-size: 12px; }
.legend { list-style: none; padding: 0; margin: 0; display: grid; gap: 10px; font-size: 14px; flex: 1; }
.legend li { display: flex; align-items: center; gap: 8px; }
.legend b { margin-left: auto; }
.d { width: 10px; height: 10px; border-radius: 50%; }
.d.low { background: var(--low-fg); }
.d.med { background: var(--medium-fg); }
.d.high { background: var(--high-fg); }
.section { margin: 24px 2px 12px; }
.tiles { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
.tile { background: #fff; border: 1px solid var(--border); border-radius: 16px; padding: 16px 8px; text-align: center; box-shadow: var(--shadow); }
.tile .num { font-size: 30px; font-weight: 800; color: var(--primary); }
.tile .muted { font-size: 12px; margin-top: 4px; }
.empty { padding: 10px 2px; }
.row { display: flex; align-items: center; gap: 12px; padding: 12px 2px; border-bottom: 1px solid var(--border); }
.row .grow { flex: 1; }
.small { font-size: 13px; }
</style>
