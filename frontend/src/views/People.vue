<script setup>
import { onMounted, ref, computed } from 'vue'
import { RouterLink } from 'vue-router'
import { usePeopleStore } from '@/stores/people'
import client from '@/api/client'

const store = usePeopleStore()
const showForm = ref(false)
const query = ref('')
const searchResults = ref(null)

const form = ref({
  name: '',
  relationship_type: 'friend',
  priority: 'medium',
  reminder_interval_days: 30,
  email: '',
  phone: '',
  birthday: '',
  tags: '',
})

onMounted(() => store.fetchAll())

const filtered = computed(() => {
  if (searchResults.value) {
    const ids = new Set(searchResults.value.map((r) => r.person_id))
    return store.people.filter((p) => ids.has(p.id))
  }
  return store.people
})

async function runSearch() {
  if (!query.value.trim()) {
    searchResults.value = null
    return
  }
  const { data } = await client.get('/api/search', { params: { q: query.value } })
  searchResults.value = data.results
}

async function addPerson() {
  const payload = { ...form.value }
  if (!payload.birthday) delete payload.birthday
  await store.create(payload)
  showForm.value = false
  form.value = {
    name: '',
    relationship_type: 'friend',
    priority: 'medium',
    reminder_interval_days: 30,
    email: '',
    phone: '',
    birthday: '',
    tags: '',
  }
}
</script>

<template>
  <div>
    <div class="head">
      <h1>People</h1>
      <button class="btn" @click="showForm = !showForm">＋ Add person</button>
    </div>

    <div class="searchbar card">
      <input
        v-model="query"
        class="input"
        placeholder="Search — try “who likes coffee” or “who mentioned interviews”"
        @keyup.enter="runSearch"
      />
      <button class="btn secondary" @click="runSearch">Search</button>
      <button v-if="searchResults" class="btn ghost" @click="query = ''; searchResults = null">
        Clear
      </button>
    </div>

    <form v-if="showForm" class="card form" @submit.prevent="addPerson">
      <div class="row">
        <div class="field">
          <label class="label">Name *</label>
          <input v-model="form.name" class="input" required />
        </div>
        <div class="field">
          <label class="label">Relationship</label>
          <select v-model="form.relationship_type" class="select">
            <option>family</option>
            <option>friend</option>
            <option>partner</option>
            <option>work</option>
            <option>networking</option>
          </select>
        </div>
      </div>
      <div class="row">
        <div class="field">
          <label class="label">Priority</label>
          <select v-model="form.priority" class="select">
            <option value="very_high">Very high</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>
        <div class="field">
          <label class="label">Remind me every (days)</label>
          <input v-model.number="form.reminder_interval_days" type="number" min="1" class="input" />
        </div>
      </div>
      <div class="row">
        <div class="field">
          <label class="label">Email</label>
          <input v-model="form.email" class="input" />
        </div>
        <div class="field">
          <label class="label">Birthday</label>
          <input v-model="form.birthday" type="date" class="input" />
        </div>
      </div>
      <div class="field">
        <label class="label">Tags (comma-separated)</label>
        <input v-model="form.tags" class="input" placeholder="coffee, college, mentor" />
      </div>
      <button class="btn" type="submit">Save person</button>
    </form>

    <p v-if="store.loading" class="muted">Loading…</p>
    <p v-else-if="!filtered.length" class="muted">
      {{ searchResults ? 'No matches.' : 'No people yet — add your first one above.' }}
    </p>

    <div class="grid people">
      <RouterLink
        v-for="p in filtered"
        :key="p.id"
        :to="{ name: 'person', params: { id: p.id } }"
        class="card person"
      >
        <div class="avatar">{{ p.name.charAt(0).toUpperCase() }}</div>
        <div class="meta">
          <strong>{{ p.name }}</strong>
          <div class="muted small">{{ p.relationship_type || 'contact' }}</div>
        </div>
        <span class="pill" :class="p.priority">{{ p.priority.replace('_', ' ') }}</span>
      </RouterLink>
    </div>
  </div>
</template>

<style scoped>
.head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.searchbar {
  display: flex;
  gap: 10px;
  align-items: center;
  margin: 16px 0;
  padding: 12px;
}
.searchbar .input {
  flex: 1;
}
.form {
  margin-bottom: 20px;
}
.row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.people {
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
}
.person {
  display: flex;
  align-items: center;
  gap: 12px;
}
.avatar {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: var(--primary-soft);
  color: var(--primary-dark);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
}
.meta {
  flex: 1;
}
.small {
  font-size: 13px;
}
</style>
