<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import StatusBar from '@/components/StatusBar.vue'
import BottomNav from '@/components/BottomNav.vue'
import Sidebar from '@/components/Sidebar.vue'
import ActionSheet from '@/components/ActionSheet.vue'
import VoiceAssistant from '@/components/VoiceAssistant.vue'

const route = useRoute()
const auth = useAuthStore()
const sheetOpen = ref(false)

// Full-bleed views (no chrome): welcome, login, onboarding.
const chrome = computed(
  () => auth.isAuthenticated && !route.meta.public && route.name !== 'onboarding',
)
</script>

<template>
  <div class="app-shell" :class="{ chrome }">
    <Sidebar v-if="chrome" class="desktop-only" @add="sheetOpen = true" />

    <div class="phone">
      <StatusBar v-if="chrome" class="mobile-only" />
      <main class="screen" :class="{ 'has-nav': chrome }">
        <div class="content">
          <RouterView />
        </div>
      </main>
      <BottomNav v-if="chrome" class="mobile-only" @fab="sheetOpen = true" />
      <ActionSheet v-if="chrome" :open="sheetOpen" @close="sheetOpen = false" />
      <VoiceAssistant v-if="chrome" />
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
.screen {
  flex: 1;
  overflow-y: auto;
  padding: 8px 20px 24px;
}
.screen.has-nav { padding-bottom: 96px; }
.content { width: 100%; }

/* ---- Tablet: give the phone a floating frame ---- */
@media (min-width: 460px) and (max-width: 899px) {
  .phone {
    margin: 24px 0;
    min-height: auto;
    height: calc(100dvh - 48px);
    border-radius: 34px;
    box-shadow: var(--shadow-lg);
    border: 1px solid var(--border);
  }
}

/* ---- Desktop: sidebar + fluid content, no phone frame ---- */
@media (min-width: 900px) {
  .app-shell.chrome { justify-content: flex-start; }
  .app-shell.chrome .phone {
    max-width: none;
    flex: 1;
    background: transparent;
    overflow: visible;
  }
  .app-shell.chrome .screen { padding: 32px 40px 48px; }
  .app-shell.chrome .screen.has-nav { padding-bottom: 48px; }
  .app-shell.chrome .content { max-width: 860px; margin: 0 auto; }
  .mobile-only { display: none !important; }
}
@media (max-width: 899px) {
  .desktop-only { display: none !important; }
}
</style>
