<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { usePeopleStore } from '@/stores/people'
import Avatar from '@/components/Avatar.vue'

const props = defineProps({ id: { type: [String, Number], required: true } })
const store = usePeopleStore()
const router = useRouter()

const person = ref(null)
const content = ref('')
const category = ref(null)
const pinned = ref(false)
const busy = ref(false)

const cats = [
  { key: 'life_update', label: 'Life Update' },
  { key: 'preference', label: 'Preference' },
  { key: 'family', label: 'Family' },
  { key: 'event', label: 'Event' },
  { key: 'goal', label: 'Goal' },
  { key: 'follow_up', label: 'Follow-up Topic' },
]

onMounted(async () => {
  person.value = await store.get(props.id)
})

async function save() {
  if (!content.value.trim()) return
  busy.value = true
  try {
    await store.addNote(props.id, {
      content: content.value,
      category: category.value || undefined,
      pinned: pinned.value,
    })
    router.push({ name: 'person', params: { id: props.id } })
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div v-if="person">
    <header class="bar">
      <button class="icon-btn" @click="router.back()">←</button>
    </header>

    <div class="head">
      <div>
        <h1>Add Note</h1>
        <p class="muted sub">Capture something important about {{ person.name.split(' ')[0] }}</p>
      </div>
      <Avatar :name="person.name" :size="52" />
    </div>

    <textarea
      v-model="content"
      class="textarea note"
      rows="5"
      placeholder="What did you learn or want to remember?&#10;&#10;Example: She mentioned her sister is getting married."
    ></textarea>

    <div class="media">
      <button class="media-btn" disabled title="Coming soon">🎤 Voice Note</button>
      <button class="media-btn" disabled title="Coming soon">📷 Photo</button>
    </div>

    <div class="ai-head">
      <span>AI Suggestions</span>
      <span class="beta">BETA</span>
    </div>
    <div class="chips">
      <button
        v-for="c in cats"
        :key="c.key"
        class="chip"
        :class="{ active: category === c.key }"
        @click="category = category === c.key ? null : c.key"
      >
        {{ c.label }}
      </button>
    </div>

    <label class="pin-row">
      <input type="checkbox" v-model="pinned" />
      <span>Pin this to the top of their profile</span>
    </label>

    <button class="btn save" :disabled="busy" @click="save">
      {{ busy ? 'Saving…' : 'Save Note' }}
    </button>
  </div>
</template>

<style scoped>
.bar { padding: 6px 0; }
.icon-btn { width: 38px; height: 38px; border-radius: 12px; background: var(--bg); font-size: 20px; color: var(--text); }
.head { display: flex; align-items: center; justify-content: space-between; margin: 6px 0 18px; }
.sub { margin-top: 6px; font-size: 14px; max-width: 220px; }
.note { min-height: 140px; margin-bottom: 14px; }
.media { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 22px; }
.media-btn {
  border: 1.5px solid var(--border); border-radius: 14px; padding: 14px;
  font-weight: 600; color: var(--text); background: #fff; opacity: 0.75;
}
.ai-head { display: flex; align-items: center; gap: 8px; font-weight: 700; margin-bottom: 12px; }
.beta { font-size: 10px; background: var(--primary-050); color: var(--primary); padding: 2px 7px; border-radius: 999px; }
.pin-row { display: flex; gap: 10px; align-items: center; margin: 18px 2px; font-size: 14px; color: var(--muted); }
.save { margin-top: 6px; }
</style>
