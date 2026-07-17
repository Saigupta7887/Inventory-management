<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  appleConfigured,
  googleConfigured,
  renderGoogleButton,
  signInWithApple,
} from '@/lib/social'

const auth = useAuthStore()
const router = useRouter()
const googleEl = ref(null)
const error = ref('')
const hasGoogle = googleConfigured()
const hasApple = appleConfigured()

function routeAfter(user) {
  router.push({ name: user.onboarded ? 'home' : 'onboarding' })
}

onMounted(() => {
  if (hasGoogle && googleEl.value) {
    renderGoogleButton(googleEl.value, async (credential) => {
      error.value = ''
      try {
        routeAfter(await auth.loginGoogle(credential))
      } catch (e) {
        error.value = e?.response?.data?.detail || 'Google sign-in failed.'
      }
    }).catch(() => (error.value = 'Could not load Google sign-in.'))
  }
})

async function apple() {
  error.value = ''
  try {
    const { identityToken, fullName } = await signInWithApple()
    routeAfter(await auth.loginApple(identityToken, fullName))
  } catch (e) {
    error.value = e?.response?.data?.detail || 'Apple sign-in failed.'
  }
}
</script>

<template>
  <div v-if="hasGoogle || hasApple" class="social">
    <div class="divider"><span>or</span></div>

    <div v-if="hasGoogle" ref="googleEl" class="gbtn"></div>

    <button v-if="hasApple" class="applebtn" @click="apple">
       Continue with Apple
    </button>

    <p v-if="error" class="err">{{ error }}</p>
  </div>
</template>

<style scoped>
.social { margin-top: 20px; }
.divider {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--muted);
  font-size: 13px;
  margin-bottom: 18px;
}
.divider::before, .divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border);
}
.gbtn { display: flex; justify-content: center; margin-bottom: 12px; min-height: 40px; }
.applebtn {
  width: 100%;
  padding: 14px;
  border-radius: 16px;
  background: #000;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}
.err { color: var(--high-fg); font-size: 13px; margin-top: 12px; text-align: center; }
</style>
