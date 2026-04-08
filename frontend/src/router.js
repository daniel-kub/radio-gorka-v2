import { createRouter, createWebHistory } from 'vue-router'
import Home from './page/Home.vue'
import AdminPanel from './page/AdminPanel.vue'
import NotFound from './page/404.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/admin-panel', component: AdminPanel },
  { path: '/:pathMatch(.*)*', name: 'NotFound', component: NotFound }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router