<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useLocationStore } from '@/stores/location'
import Avatar from '@/components/Avatar.vue'

const store = useLocationStore()
const router = useRouter()

const types = ref([])
const activeType = ref(null)
const gps = ref(null) // nearby() result
const checkin = ref(null) // check-in result
const status = ref('') // GPS status message
const busy = ref(false)
const lastCoords = ref(null) // {lat, lng} from last GPS fix
const savingSpot = ref(false)
const spot = ref({ name: '', place_type: 'grocery' })

const typeMeta = {
  grocery: { icon: '🛒', label: 'Grocery' },
  pharmacy: { icon: '💊', label: 'Pharmacy' },
  cafe: { icon: '☕', label: 'Cafe' },
  restaurant: { icon: '🍽️', label: 'Restaurant' },
  gym: { icon: '🏋️', label: 'Gym' },
  bookstore: { icon: '📚', label: 'Bookstore' },
  other: { icon: '📍', label: 'Other' },
}

onMounted(async () => {
  types.value = await store.placeTypes()
})

function useLocation() {
  if (!navigator.geolocation) {
    status.value = 'Location is not available in this browser.'
    return
  }
  status.value = 'Finding places near you…'
  busy.value = true
  navigator.geolocation.getCurrentPosition(
    async (pos) => {
      try {
        lastCoords.value = { lat: pos.coords.latitude, lng: pos.coords.longitude }
        gps.value = await store.nearby(pos.coords.latitude, pos.coords.longitude, 5)
        checkin.value = null
        activeType.value = null
        status.value = ''
      } finally {
        busy.value = false
      }
    },
    () => {
      status.value = 'Couldn’t get your location. Try a manual check-in below.'
      busy.value = false
    },
    { timeout: 8000 },
  )
}

async function checkInType(t) {
  activeType.value = t
  gps.value = null
  checkin.value = await store.checkIn(t)
}

async function complete(id) {
  await store.completeErrand(id)
  // Refresh whichever view is active.
  if (activeType.value) await checkInType(activeType.value)
  else if (lastCoords.value) gps.value = await store.nearby(lastCoords.value.lat, lastCoords.value.lng, 5)
}

async function saveSpot() {
  if (!spot.value.name.trim() || !lastCoords.value) return
  await store.createPlace({
    name: spot.value.name,
    place_type: spot.value.place_type,
    latitude: lastCoords.value.lat,
    longitude: lastCoords.value.lng,
  })
  spot.value.name = ''
  savingSpot.value = false
  gps.value = await store.nearby(lastCoords.value.lat, lastCoords.value.lng, 5)
}
</script>

