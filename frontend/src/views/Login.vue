<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const mode = ref('register') // 'register' | 'login'
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
      router.push({ name: user.onboarded ? 'dashboard' : 'onboarding' })
    }
  } catch (e) {
    error.value =
      e?.response?.data?.detail || 'Something went wrong. Please try again.'
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="auth">
    <div class="card">
      <div class="tabs">
        <button :class="{ active: mode === 'register' }" @click="mode = 'register'">
          Create account
        </button>
        <button :class="{ active: mode === 'login' }" @click="mode = 'login'">
          Log in
        </button>
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

        <button class="btn full" :disabled="busy">
          {{ busy ? 'Please wait…' : mode === 'register' ? 'Create account' : 'Log in' }}
        </button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.auth {
  max-width: 400px;
  margin: 8vh auto 0;
}
.tabs {
  display: flex;
  gap: 6px;
  margin-bottom: 20px;
  background: var(--bg);
  padding: 4px;
  border-radius: 10px;
}
.tabs button {
  flex: 1;
  border: none;
  background: transparent;
  padding: 8px;
  border-radius: 8px;
  font-weight: 600;
  color: var(--muted);
}
.tabs button.active {
  background: #fff;
  color: var(--text);
  box-shadow: var(--shadow);
}
.btn.full {
  width: 100%;
  justify-content: center;
  margin-top: 6px;
}
.error {
  color: var(--danger);
  font-size: 13px;
  margin: 0 0 12px;
}
</style>
