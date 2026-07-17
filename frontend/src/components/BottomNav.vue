<script setup>
defineEmits(['fab'])

const tabs = [
  { name: 'home', label: 'Home', d: 'M3 10.5 12 3l9 7.5M5 9.5V20h5v-6h4v6h5V9.5' },
  { name: 'people', label: 'People', d: 'M16 19c0-2.2-1.8-4-4-4s-4 1.8-4 4M12 11a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z' },
  { name: 'reminders', label: 'Reminders', d: 'M18 8a6 6 0 1 0-12 0c0 7-3 8-3 8h18s-3-1-3-8M13.7 21a2 2 0 0 1-3.4 0' },
  { name: 'insights', label: 'Insights', d: 'M4 20V10M10 20V4M16 20v-7M22 20H2' },
]
</script>

<template>
  <nav class="nav">
    <RouterLink
      v-for="(t, i) in tabs"
      :key="t.name"
      :to="{ name: t.name }"
      class="tab"
      active-class="active"
      :class="{ pushright: i === 2 }"
    >
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path :d="t.d" />
      </svg>
      <span>{{ t.label }}</span>
    </RouterLink>

    <button class="fab" @click="$emit('fab')" aria-label="Quick add">
      <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.5" stroke-linecap="round">
        <path d="M12 5v14M5 12h14" />
      </svg>
    </button>
  </nav>
</template>

<style scoped>
.nav {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 74px;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: saturate(180%) blur(14px);
  border-top: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-around;
  padding: 0 6px;
}
.tab {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
  color: var(--muted);
  font-size: 11px;
  font-weight: 600;
  flex: 1;
}
.tab.active { color: var(--primary); }
.tab.pushright { margin-right: 56px; }
.fab {
  position: absolute;
  left: 50%;
  top: -20px;
  transform: translateX(-50%);
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--grad);
  box-shadow: 0 8px 20px rgba(124, 77, 255, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
}
.fab:active { transform: translateX(-50%) scale(0.96); }
</style>
