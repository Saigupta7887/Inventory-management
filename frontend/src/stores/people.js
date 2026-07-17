import { defineStore } from 'pinia'
import client from '@/api/client'

export const usePeopleStore = defineStore('people', {
  state: () => ({
    people: [],
    loading: false,
  }),
  actions: {
    async fetchAll() {
      this.loading = true
      try {
        const { data } = await client.get('/api/people')
        this.people = data
      } finally {
        this.loading = false
      }
    },
    async get(id) {
      const { data } = await client.get(`/api/people/${id}`)
      return data
    },
    async create(person) {
      const { data } = await client.post('/api/people', person)
      this.people.push(data)
      return data
    },
    async update(id, patch) {
      const { data } = await client.patch(`/api/people/${id}`, patch)
      const idx = this.people.findIndex((p) => p.id === id)
      if (idx !== -1) this.people[idx] = data
      return data
    },
    async remove(id) {
      await client.delete(`/api/people/${id}`)
      this.people = this.people.filter((p) => p.id !== id)
    },
    async notes(id) {
      const { data } = await client.get(`/api/people/${id}/notes`)
      return data
    },
    async addNote(id, note) {
      const { data } = await client.post(`/api/people/${id}/notes`, note)
      return data
    },
    async interactions(id) {
      const { data } = await client.get(`/api/people/${id}/interactions`)
      return data
    },
    async logInteraction(id, interaction) {
      const { data } = await client.post(
        `/api/people/${id}/interactions`,
        interaction,
      )
      return data
    },
    async contextCard(id) {
      const { data } = await client.get(`/api/people/${id}/context-card`)
      return data
    },
  },
})
