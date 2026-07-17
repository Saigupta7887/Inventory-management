<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import BrandMark from '@/components/BrandMark.vue'
import Avatar from '@/components/Avatar.vue'

defineEmits(['add'])
const auth = useAuthStore()
const router = useRouter()

const links = [
  { name: 'home', label: 'Home', d: 'M3 10.5 12 3l9 7.5M5 9.5V20h5v-6h4v6h5V9.5' },
  { name: 'people', label: 'People', d: 'M16 19c0-2.2-1.8-4-4-4s-4 1.8-4 4M12 11a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z' },
  { name: 'reminders', label: 'Reminders', d: 'M18 8a6 6 0 1 0-12 0c0 7-3 8-3 8h18s-3-1-3-8M13.7 21a2 2 0 0 1-3.4 0' },
  { name: 'nearby', label: 'Nearby', d: 'M12 21s7-5.7 7-11a7 7 0 1 0-14 0c0 5.3 7 11 7 11ZM12 12a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5Z' },
  { name: 'insights', label: 'Insights', d: 'M4 20V10M10 20V4M16 20v-7M22 20H2' },
  { name: 'settings', label: 'Settings', d: 'M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6ZM19.4 15a1.6 1.6 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.6 1.6 0 0 0-2.7 1.1V21a2 2 0 1 1-4 0v-.1A1.6 1.6 0 0 0 6.6 19l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1A1.6 1.6 0 0 0 4 13.6H4a2 2 0 1 1 0-4h.1A1.6 1.6 0 0 0 5 6.6l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1A1.6 1.6 0 0 0 10 4V4a2 2 0 1 1 4 0v.1a1.6 1.6 0 0 0 2.7 1.1l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.6 1.6 0 0 0 .9 2.8' },
]

function logout() {
  auth.logout()
  router.push({ name: 'welcome' })
}
</script>

<template>
  <aside class="sidebar">
    <RouterLink :to="{ name: 'home' }" class="brand">
      <BrandMark :size="30" /><span>bondly</span>
    </RouterLink>

    <button class="add" @click="$emit('add')">＋ Quick add</button>

    <nav>
      <RouterLink
        v-for="l in links"
        :key="l.name"
        :to="{ name: l.name }"
        class="link"
        active-class="active"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path :d="l.d" /></svg>
        <span>{{ l.label }}</span>
      </RouterLink>
    </nav>

    <div class="foot">
      <div class="me">
        <Avatar :name="auth.user?.full_name || auth.user?.email || '?'" :size="34" />
        <div class="who">
          <strong>{{ auth.user?.full_name || 'You' }}</strong>
          <span class="muted">{{ auth.user?.email }}</span>
        </div>
      </div>
      <button class="logout" @click="logout">Log out</button>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  width: 250px;
  flex-shrink: 0;
  height: 100dvh;
  position: sticky;
  top: 0;
  background: #fff;
  border-right: 1px solid var(--border);
  padding: 22px 16px;
  display: flex;
  flex-direction: column;
}
.brand { display: flex; align-items: center; gap: 10px; font-size: 22px; font-weight: 800; letter-spacing: -0.03em; padding: 0 8px 18px; }
.add {
  background: var(--grad); color: #fff; font-weight: 700; font-size: 15px;
  padding: 12px; border-radius: 14px; margin-bottom: 16px;
}
nav { display: flex; flex-direction: column; gap: 4px; }
.link {
  display: flex; align-items: center; gap: 12px;
  padding: 12px 14px; border-radius: 12px;
  color: var(--muted); font-weight: 600; font-size: 15px;
}
.link:hover { background: var(--bg); color: var(--text); }
.link.active { background: var(--primary-050); color: var(--primary); }
.foot { margin-top: auto; padding-top: 16px; border-top: 1px solid var(--border); }
.me { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
.me .who { display: flex; flex-direction: column; overflow: hidden; }
.me strong { font-size: 14px; }
.me .muted { font-size: 12px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.logout {
  width: 100%; padding: 10px; border-radius: 12px;
  background: var(--bg); color: var(--muted); font-weight: 600; font-size: 14px;
}
</style>
