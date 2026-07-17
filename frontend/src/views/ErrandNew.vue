<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useLocationStore } from '@/stores/location'
import { usePeopleStore } from '@/stores/people'

const router = useRouter()
const location = useLocationStore()
const people = usePeopleStore()

const title = ref('')
const placeType = ref('grocery')
const personId = ref('')
const note = ref('')
const types = ref([])
const busy = ref(false)

onMounted(async () => {
  types.value = await location.placeTypes()
  if (!people.people.length) await people.fetchAll()
})

async function save() {
  if (!title.value.trim()) return
  busy.value = true
  try {
    await location.createErrand({
      title: title.value,
      place_type: placeType.value,
      person_id: personId.value ? Number(personId.value) : null,
      note: note.value || null,
    })
    router.push({ name: 'nearby' })
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div>
    <header class="bar">
      <button class="icon-btn" @click="router.back()">←</button>
      <h1>Add Errand</h1>
    </header>

    <p class="muted intro">
      Something to pick up or do for someone at a type of place. Bondly reminds you
      when you’re there.
    </p>

    <div class="field">
      <label class="label">What to do</label>
      <input v-model="title" class="input" placeholder="e.g. Pick up matcha" />
    </div>

    <div class="field">
      <label class="label">At which kind of place?</label>
      <select v-model="placeType" class="select">
        <option v-for="t in types" :key="t" :value="t">{{ t }}</option>
      </select>
    </div>

    <div class="field">
      <label class="label">For someone? (optional)</label>
      <select v-model="personId" class="select">
        <option value="">— No one in particular —</option>
        <option v-for="p in people.people" :key="p.id" :value="p.id">{{ p.name }}</option>
      </select>
    </div>

    <div class="field">
      <label class="label">Note (optional)</label>
      <input v-model="note" class="input" placeholder="Details…" />
    </div>

    <button class="btn" :disabled="busy" @click="save">
      {{ busy ? 'Saving…' : 'Save errand' }}
    </button>
  </div>
</template>

<style scoped>
.bar { display: flex; align-items: center; gap: 12px; padding: 6px 0 14px; }
.icon-btn { width: 38px; height: 38px; border-radius: 12px; background: var(--bg); font-size: 20px; color: var(--text); }
.intro { font-size: 14px; margin-bottom: 20px; }
.select { text-transform: capitalize; }
</style>
