<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { usePeopleStore } from '@/stores/people'
import Avatar from '@/components/Avatar.vue'

const props = defineProps({ id: { type: [String, Number], required: true } })
const store = usePeopleStore()
const router = useRouter()

const person = ref(null)
const summary = ref('')
const followUp = ref('')
const busy = ref(false)
const typeIdx = ref(0)
const moodIdx = ref(2)

const types = [
  { key: 'call', label: 'Call', icon: '📞' },
  { key: 'text', label: 'Text', icon: '💬' },
  { key: 'meeting', label: 'In Person', icon: '🧑‍🤝‍🧑' },
  { key: 'email', label: 'Email', icon: '✉️' },
  { key: 'meeting', label: 'Meeting', icon: '📅' },
  { key: 'call', label: 'Video Call', icon: '🎥' },
  { key: 'other', label: 'Other', icon: '•••' },
]
const moods = [
  { key: 'negative', e: '🙁' },
  { key: 'neutral', e: '😐' },
  { key: 'positive', e: '🙂' },
  { key: 'positive', e: '😀' },
]

onMounted(async () => {
  person.value = await store.get(props.id)
})

async function save() {
  busy.value = true
  try {
    await store.logInteraction(props.id, {
      channel: types[typeIdx.value].key,
      summary: summary.value,
      follow_up: followUp.value,
      mood: moods[moodIdx.value].key,
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
    <h1>Log Interaction</h1>

    <p class="q">Who was this with?</p>
    <div class="who card">
      <Avatar :name="person.name" :size="42" />
      <strong>{{ person.name }}</strong>
    </div>

    <p class="q">Type of interaction</p>
    <div class="type-grid">
      <button
        v-for="(t, i) in types"
        :key="i"
        class="type"
        :class="{ active: typeIdx === i }"
        @click="typeIdx = i"
      >
        <span class="ic">{{ t.icon }}</span>{{ t.label }}
      </button>
    </div>

    <p class="q">Summary</p>
    <textarea v-model="summary" class="textarea" rows="3" placeholder="What did you talk about?"></textarea>

    <p class="q">Follow-up (optional)</p>
    <input v-model="followUp" class="input" placeholder="Anything to check on later?" />

    <p class="q">Mood</p>
    <div class="moods">
      <button
        v-for="(m, i) in moods"
        :key="i"
        class="mood"
        :class="{ active: moodIdx === i }"
        @click="moodIdx = i"
      >
        {{ m.e }}
      </button>
    </div>

    <button class="btn save" :disabled="busy" @click="save">
      {{ busy ? 'Saving…' : 'Save Interaction' }}
    </button>
  </div>
</template>

<style scoped>
.bar { padding: 6px 0; }
.icon-btn { width: 38px; height: 38px; border-radius: 12px; background: var(--bg); font-size: 20px; color: var(--text); }
.q { font-weight: 700; margin: 20px 0 10px; }
.who { display: flex; align-items: center; gap: 12px; padding: 12px 14px; }
.type-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
.type {
  display: flex; flex-direction: column; align-items: center; gap: 5px;
  padding: 12px 4px; border: 1.5px solid var(--border); border-radius: 14px;
  background: #fff; font-size: 11px; font-weight: 600; color: var(--text);
}
.type .ic { font-size: 18px; }
.type.active { border-color: var(--primary); background: var(--primary-050); color: var(--primary); }
.moods { display: flex; gap: 10px; }
.mood {
  flex: 1; padding: 12px 0; font-size: 26px;
  border: 1.5px solid var(--border); border-radius: 14px; background: #fff;
}
.mood.active { border-color: var(--primary); background: var(--primary-050); }
.save { margin-top: 24px; }
</style>
