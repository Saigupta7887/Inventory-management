import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/welcome', name: 'welcome', component: () => import('@/views/Welcome.vue'), meta: { public: true } },
  { path: '/login', name: 'login', component: () => import('@/views/Login.vue'), meta: { public: true } },
  { path: '/onboarding', name: 'onboarding', component: () => import('@/views/Onboarding.vue') },
  { path: '/', name: 'home', component: () => import('@/views/Home.vue') },
  { path: '/people', name: 'people', component: () => import('@/views/People.vue') },
  { path: '/people/:id', name: 'person', component: () => import('@/views/PersonProfile.vue'), props: true },
  { path: '/people/:id/note', name: 'add-note', component: () => import('@/views/AddNote.vue'), props: true },
  { path: '/people/:id/log', name: 'log-interaction', component: () => import('@/views/LogInteraction.vue'), props: true },
  { path: '/reminders', name: 'reminders', component: () => import('@/views/Reminders.vue') },
  { path: '/insights', name: 'insights', component: () => import('@/views/Insights.vue') },
  { path: '/settings', name: 'settings', component: () => import('@/views/Settings.vue') },
  { path: '/nearby', name: 'nearby', component: () => import('@/views/Nearby.vue') },
  { path: '/errands/new', name: 'errand-new', component: () => import('@/views/ErrandNew.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (!to.meta.public && !auth.isAuthenticated) {
    return { name: 'welcome' }
  }
  if (to.meta.public && auth.isAuthenticated) {
    return { name: 'home' }
  }
  return true
})

export default router
