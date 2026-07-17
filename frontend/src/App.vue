<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AppNav from '@/components/AppNav.vue'

const route = useRoute()
const auth = useAuthStore()

// Hide the chrome on public/full-screen views.
const showNav = computed(
  () => auth.isAuthenticated && !route.meta.public && route.name !== 'onboarding',
)
</script>

<template>
  <div class="app-shell">
    <AppNav v-if="showNav" />
    <main :class="{ 'with-nav': showNav }">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.app-shell {
  min-height: 100vh;
}
main {
  max-width: 1040px;
  margin: 0 auto;
  padding: 28px 20px 60px;
}
main.with-nav {
  padding-top: 20px;
}
</style>