<template>
  <div>
    <header class="bar">
      <button class="icon-btn" @click="router.back()">←</button>
      <h1>Nearby</h1>
      <RouterLink :to="{ name: 'errand-new' }" class="icon-btn add">+</RouterLink>
    </header>

    <button class="btn grad gps" :disabled="busy" @click="useLocation">
      📍 {{ busy ? 'Locating…' : 'Use my location' }}
    </button>
    <p v-if="status" class="muted status">{{ status }}</p>

    <p class="q">Or check in manually</p>
    <div class="chips">
      <button
        v-for="t in types"
        :key="t"
        class="chip"
        :class="{ active: activeType === t }"
        @click="checkInType(t)"
      >
        {{ (typeMeta[t] || {}).icon }} {{ (typeMeta[t] || {}).label || t }}
      </button>
    </div>

    <!-- Manual check-in result -->
    <template v-if="checkin">
      <h3 class="section">
        {{ (typeMeta[checkin.place_type] || {}).icon }} At a {{ checkin.place_type }}
      </h3>
      <p v-if="!checkin.errands.length" class="muted empty">No errands saved for here yet.</p>
      <div v-for="e in checkin.errands" :key="e.id" class="card errand">
        <div class="grow">
          <strong>{{ e.title }}</strong>
          <div v-if="e.person_name" class="muted small">for {{ e.person_name }}</div>
          <div v-if="e.note" class="muted small">{{ e.note }}</div>
        </div>
        <button class="done" @click="complete(e.id)">✓</button>
      </div>
      <div v-if="checkin.saved_places.length" class="places">
        <span class="muted small">Saved {{ checkin.place_type }} spots: </span>
        <span v-for="p in checkin.saved_places" :key="p.id" class="placechip">{{ p.name }}</span>
      </div>
    </template>

    <!-- GPS result -->
    <template v-if="gps">
      <div class="savespot">
        <button v-if="!savingSpot" class="btn soft sm" @click="savingSpot = true">
          ＋ Save this spot as a place
        </button>
        <div v-else class="spotform card">
          <input v-model="spot.name" class="input" placeholder="Place name (e.g. Corner Market)" />
          <select v-model="spot.place_type" class="select">
            <option v-for="t in types" :key="t" :value="t">{{ t }}</option>
          </select>
          <div class="spotbtns">
            <button class="btn outline sm" @click="savingSpot = false">Cancel</button>
            <button class="btn sm" @click="saveSpot">Save spot</button>
          </div>
        </div>
      </div>

      <h3 class="section">📍 Places near you</h3>
      <p v-if="!gps.nearby_places.length" class="muted empty">No saved places within 5 km.</p>
      <div v-for="np in gps.nearby_places" :key="np.place.id" class="card">
        <div class="placehead">
          <strong>{{ (typeMeta[np.place.place_type] || {}).icon }} {{ np.place.name }}</strong>
          <span class="muted small">{{ np.distance_km }} km</span>
        </div>
        <div v-for="e in np.errands" :key="e.id" class="errand inner">
          <div class="grow">
            <strong>{{ e.title }}</strong>
            <span v-if="e.person_name" class="muted small"> · for {{ e.person_name }}</span>
          </div>
          <button class="done" @click="complete(e.id)">✓</button>
        </div>
        <p v-if="!np.errands.length" class="muted small">No errands for this type.</p>
      </div>

      <h3 class="section">👥 People near you</h3>
      <p v-if="!gps.nearby_people.length" class="muted empty">No contacts based nearby.</p>
      <RouterLink
        v-for="p in gps.nearby_people"
        :key="p.person_id"
        :to="{ name: 'person', params: { id: p.person_id } }"
        class="row"
      >
        <Avatar :name="p.name" :size="44" />
        <div class="grow">
          <strong>{{ p.name }}</strong>
          <div class="muted small">{{ p.location_label || 'Nearby' }}</div>
        </div>
        <span class="muted small">{{ p.distance_km }} km</span>
      </RouterLink>
    </template>

    <div v-if="!gps && !checkin" class="hint card">
      <p class="muted">
        Save an errand for someone (like “matcha for Sarah” at a grocery store).
        When you’re near that kind of place — by GPS or a manual check-in — Bondly
        reminds you, and shows contacts based nearby.
      </p>
    </div>
  </div>
</template>

<style scoped>
.bar { display: flex; align-items: center; gap: 12px; padding: 6px 0 12px; }
.bar h1 { flex: 1; }
.icon-btn { width: 38px; height: 38px; border-radius: 12px; background: var(--bg); font-size: 20px; color: var(--text); display: flex; align-items: center; justify-content: center; }
.icon-btn.add { background: var(--primary-050); color: var(--primary); font-size: 22px; }
.gps { margin-bottom: 8px; }
.status { text-align: center; font-size: 13px; margin-bottom: 8px; }
.q { font-weight: 700; margin: 18px 0 10px; }
.section { margin: 22px 2px 12px; }
.empty { padding: 8px 2px; }
.errand { display: flex; align-items: center; gap: 12px; margin-bottom: 10px; }
.errand.inner { margin-top: 10px; padding: 10px 0 0; border-top: 1px solid var(--border); }
.errand .grow { flex: 1; }
.small { font-size: 13px; }
.done {
  width: 38px; height: 38px; border-radius: 12px;
  background: var(--low-bg); color: var(--low-fg); font-size: 16px; font-weight: 700; flex-shrink: 0;
}
.placehead { display: flex; justify-content: space-between; align-items: center; }
.places { margin-top: 10px; display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
.placechip { background: var(--primary-050); color: var(--primary); font-size: 12px; font-weight: 600; padding: 3px 10px; border-radius: 999px; }
.row { display: flex; align-items: center; gap: 12px; padding: 12px 2px; border-bottom: 1px solid var(--border); }
.row .grow { flex: 1; }
.hint { margin-top: 20px; background: var(--grad-soft); border-color: var(--primary-100); }
.savespot { margin-top: 14px; }
.spotform { display: grid; gap: 10px; }
.spotform .select { text-transform: capitalize; }
.spotbtns { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
</style>
