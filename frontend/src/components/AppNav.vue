<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const links = [
  { name: 'dashboard', label: 'Dashboard', icon: '🏠' },
  { name: 'people', label: 'People', icon: '👥' },
  { name: 'reminders', label: 'Reminders', icon: '🔔' },
  { name: 'insights', label: 'Insights', icon: '📈' },
  { name: 'settings', label: 'Settings', icon: '⚙️' },
]

function logout() {
  auth.logout()
  router.push({ name: 'welcome' })
}
</script>

<template>
  <header class="nav">
    <div class="nav-inner">
      <RouterLink :to="{ name: 'dashboard' }" class="brand">🤝 Bondly</RouterLink>
      <nav class="links">
        <RouterLink
          v-for="l in links"
          :key="l.name"
          :to="{ name: l.name }"
          class="link"
          active-class="active"
        >
          <span class="icon">{{ l.icon }}</span>
          <span class="text">{{ l.label }}</span>
        </RouterLink>
      </nav>
      <button class="btn ghost" @click="logout">Log out</button>
    </div>
  </header>
</template>

<style scoped>
.nav {
  position: sticky;
  top: 0;
  z-index: 10;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: saturate(180%) blur(12px);
  border-bottom: 1px solid var(--border);
}
.nav-inner {
  max-width: 1040px;
  margin: 0 auto;
  padding: 12px 20px;
  display: flex;
  align-items: center;
  gap: 18px;
}
.brand {
  font-weight: 800;
  font-size: 18px;
}
.links {
  display: flex;
  gap: 4px;
  margin-left: auto;
}
.link {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 8px 12px;
  border-radius: 10px;
  color: var(--muted);
  font-size: 14px;
  font-weight: 600;
}
.link:hover {
  background: var(--primary-soft);
  color: var(--primary-dark);
}
.link.active {
  background: var(--primary-soft);
  color: var(--primary-dark);
}
@media (max-width: 720px) {
  .link .text {
    display: none;
  }
}
</style>
