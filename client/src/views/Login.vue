<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card class="elevation-12">
          <v-toolbar color="primary" dark flat>
            <v-toolbar-title>Login</v-toolbar-title>
          </v-toolbar>
          <v-progress-linear v-if="loading" absolute indeterminate />
          <v-form @submit.prevent="requestLogin">
            <v-card-text>
              <v-alert v-if="displayError" type="error">
                {{ errorMessage }}
              </v-alert>
              <v-text-field
                v-model="username"
                label="Username"
                name="username"
                prepend-icon="mdi-account"
                type="text"
                :disabled="loading"
              />
              <v-text-field
                v-model="password"
                id="password"
                label="Password"
                name="password"
                prepend-icon="mdi-lock"
                type="password"
                :disabled="loading"
              />
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn color="primary" type="submit" :disabled="loading"
                >Login</v-btn
              >
            </v-card-actions>
          </v-form>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import axios, { AxiosResponse } from 'axios'
import { Component, Vue } from 'vue-property-decorator'
import { ApiLoginRequest, ApiLoginResponse } from '@/utils/api'

@Component
export default class Login extends Vue {
  username = '';
  password = '';
  displayError = false;
  errorMessage = '';
  loading = false;

  async mounted(): Promise<void> {
    this.loading = true
    if (await this.$store.dispatch('check_log_in', true)) {
      this.$router.push({ path: '/' })
    }
    this.loading = false
  }

  async requestLogin(): Promise<void> {
    this.loading = true
    const response = await axios.post<ApiLoginRequest, AxiosResponse<ApiLoginResponse>>('/api/login', {
      username: this.username,
      password: this.password
    })
    if (response.status >= 200 && response.status < 300) {
      if ('error' in response.data && response.data.error) {
        this.displayError = true
        this.errorMessage = response.data.error_message
      } else if ('success' in response.data && response.data.success) {
        this.$store.commit('log_in', this.username)
        this.$router.push({ path: response.data.next })
      }
    }
    this.password = ''
    this.loading = false
  }
}
</script>
