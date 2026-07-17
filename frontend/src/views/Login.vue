<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import BrandMark from '@/components/BrandMark.vue'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const mode = ref(route.query.mode === 'login' ? 'login' : 'register')
const email = ref('')
const password = ref('')
const fullName = ref('')
const error = ref('')
const busy = ref(false)

async function submit() {
  error.value = ''
  busy.value = true
  try {
    if (mode.value === 'register') {
      await auth.register(email.value, password.value, fullName.value)
      router.push({ name: 'onboarding' })
    } else {
      const user = await auth.login(email.value, password.value)
      router.push({ name: user.onboarded ? 'home' : 'onboarding' })
    }
  } catch (e) {
    error.value = e?.response?.data?.detail || 'Something went wrong. Try again.'
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="auth">
    <div class="head">
      <BrandMark :size="52" />
      <div class="wordmark">bondly</div>
    </div>

    <div class="tabs">
      <button :class="{ active: mode === 'register' }" @click="mode = 'register'">Create account</button>
      <button :class="{ active: mode === 'login' }" @click="mode = 'login'">Log in</button>
    </div>

    <form @submit.prevent="submit">
      <div v-if="mode === 'register'" class="field">
        <label class="label">Name</label>
        <input v-model="fullName" class="input" placeholder="Your name" />
      </div>
      <div class="field">
        <label class="label">Email</label>
        <input v-model="email" type="email" class="input" required placeholder="you@example.com" />
      </div>
      <div class="field">
        <label class="label">Password</label>
        <input v-model="password" type="password" class="input" required minlength="6" placeholder="••••••••" />
      </div>
      <p v-if="error" class="error">{{ error }}</p>
      <button class="btn grad" :disabled="busy">
        {{ busy ? 'Please wait…' : mode === 'register' ? 'Create account' : 'Log in' }}
      </button>
    </form>
  </div>
</template>

<style scoped>
.auth { padding: 5vh 6px; }
.head { text-align: center; margin-bottom: 26px; }
.wordmark { font-size: 30px; font-weight: 800; letter-spacing: -0.03em; margin-top: 4px; }
.tabs {
  display: flex;
  gap: 4px;
  background: var(--bg);
  padding: 5px;
  border-radius: 14px;
  margin-bottom: 22px;
}
.tabs button {
  flex: 1;
  padding: 11px;
  border-radius: 10px;
  font-weight: 700;
  font-size: 14px;
  color: var(--muted);
}
.tabs button.active { background: #fff; color: var(--text); box-shadow: var(--shadow); }
.error { color: var(--high-fg); font-size: 13px; margin: 0 0 14px; }
</style>
