<script setup>
import { useRouter } from 'vue-router'
import BrandMark from '@/components/BrandMark.vue'
import Avatar from '@/components/Avatar.vue'

const router = useRouter()
const floats = ['Aya', 'Ravi', 'Mia', 'Leo', 'Nina']
</script>

<template>
  <div class="welcome">
    <div class="top">
      <BrandMark :size="64" />
      <div class="wordmark">bondly</div>
      <p class="tagline">Remember what<br />matters about people.</p>

      <div class="collage">
        <span
          v-for="(n, i) in floats"
          :key="n"
          class="float"
          :class="'f' + i"
        >
          <Avatar :name="n" :size="i === 2 ? 60 : 46" />
        </span>
        <span class="heart h1">💜</span>
        <span class="heart h2">🧡</span>
      </div>
    </div>

    <div class="actions">
      <button class="btn grad" @click="router.push({ name: 'login', query: { mode: 'register' } })">
        Get Started
      </button>
      <button class="btn outline" @click="router.push({ name: 'login', query: { mode: 'login' } })">
        Sign In
      </button>
      <p class="footer muted">Your relationships. Your story.<br />Always with you.</p>
    </div>
  </div>
</template>

<style scoped>
.welcome {
  min-height: calc(100dvh - 40px);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 4vh 4px 3vh;
  background: radial-gradient(120% 60% at 50% 0%, #f6effe 0%, transparent 70%);
}
.top { text-align: center; }
.wordmark {
  font-size: 44px;
  font-weight: 800;
  letter-spacing: -0.03em;
  margin: 6px 0 14px;
}
.tagline { font-size: 20px; font-weight: 700; line-height: 1.35; }
.collage {
  position: relative;
  height: 210px;
  margin-top: 24px;
}
.float { position: absolute; box-shadow: var(--shadow); border-radius: 50%; }
.float :deep(.avatar) { border: 3px solid #fff; }
.f0 { top: 40px; left: 26%; transform: translateX(-50%); }
.f1 { top: 6px; left: 50%; transform: translateX(-50%); }
.f2 { top: 70px; left: 50%; transform: translateX(-50%); }
.f3 { top: 6px; right: 22%; }
.f4 { top: 96px; left: 16%; }
.heart { position: absolute; font-size: 22px; }
.h1 { top: 30px; right: 20%; }
.h2 { bottom: 20px; right: 30%; }
.actions { display: grid; gap: 12px; padding: 0 4px; }
.footer { text-align: center; font-size: 13px; margin-top: 8px; line-height: 1.5; }
</style>
