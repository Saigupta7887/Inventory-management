<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const reminderStyle = ref('balanced')
const aiSuggestions = ref(true)
const busy = ref(false)

const styles = [
  { key: 'gentle', label: 'Gentle', desc: 'Occasional nudges' },
  { key: 'balanced', label: 'Balanced', desc: 'A steady rhythm' },
  { key: 'active', label: 'Active', desc: 'Stay on top of it' },
]

async function finish() {
  busy.value = true
  try {
    await auth.savePreferences({
      reminder_style: reminderStyle.value,
      ai_suggestions_enabled: aiSuggestions.value,
      onboarded: true,
    })
    router.push({ name: 'dashboard' })
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="onboarding">
    <div class="card">
      <h1>Welcome to Bondly 👋</h1>
      <p class="muted">A couple of quick preferences and you're set.</p>

      <h3 style="margin-top: 24px">How often should we remind you?</h3>
      <div class="choices">
        <button
          v-for="s in styles"
          :key="s.key"
          class="choice"
          :class="{ active: reminderStyle === s.key }"
          @click="reminderStyle = s.key"
        >
          <strong>{{ s.label }}</strong>
          <span class="muted">{{ s.desc }}</span>
        </button>
      </div>

      <label class="toggle">
        <input type="checkbox" v-model="aiSuggestions" />
        <span>Enable AI suggestions (note categorization &amp; message drafts)</span>
      </label>

      <button class="btn full" :disabled="busy" @click="finish">
        {{ busy ? 'Saving…' : 'Enter Bondly' }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.onboarding {
  max-width: 480px;
  margin: 8vh auto 0;
}
.choices {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-bottom: 20px;
}
.choice {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 14px 10px;
  border: 1px solid var(--border);
  border-radius: 12px;
  background: #fff;
  text-align: center;
}
.choice.active {
  border-color: var(--primary);
  background: var(--primary-soft);
}
.toggle {
  display: flex;
  gap: 10px;
  align-items: center;
  font-size: 14px;
  margin: 12px 0 22px;
}
.btn.full {
  width: 100%;
  justify-content: center;
}
</style>
