<script setup>
import { ref } from 'vue'
import { usePeopleStore } from '@/stores/people'

const emit = defineEmits(['close', 'created'])
const store = usePeopleStore()

const form = ref({
  name: '',
  relationship_type: 'friend',
  priority: 'medium',
  reminder_interval_days: 30,
  email: '',
  birthday: '',
  tags: '',
  location_label: '',
})
const busy = ref(false)

async function save() {
  if (!form.value.name.trim()) return
  busy.value = true
  try {
    const payload = { ...form.value }
    if (!payload.birthday) delete payload.birthday
    const created = await store.create(payload)
    emit('created', created)
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="backdrop" @click.self="emit('close')">
    <div class="sheet">
      <div class="grabber"></div>
      <h2>Add person</h2>

      <div class="field">
        <label class="label">Name</label>
        <input v-model="form.name" class="input" placeholder="Full name" />
      </div>
      <div class="two">
        <div class="field">
          <label class="label">Relationship</label>
          <select v-model="form.relationship_type" class="select">
            <option>family</option><option>friend</option><option>partner</option>
            <option>work</option><option>mentor</option><option>networking</option>
          </select>
        </div>
        <div class="field">
          <label class="label">Priority</label>
          <select v-model="form.priority" class="select">
            <option value="very_high">Very high</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>
      </div>
      <div class="two">
        <div class="field">
          <label class="label">Remind every (days)</label>
          <input v-model.number="form.reminder_interval_days" type="number" min="1" class="input" />
        </div>
        <div class="field">
          <label class="label">Birthday</label>
          <input v-model="form.birthday" type="date" class="input" />
        </div>
      </div>
      <div class="field">
        <label class="label">Based in (optional)</label>
        <input v-model="form.location_label" class="input" placeholder="e.g. Bangalore" />
      </div>
      <div class="field">
        <label class="label">Tags</label>
        <input v-model="form.tags" class="input" placeholder="coffee, college, mentor" />
      </div>

      <div class="row-btn">
        <button class="btn outline" @click="emit('close')">Cancel</button>
        <button class="btn" :disabled="busy" @click="save">{{ busy ? 'Saving…' : 'Save' }}</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.backdrop {
  position: absolute; inset: 0; z-index: 60;
  background: rgba(20, 16, 40, 0.4);
  display: flex; align-items: flex-end;
}
.sheet {
  width: 100%;
  max-height: 92%;
  overflow-y: auto;
  background: #fff;
  border-radius: 24px 24px 0 0;
  padding: 10px 18px 30px;
}
.grabber { width: 40px; height: 4px; border-radius: 999px; background: var(--border); margin: 4px auto 12px; }
h2 { margin-bottom: 16px; }
.two { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.row-btn { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 6px; }
</style>
