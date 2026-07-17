<script setup>
import { onMounted, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const reminderStyle = ref('balanced')
const aiSuggestions = ref(true)
const fullName = ref('')
const saved = ref(false)
const busy = ref(false)

onMounted(async () => {
  if (!auth.user) await auth.fetchMe().catch(() => {})
  if (auth.user) {
    reminderStyle.value = auth.user.reminder_style
    aiSuggestions.value = auth.user.ai_suggestions_enabled
    fullName.value = auth.user.full_name || ''
  }
})

async function save() {
  busy.value = true
  saved.value = false
  try {
    await auth.savePreferences({
      reminder_style: reminderStyle.value,
      ai_suggestions_enabled: aiSuggestions.value,
      full_name: fullName.value,
    })
    saved.value = true
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="settings">
    <h1>Settings</h1>

    <section class="card">
      <h2>Profile</h2>
      <div class="field">
        <label class="label">Name</label>
        <input v-model="fullName" class="input" />
      </div>
      <div class="field">
        <label class="label">Email</label>
        <input :value="auth.user?.email" class="input" disabled />
      </div>
    </section>

    <section class="card">
      <h2>Preferences</h2>
      <div class="field">
        <label class="label">Reminder style</label>
        <select v-model="reminderStyle" class="select">
          <option value="gentle">Gentle</option>
          <option value="balanced">Balanced</option>
          <option value="active">Active</option>
        </select>
      </div>
      <label class="toggle">
        <input type="checkbox" v-model="aiSuggestions" />
        <span>AI suggestions (note categorization &amp; message drafts)</span>
      </label>
    </section>

    <div class="actions">
      <button class="btn" :disabled="busy" @click="save">
        {{ busy ? 'Saving…' : 'Save changes' }}
      </button>
      <span v-if="saved" class="saved">✓ Saved</span>
    </div>
  </div>
</template>

<style scoped>
.settings { max-width: 560px; }
.card { margin-bottom: 16px; }
.toggle { display: flex; gap: 10px; align-items: center; font-size: 14px; }
.actions { display: flex; align-items: center; gap: 12px; }
.saved { color: var(--success); font-weight: 600; }
</style>
