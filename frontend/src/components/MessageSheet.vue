<script setup>
import { ref } from 'vue'
import { usePeopleStore } from '@/stores/people'
import { channelsFor, linkFor } from '@/lib/contactActions'

const props = defineProps({
  person: { type: Object, required: true },
  draft: { type: String, default: '' },
})
const emit = defineEmits(['close', 'logged'])
const store = usePeopleStore()

const text = ref(props.draft)
const channels = channelsFor(props.person)
const opened = ref(null)
const logging = ref(false)

function open(channel) {
  const url = linkFor(channel, props.person, text.value)
  // Opens WhatsApp / Messages / Mail / dialer with the draft pre-filled.
  window.open(url, '_blank')
  opened.value = channel
}

async function logIt() {
  logging.value = true
  const map = { whatsapp: 'text', sms: 'text', call: 'call', email: 'email' }
  try {
    await store.logInteraction(props.person.id, {
      channel: map[opened.value] || 'other',
      summary: text.value ? text.value.slice(0, 120) : null,
      mood: 'positive',
    })
    emit('logged')
    emit('close')
  } finally {
    logging.value = false
  }
}
</script>

<template>
  <div class="backdrop" @click.self="emit('close')">
    <div class="sheet">
      <div class="grabber"></div>
      <h2>Message {{ person.name.split(' ')[0] }}</h2>

      <template v-if="channels.length">
        <label class="label">Your message</label>
        <textarea v-model="text" class="textarea" rows="3"></textarea>
        <p class="muted tip">✨ AI-drafted — edit it, then pick how to send.</p>

        <div class="channels">
          <button
            v-for="c in channels"
            :key="c.key"
            class="ch"
            :class="{ active: opened === c.key }"
            @click="open(c.key)"
          >
            <span class="ic">{{ c.icon }}</span>{{ c.label }}
          </button>
        </div>

        <div v-if="opened" class="logged">
          <p class="muted">Opened {{ opened === 'call' ? 'the dialer' : opened }} for you. Reached them?</p>
          <button class="btn" :disabled="logging" @click="logIt">
            {{ logging ? 'Logging…' : '✓ Log this interaction' }}
          </button>
        </div>
      </template>

      <div v-else class="empty">
        <p class="muted">
          Add a phone number or email for {{ person.name.split(' ')[0] }} to message them here.
        </p>
        <button class="btn outline" @click="emit('close')">Close</button>
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
  width: 100%; background: #fff;
  border-radius: 24px 24px 0 0; padding: 10px 18px 30px;
  max-height: 92%; overflow-y: auto;
}
.grabber { width: 40px; height: 4px; border-radius: 999px; background: var(--border); margin: 4px auto 12px; }
h2 { margin-bottom: 14px; }
.tip { font-size: 12px; margin: 6px 0 16px; }
.channels { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
.ch {
  display: flex; align-items: center; justify-content: center; gap: 8px;
  padding: 14px; border: 1.5px solid var(--border); border-radius: 14px;
  background: #fff; font-weight: 700; color: var(--text);
}
.ch.active { border-color: var(--primary); background: var(--primary-050); color: var(--primary); }
.ch .ic { font-size: 18px; }
.logged { margin-top: 18px; display: grid; gap: 10px; }
.empty { display: grid; gap: 14px; padding: 10px 0; }
</style>
