import { createRouter, createWebHistory } from 'vue-router'
import Home from './page/Home.vue'
import EventHome from './page/EventHome.vue'
import AdminPanel from './page/AdminPanel.vue'
import NotFound from './page/404.vue'

const eventMode = import.meta.env.VITE_EVENT_MODE === 'true'

const routes = [
  { path: '/', component: Home },
  ...(eventMode ? [{ path: '/event', component: EventHome }] : []),
  { path: '/admin-panel', component: AdminPanel },
  { path: '/:pathMatch(.*)*', name: 'NotFound', component: NotFound }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router