import { defineStore } from 'pinia'
import client from '@/api/client'

export const useLocationStore = defineStore('location', {
  state: () => ({
    errands: [],
    places: [],
  }),
  actions: {
    async fetchErrands(includeCompleted = false) {
      const { data } = await client.get('/api/errands', {
        params: { include_completed: includeCompleted },
      })
      this.errands = data
      return data
    },
    async createErrand(errand) {
      const { data } = await client.post('/api/errands', errand)
      this.errands.unshift(data)
      return data
    },
    async completeErrand(id) {
      const { data } = await client.patch(`/api/errands/${id}`, { completed: true })
      this.errands = this.errands.filter((e) => e.id !== id)
      return data
    },
    async fetchPlaces() {
      const { data } = await client.get('/api/places')
      this.places = data
      return data
    },
    async createPlace(place) {
      const { data } = await client.post('/api/places', place)
      this.places.push(data)
      return data
    },
    async placeTypes() {
      const { data } = await client.get('/api/nearby/place-types')
      return data
    },
    async nearby(lat, lng, radiusKm = 5) {
      const { data } = await client.get('/api/nearby', {
        params: { lat, lng, radius_km: radiusKm },
      })
      return data
    },
    async checkIn(placeType) {
      const { data } = await client.get('/api/nearby/check-in', {
        params: { place_type: placeType },
      })
      return data
    },
  },
})
