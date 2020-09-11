import Vue from 'vue'
import Vuex from 'vuex'
import axios, { AxiosResponse } from 'axios'
import { ApiInfoRequest, ApiInfoResponse } from '@/utils/api'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    checked_log_in: false,
    logged_in: false,
    username: ''
  },
  mutations: {
    checked_log_in(state) {
      state.checked_log_in = true
    },
    log_in(state, username) {
      state.logged_in = true
      state.username = username
    },
    log_out(state) {
      state.logged_in = false
      state.username = ''
    }
  },
  actions: {
    async check_log_in({ commit, dispatch }, force = false) {
      if (!this.state.checked_log_in || force) {
        try {
          const response = await axios.get<ApiInfoRequest, AxiosResponse<ApiInfoResponse>>('/api/info')
          if (response.status >= 200 && response.status < 300 && !('error' in response.data)) {
            commit('log_in', response.data.username)
          } else {
            dispatch('log_out')
          }
        } catch (err) {
          dispatch('log_out')
        }
        commit('checked_log_in')
      }
      return this.state.logged_in
    },
    async log_out({ commit }) {
      if (this.state.logged_in) {
        await axios.get('/api/logout')
      }
      commit('log_out')
    }
  },
  modules: {
  },
  strict: process.env.NODE_ENV !== 'production'
})
