<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { usePeopleStore } from '@/stores/people'
import client from '@/api/client'
import Avatar from '@/components/Avatar.vue'
import PersonForm from '@/components/PersonForm.vue'

const store = usePeopleStore()
const route = useRoute()

const query = ref('')
const searchIds = ref(null)
const filter = ref('all')
const showForm = ref(false)

const filters = ['all', 'family', 'friends', 'work', 'partner', 'mentors']

onMounted(async () => {
  await store.fetchAll()
  if (route.query.add) showForm.value = true
})

const list = computed(() => {
  let items = store.people
  if (searchIds.value) {
    const ids = new Set(searchIds.value)
    items = items.filter((p) => ids.has(p.id))
  }
  if (filter.value !== 'all') {
    items = items.filter(
      (p) => (p.relationship_type || '').toLowerCase().startsWith(filter.value.slice(0, 4)),
    )
  }
  return items
})

async function runSearch() {
  if (!query.value.trim()) {
    searchIds.value = null
    return
  }
  const { data } = await client.get('/api/search', { params: { q: query.value } })
  searchIds.value = data.results.map((r) => r.person_id)
}

function daysAgo(dt) {
  if (!dt) return 'No contact yet'
  const d = Math.floor((Date.now() - new Date(dt)) / 86400000)
  return d === 0 ? 'Talked today' : `Last talked ${d} day${d === 1 ? '' : 's'} ago`
}

async function onCreated() {
  showForm.value = false
}
</script>

<template>
  <div>
    <header class="head">
      <h1>People</h1>
      <button class="add" @click="showForm = true">+</button>
    </header>

    <div class="search">
      <span class="mag">🔍</span>
      <input
        v-model="query"
        class="sinput"
        placeholder="Search people…"
        @keyup.enter="runSearch"
        @input="query || (searchIds = null)"
      />
      <button class="filt" @click="runSearch">⌕</button>
    </div>

    <div class="chips">
      <button
        v-for="f in filters"
        :key="f"
        class="chip"
        :class="{ active: filter === f }"
        @click="filter = f"
      >
        {{ f === 'all' ? 'All' : f.charAt(0).toUpperCase() + f.slice(1) }}
      </button>
    </div>

    <p v-if="store.loading" class="spinner">Loading…</p>
    <p v-else-if="!list.length" class="muted empty">
      {{ searchIds ? 'No matches.' : 'No people yet — tap + to add someone.' }}
    </p>

    <RouterLink
      v-for="p in list"
      :key="p.id"
      :to="{ name: 'person', params: { id: p.id } }"
      class="row"
    >
      <Avatar :name="p.name" :size="48" />
      <div class="grow">
        <strong>{{ p.name }}</strong>
        <div class="muted rel">{{ p.relationship_type || 'Contact' }}</div>
        <div class="muted small">{{ daysAgo(p.last_interaction_at) }}</div>
      </div>
      <span class="pill" :class="p.priority">{{ p.priority.replace('_', ' ') }}</span>
    </RouterLink>

    <PersonForm v-if="showForm" @close="showForm = false" @created="onCreated" />
  </div>
</template>

<style scoped>
.head { display: flex; align-items: center; justify-content: space-between; margin-top: 6px; }
.add {
  width: 38px; height: 38px; border-radius: 12px;
  background: var(--primary-050); color: var(--primary);
  font-size: 24px; font-weight: 700; line-height: 1;
}
.search {
  display: flex; align-items: center; gap: 8px;
  background: #f3f1fa; border-radius: 14px; padding: 4px 12px;
  margin: 16px 0 14px;
}
.mag { opacity: 0.6; }
.sinput { flex: 1; border: none; background: none; padding: 12px 0; font-size: 15px; outline: none; color: var(--text); }
.filt { color: var(--primary); font-size: 20px; padding: 0 4px; }
.empty { padding: 30px 4px; text-align: center; }
.row {
  display: flex; align-items: center; gap: 14px;
  padding: 14px 2px;
  border-bottom: 1px solid var(--border);
}
.row .grow { flex: 1; }
.row strong { font-size: 16px; }
.rel { font-size: 13px; }
.small { font-size: 12px; }
</style>
