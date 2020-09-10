<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card class="elevation-12">
          <v-toolbar color="primary" dark flat>
            <v-toolbar-title>Login</v-toolbar-title>
          </v-toolbar>
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
              ></v-text-field>

              <v-text-field
                v-model="password"
                id="password"
                label="Password"
                name="password"
                prepend-icon="mdi-lock"
                type="password"
              ></v-text-field>
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn color="primary" type="submit">Login</v-btn>
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

  async mounted () {
    try {
      const response = await axios.get('/api/info')
      if (response.status === 200) {
        this.$router.push({ path: '/' })
      }
    } catch (err) {
      // Pass
    }
  }

  async requestLogin () {
    const response = await axios.post<ApiLoginRequest, AxiosResponse<ApiLoginResponse>>('/api/login', {
      username: this.username,
      password: this.password
    })
    if (response.status >= 200 && response.status < 300) {
      if ('error' in response.data && response.data.error) {
        this.displayError = true
        this.errorMessage = response.data.error_message
      } else if ('success' in response.data && response.data.success) {
        this.$router.push({ path: response.data.next })
      }
    }
    this.username = ''
    this.password = ''
  }
}
</script>
