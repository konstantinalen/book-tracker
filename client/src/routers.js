import { createRouter, createWebHistory } from 'vue-router'

import Events from './components/Events.vue'
import Books from './components/Books.vue'

const routes = [
  { path: '/', redirect: '/events' }, 
  { path: '/events', component: Events },
  { path: '/books', component: Books }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router