<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({ open: Boolean })
const emit = defineEmits(['close'])
const router = useRouter()

const actions = [
  { icon: '👤', label: 'Add person', to: { name: 'people', query: { add: 1 } } },
  { icon: '🛒', label: 'Add errand', to: { name: 'errand-new' } },
  { icon: '📍', label: 'Check in nearby', to: { name: 'nearby' } },
]

function go(to) {
  emit('close')
  router.push(to)
}
</script>

<template>
  <transition name="sheet">
    <div v-if="props.open" class="backdrop" @click.self="emit('close')">
      <div class="sheet">
        <div class="grabber"></div>
        <h3 class="title">Quick add</h3>
        <button v-for="a in actions" :key="a.label" class="row" @click="go(a.to)">
          <span class="ic">{{ a.icon }}</span>
          <span>{{ a.label }}</span>
          <span class="chev">›</span>
        </button>
      </div>
    </div>
  </transition>
</template>

<style scoped>
.backdrop {
  position: absolute;
  inset: 0;
  background: rgba(20, 16, 40, 0.35);
  display: flex;
  align-items: flex-end;
  z-index: 50;
}
.sheet {
  width: 100%;
  background: #fff;
  border-radius: 24px 24px 0 0;
  padding: 10px 18px calc(90px);
  box-shadow: var(--shadow-lg);
}
.grabber {
  width: 40px;
  height: 4px;
  border-radius: 999px;
  background: var(--border);
  margin: 4px auto 10px;
}
.title { margin: 6px 4px 12px; }
.row {
  display: flex;
  align-items: center;
  gap: 14px;
  width: 100%;
  padding: 15px 8px;
  font-size: 16px;
  font-weight: 600;
  color: var(--text);
  border-bottom: 1px solid var(--border);
}
.row:last-child { border-bottom: none; }
.ic {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  background: var(--primary-050);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}
.chev { margin-left: auto; color: var(--muted); font-size: 22px; }

.sheet-enter-active, .sheet-leave-active { transition: opacity 0.2s ease; }
.sheet-enter-active .sheet, .sheet-leave-active .sheet { transition: transform 0.25s ease; }
.sheet-enter-from, .sheet-leave-to { opacity: 0; }
.sheet-enter-from .sheet, .sheet-leave-to .sheet { transform: translateY(100%); }
</style>
