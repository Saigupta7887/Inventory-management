<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Avatar from '@/components/Avatar.vue'

const auth = useAuthStore()
const router = useRouter()

const editing = ref(false)
const reminderStyle = ref('balanced')
const ai = ref(true)
const fullName = ref('')
const saved = ref(false)

onMounted(async () => {
  if (!auth.user) await auth.fetchMe().catch(() => {})
  if (auth.user) {
    reminderStyle.value = auth.user.reminder_style
    ai.value = auth.user.ai_suggestions_enabled
    fullName.value = auth.user.full_name || ''
  }
})

const preferences = [
  { icon: '🔔', label: 'Reminder Preferences' },
  { icon: '📣', label: 'Notification Settings' },
  { icon: '✨', label: 'AI Preferences' },
  { icon: '🔒', label: 'Privacy & Data' },
]
const account = [
  { icon: '📥', label: 'Import Contacts' },
  { icon: '💾', label: 'Backup & Export' },
  { icon: '👤', label: 'Account Details' },
  { icon: '❓', label: 'Help & Support' },
]

async function save() {
  await auth.savePreferences({
    reminder_style: reminderStyle.value,
    ai_suggestions_enabled: ai.value,
    full_name: fullName.value,
  })
  saved.value = true
  editing.value = false
  setTimeout(() => (saved.value = false), 2000)
}

function logout() {
  auth.logout()
  router.push({ name: 'welcome' })
}
</script>

<template>
  <div>
    <h1 class="pagetitle">Settings</h1>

    <div class="card profile" @click="editing = !editing">
      <Avatar :name="auth.user?.full_name || auth.user?.email || '?'" :size="48" />
      <div class="grow">
        <strong>{{ auth.user?.full_name || 'Your name' }}</strong>
        <div class="muted small">{{ auth.user?.email }}</div>
      </div>
      <span class="chev">›</span>
    </div>

    <div v-if="editing" class="card edit">
      <div class="field">
        <label class="label">Name</label>
        <input v-model="fullName" class="input" />
      </div>
      <div class="field">
        <label class="label">Reminder style</label>
        <select v-model="reminderStyle" class="select">
          <option value="gentle">Gentle</option>
          <option value="balanced">Balanced</option>
          <option value="active">Active</option>
        </select>
      </div>
      <label class="toggle">
        <input type="checkbox" v-model="ai" /> AI suggestions
      </label>
      <button class="btn" @click="save">Save changes</button>
    </div>
    <p v-if="saved" class="saved">✓ Saved</p>

    <h3 class="group-title">Preferences</h3>
    <div class="group">
      <button v-for="p in preferences" :key="p.label" class="setrow" @click="editing = true">
        <span class="ic">{{ p.icon }}</span><span class="grow">{{ p.label }}</span><span class="chev">›</span>
      </button>
    </div>

    <h3 class="group-title">Account</h3>
    <div class="group">
      <button v-for="a in account" :key="a.label" class="setrow">
        <span class="ic">{{ a.icon }}</span><span class="grow">{{ a.label }}</span><span class="chev">›</span>
      </button>
    </div>

    <button class="logout" @click="logout">Log Out</button>
  </div>
</template>

<style scoped>
.pagetitle { margin: 8px 0 18px; }
.profile { display: flex; align-items: center; gap: 14px; cursor: pointer; }
.profile .grow { flex: 1; }
.profile strong { font-size: 16px; }
.small { font-size: 13px; }
.edit { margin-top: 12px; }
.toggle { display: flex; gap: 10px; align-items: center; margin-bottom: 16px; font-size: 14px; }
.saved { color: var(--success); font-weight: 700; text-align: center; margin: 10px 0; }
.group-title { margin: 22px 2px 10px; color: var(--muted); }
.group { background: #fff; border: 1px solid var(--border); border-radius: 16px; overflow: hidden; box-shadow: var(--shadow); }
.setrow {
  display: flex; align-items: center; gap: 14px; width: 100%;
  padding: 15px 16px; font-size: 15px; font-weight: 600; color: var(--text);
  border-bottom: 1px solid var(--border);
}
.setrow:last-child { border-bottom: none; }
.setrow .grow { flex: 1; text-align: left; }
.ic {
  width: 34px; height: 34px; border-radius: 10px; background: var(--primary-050);
  display: flex; align-items: center; justify-content: center; font-size: 17px;
}
.chev { color: var(--muted); font-size: 20px; }
.logout {
  width: 100%; margin: 22px 0 10px; padding: 15px;
  border-radius: 16px; background: var(--high-bg); color: var(--high-fg);
  font-weight: 700; font-size: 16px;
}
</style>
