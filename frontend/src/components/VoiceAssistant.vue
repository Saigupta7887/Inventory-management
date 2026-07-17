<script setup>
import { onUnmounted, ref } from 'vue'
import { runCommand } from '@/lib/assistant'

const SR = window.SpeechRecognition || window.webkitSpeechRecognition
const supported = !!SR

const open = ref(false)
const listening = ref(false)
const thinking = ref(false)
const transcript = ref('')
const reply = ref('')
const typed = ref('')
const always = ref(false)
let recog = null

function speak(text) {
  try {
    if (!window.speechSynthesis) return
    window.speechSynthesis.cancel()
    const u = new SpeechSynthesisUtterance(text)
    u.rate = 1.02
    u.pitch = 1.05
    window.speechSynthesis.speak(u)
  } catch { /* ignore */ }
}

async function handle(text) {
  if (!text || !text.trim()) return
  transcript.value = text
  thinking.value = true
  reply.value = ''
  try {
    const res = await runCommand(text)
    reply.value = res.say
    speak(res.say)
  } catch (e) {
    reply.value = 'Something went wrong doing that.'
  } finally {
    thinking.value = false
  }
}

function makeRecognizer() {
  const r = new SR()
  r.lang = 'en-US'
  r.interimResults = true
  r.continuous = always.value
  r.onresult = (ev) => {
    let text = ''
    for (let i = ev.resultIndex; i < ev.results.length; i++) text += ev.results[i][0].transcript
    transcript.value = text
    const isFinal = ev.results[ev.results.length - 1].isFinal
    if (!isFinal) return
    if (always.value) {
      // Wake-word gate: only act if they said "bondly".
      if (/\bbondly\b/i.test(text)) handle(text)
    } else {
      handle(text)
    }
  }
  r.onend = () => {
    listening.value = false
    if (always.value) start() // keep the wake word alive
  }
  r.onerror = (e) => {
    if (e.error === 'not-allowed') reply.value = 'Microphone access was blocked.'
    listening.value = false
  }
  return r
}

function start() {
  if (!supported) return
  try {
    recog = makeRecognizer()
    recog.start()
    listening.value = true
    reply.value = ''
    transcript.value = ''
  } catch { /* already started */ }
}

function stop() {
  always.value = false
  if (recog) { try { recog.stop() } catch { /* ignore */ } }
  listening.value = false
}

function toggleAlways() {
  always.value = !always.value
  if (always.value) start()
  else stop()
}

function submitTyped() {
  if (!typed.value.trim()) return
  handle(typed.value)
  typed.value = ''
}

onUnmounted(() => stop())
</script>

<template>
  <div class="assistant">
    <transition name="pop">
      <div v-if="open" class="panel">
        <div class="head">
          <span class="title">🎙️ Hey Bondly</span>
          <button class="x" @click="open = false">✕</button>
        </div>

        <div class="body">
          <p v-if="!transcript && !reply" class="muted hint">
            Tap the mic and say something like<br />
            <em>“note that Sarah loves matcha”</em>,
            <em>“log a call with Nikhil”</em>, or
            <em>“who should I reconnect with?”</em>
          </p>
          <p v-if="transcript" class="you">“{{ transcript }}”</p>
          <p v-if="thinking" class="muted">…</p>
          <p v-if="reply" class="bondly">{{ reply }}</p>
        </div>

        <div v-if="supported" class="controls">
          <button class="mic" :class="{ live: listening }" @click="listening ? stop() : start()">
            {{ listening ? '● Listening…' : '🎤 Tap to talk' }}
          </button>
          <label class="wake">
            <input type="checkbox" :checked="always" @change="toggleAlways" />
            Always listen for “Bondly”
          </label>
        </div>
        <p v-else class="muted small">Voice isn't supported in this browser — type a command below.</p>

        <form class="typed" @submit.prevent="submitTyped">
          <input v-model="typed" class="input" placeholder="…or type a command" />
          <button class="go" type="submit">➤</button>
        </form>
      </div>
    </transition>

    <button class="fab-mic" :class="{ live: listening }" @click="open = !open" aria-label="Hey Bondly">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="9" y="3" width="6" height="11" rx="3" /><path d="M5 11a7 7 0 0 0 14 0M12 18v3" />
      </svg>
    </button>
  </div>
</template>

<style scoped>
.fab-mic {
  position: absolute;
  right: 18px;
  bottom: 90px;
  width: 54px;
  height: 54px;
  border-radius: 50%;
  background: var(--grad);
  box-shadow: 0 8px 22px rgba(124, 77, 255, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 40;
}
.fab-mic.live { animation: pulse 1.2s infinite; }
@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(124, 77, 255, 0.5); }
  100% { box-shadow: 0 0 0 16px rgba(124, 77, 255, 0); }
}
.panel {
  position: absolute;
  right: 18px;
  bottom: 156px;
  width: min(340px, calc(100% - 36px));
  background: #fff;
  border: 1px solid var(--border);
  border-radius: 20px;
  box-shadow: var(--shadow-lg);
  padding: 16px;
  z-index: 41;
}
.head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
.title { font-weight: 800; }
.x { color: var(--muted); font-size: 15px; }
.body { min-height: 60px; margin-bottom: 12px; }
.hint { font-size: 13px; line-height: 1.6; }
.hint em { color: var(--primary); font-style: normal; }
.you { font-weight: 600; margin-bottom: 8px; }
.bondly {
  background: var(--grad-soft);
  border: 1px solid var(--primary-100);
  border-radius: 12px;
  padding: 10px 12px;
  font-weight: 600;
}
.controls { display: flex; flex-direction: column; gap: 10px; margin-bottom: 12px; }
.mic {
  width: 100%;
  padding: 12px;
  border-radius: 14px;
  background: var(--primary);
  color: #fff;
  font-weight: 700;
}
.mic.live { background: var(--high-fg); }
.wake { display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--muted); }
.typed { display: flex; gap: 8px; }
.typed .input { flex: 1; padding: 11px 12px; }
.go {
  width: 46px; border-radius: 12px; background: var(--primary-050); color: var(--primary); font-size: 16px;
}
.small { font-size: 12px; }

.pop-enter-active, .pop-leave-active { transition: opacity 0.15s ease, transform 0.15s ease; }
.pop-enter-from, .pop-leave-to { opacity: 0; transform: translateY(8px) scale(0.98); }

@media (min-width: 900px) {
  .fab-mic { bottom: 28px; right: 28px; }
  .panel { bottom: 94px; right: 28px; }
}
</style>
