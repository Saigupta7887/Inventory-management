<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const focus = ref('family')
const reminderStyle = ref('gentle')
const frequency = ref(1) // 0 less, 1 balanced, 2 more
const ai = ref(true)
const busy = ref(false)

const focuses = [
  { key: 'family', label: 'Family', icon: '👨‍👩‍👧' },
  { key: 'friends', label: 'Friends', icon: '🧑‍🤝‍🧑' },
  { key: 'work', label: 'Work', icon: '💼' },
  { key: 'mentors', label: 'Mentors', icon: '🎓' },
  { key: 'partner', label: 'Partner', icon: '💗' },
  { key: 'others', label: 'Others', icon: '🌐' },
]

async function finish() {
  busy.value = true
  try {
    await auth.savePreferences({
      reminder_style: reminderStyle.value,
      ai_suggestions_enabled: ai.value,
      onboarded: true,
    })
    router.push({ name: 'home' })
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="onb">
    <div class="progress">
      <span class="dot active"></span>
      <span class="dot"></span><span class="dot"></span><span class="dot"></span>
    </div>

    <h1>Let's personalize<br />Bondly for you 👋</h1>
    <p class="muted sub">These preferences help us give you better reminders and insights.</p>

    <h3 class="q">What's your main focus?</h3>
    <div class="focus-grid">
      <button
        v-for="f in focuses"
        :key="f.key"
        class="focus"
        :class="{ active: focus === f.key }"
        @click="focus = f.key"
      >
        <span class="ic">{{ f.icon }}</span>
        <span>{{ f.label }}</span>
      </button>
    </div>

    <h3 class="q">Reminder style</h3>
    <div class="style-row">
      <button class="style" :class="{ active: reminderStyle === 'gentle' }" @click="reminderStyle = 'gentle'">
        <strong>Gentle</strong><span class="muted">Subtle reminders</span>
      </button>
      <button class="style" :class="{ active: reminderStyle === 'balanced' }" @click="reminderStyle = 'balanced'">
        <strong>Regular</strong><span class="muted">Standard alerts</span>
      </button>
    </div>

    <h3 class="q">How often would you like reminders?</h3>
    <input type="range" min="0" max="2" step="1" v-model.number="frequency" class="slider" />
    <div class="scale"><span>Less</span><span>Balanced</span><span>More</span></div>

    <div class="toggle-row">
      <span>AI suggestions</span>
      <button class="switch" :class="{ on: ai }" @click="ai = !ai"><span></span></button>
    </div>

    <button class="btn" :disabled="busy" @click="finish">
      {{ busy ? 'Saving…' : 'Continue' }}
    </button>
  </div>
</template>

<style scoped>
.onb { padding: 8px 4px 20px; }
.progress { display: flex; gap: 8px; margin: 8px 0 20px; }
.dot { width: 26px; height: 6px; border-radius: 999px; background: var(--border); }
.dot.active { background: var(--primary); width: 30px; }
.sub { margin: 8px 0 4px; font-size: 14px; }
.q { margin: 24px 0 12px; }
.focus-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
.focus {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px 6px;
  border: 1.5px solid var(--border);
  border-radius: 16px;
  background: #fff;
  font-size: 13px;
  font-weight: 600;
}
.focus.active { border-color: var(--primary); background: var(--primary-050); color: var(--primary); }
.focus .ic { font-size: 24px; }
.style-row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.style {
  display: flex;
  flex-direction: column;
  gap: 3px;
  align-items: flex-start;
  padding: 14px;
  border: 1.5px solid var(--border);
  border-radius: 16px;
  background: #fff;
  font-size: 13px;
}
.style strong { font-size: 15px; }
.style.active { border-color: var(--primary); background: var(--primary-050); }
.slider { width: 100%; accent-color: var(--primary); }
.scale { display: flex; justify-content: space-between; font-size: 12px; color: var(--muted); margin-top: 4px; }
.toggle-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 26px 0 20px;
  font-weight: 600;
}
.switch {
  width: 52px;
  height: 30px;
  border-radius: 999px;
  background: var(--border);
  position: relative;
  transition: background 0.2s;
}
.switch.on { background: var(--primary); }
.switch span {
  position: absolute;
  top: 3px;
  left: 3px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #fff;
  transition: left 0.2s;
}
.switch.on span { left: 25px; }
</style>
