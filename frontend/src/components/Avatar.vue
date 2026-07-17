<script setup>
import { computed } from 'vue'

const props = defineProps({
  name: { type: String, default: '?' },
  size: { type: Number, default: 44 },
})

const initials = computed(() => {
  const parts = props.name.trim().split(/\s+/)
  return (parts[0]?.[0] || '?').toUpperCase() + (parts[1]?.[0]?.toUpperCase() || '')
})

// Deterministic warm gradient per name.
const bg = computed(() => {
  let h = 0
  for (const c of props.name) h = (h * 31 + c.charCodeAt(0)) % 360
  return `linear-gradient(135deg, hsl(${h} 70% 62%), hsl(${(h + 40) % 360} 75% 55%))`
})
</script>

<template>
  <span
    class="avatar"
    :style="{
      width: size + 'px',
      height: size + 'px',
      background: bg,
      color: '#fff',
      fontSize: size * 0.38 + 'px',
    }"
    >{{ initials }}</span
  >
</template>
