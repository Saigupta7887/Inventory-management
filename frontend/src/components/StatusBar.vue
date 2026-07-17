<script setup>
import { onMounted, onUnmounted, ref } from 'vue'

const time = ref('')
let timer

function tick() {
  const d = new Date()
  time.value = d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
  tick()
  timer = setInterval(tick, 30_000)
})
onUnmounted(() => clearInterval(timer))
</script>

<template>
  <div class="statusbar">
    <span class="time">{{ time }}</span>
    <span class="icons">
      <svg width="18" height="11" viewBox="0 0 18 11" fill="currentColor"><rect x="0" y="7" width="3" height="4" rx="1"/><rect x="5" y="5" width="3" height="6" rx="1"/><rect x="10" y="2.5" width="3" height="8.5" rx="1"/><rect x="15" y="0" width="3" height="11" rx="1"/></svg>
      <svg width="16" height="11" viewBox="0 0 16 12" fill="currentColor"><path d="M8 2.4c2 0 3.9.8 5.3 2.1l1.2-1.2A9.4 9.4 0 0 0 8 .6 9.4 9.4 0 0 0 1.5 3.3l1.2 1.2A7.5 7.5 0 0 1 8 2.4Zm0 3.2c1.1 0 2.2.4 3 1.2l1.2-1.2A6 6 0 0 0 8 3.9a6 6 0 0 0-4.2 1.7L5 6.8a4.3 4.3 0 0 1 3-1.2Zm0 3.1L9.7 10 8 11.7 6.3 10 8 8.7Z"/></svg>
      <svg width="25" height="12" viewBox="0 0 25 12" fill="none"><rect x="1" y="1" width="20" height="10" rx="3" stroke="currentColor" stroke-opacity="0.5"/><rect x="2.5" y="2.5" width="16" height="7" rx="1.5" fill="currentColor"/><rect x="22.5" y="4" width="1.5" height="4" rx="0.75" fill="currentColor" fill-opacity="0.5"/></svg>
    </span>
  </div>
</template>

<style scoped>
.statusbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 22px 4px;
  color: var(--text);
  flex-shrink: 0;
}
.time { font-weight: 700; font-size: 14px; }
.icons { display: flex; align-items: center; gap: 6px; }
</style>
