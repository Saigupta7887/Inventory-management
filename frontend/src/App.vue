<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import StatusBar from '@/components/StatusBar.vue'
import BottomNav from '@/components/BottomNav.vue'
import ActionSheet from '@/components/ActionSheet.vue'

const route = useRoute()
const auth = useAuthStore()
const sheetOpen = ref(false)

// Full-bleed views (no chrome): welcome, login, onboarding.
const chrome = computed(
  () => auth.isAuthenticated && !route.meta.public && route.name !== 'onboarding',
)
</script>

<template>
  <div class="app-shell">
    <div class="phone">
      <StatusBar />
      <main class="screen" :class="{ 'has-nav': chrome }">
        <RouterView />
      </main>
      <BottomNav v-if="chrome" @fab="sheetOpen = true" />
      <ActionSheet v-if="chrome" :open="sheetOpen" @close="sheetOpen = false" />
    </div>
  </div>
</template>

<style scoped>
.app-shell {
  min-height: 100dvh;
  display: flex;
  justify-content: center;
  background:
    radial-gradient(1200px 600px at 50% -10%, #efe9ff 0%, transparent 60%),
    var(--bg);
}
.phone {
  position: relative;
  width: 100%;
  max-width: 430px;
  min-height: 100dvh;
  background: var(--surface);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
@media (min-width: 460px) {
  .phone {
    margin: 24px 0;
    min-height: auto;
    height: calc(100dvh - 48px);
    border-radius: 34px;
    box-shadow: var(--shadow-lg);
    border: 1px solid var(--border);
  }
}
.screen {
  flex: 1;
  overflow-y: auto;
  padding: 8px 20px 24px;
}
.screen.has-nav {
  padding-bottom: 96px;
}
</style>
