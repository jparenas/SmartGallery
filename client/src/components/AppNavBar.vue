<template>
  <v-app-bar fixed app elevate-on-scroll>
    <v-toolbar-title>SmartGallery</v-toolbar-title>

    <v-spacer></v-spacer>

    <v-text-field
      id="search"
      label="Search"
      name="Search"
      prepend-inner-icon="mdi-magnify"
      type="text"
      light
      solo
      dense
      hide-details
    />

    <v-spacer></v-spacer>

    <v-menu bottom left offset-y>
      <template v-slot:activator="{ on, attrs }">
        <v-btn tile outlined v-bind="attrs" v-on="on">
          <span>{{ username }}</span>
          <v-icon>mdi-account</v-icon>
        </v-btn>
      </template>

      <v-list>
        <v-list-item @click="logOut" dense class="px-0 text-center">
          <v-list-item>Log Out</v-list-item>
        </v-list-item>
      </v-list>
    </v-menu>
  </v-app-bar>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

@Component
export default class AppNavBar extends Vue {
  async mounted(): Promise<void> {
    if (!(await this.$store.dispatch('check_log_in'))) {
      this.$router.push({ path: '/login' })
    }
  }

  get username(): string {
    return this.$store.state.username
  }

  async logOut(): Promise<void> {
    await this.$store.dispatch('log_out')
    this.$router.push({ path: '/login' })
  }
}
</script>

<style scoped lang="scss">
</style>
