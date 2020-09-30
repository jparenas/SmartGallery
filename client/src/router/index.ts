import Vue from 'vue'
import VueRouter, { RouteConfig } from 'vue-router'

Vue.use(VueRouter)

const routes: Array<RouteConfig> = [
  { path: '/', redirect: '/gallery' },
  {
    path: '/about',
    name: 'About',
    component: () => import(/* webpackChunkName: "about" */ '../views/About.vue')
  },
  {
    path: '/gallery',
    name: 'gallery',
    component: () => import(/* webpackChunkName: "gallery" */ '../views/Gallery.vue')
  },
  {
    path: '/login/:username?',
    name: 'Login',
    component: () => import(/* webpackChunkName: "login" */ '../views/Login.vue'),
    meta: { hideNavigation: true }
  },
  {
    path: '/sign_up',
    name: 'Sign Up',
    component: () => import(/* webpackChunkName: "sign_up" */ '../views/SignUp.vue'),
    meta: { hideNavigation: true }
  },
  {
    path: '/image/:id',
    name: 'ImageViewer',
    component: () => import(/* webpackChunkName: "image_viewer" */ '../views/ImageViewer.vue')
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
