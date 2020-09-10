import Vue from 'vue'
import App from './App.vue'
import router from './router'
import vuetify from './plugins/vuetify'
import axios from 'axios'
import 'roboto-fontface/css/roboto/roboto-fontface.css'
import '@mdi/font/css/materialdesignicons.css'

Vue.config.productionTip = false

axios.defaults.baseURL = process.env.VUE_APP_API_ENDPOINT
axios.defaults.withCredentials = true

new Vue({
  router,
  vuetify,
  render: h => h(App)
}).$mount('#app')
