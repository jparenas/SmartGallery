<template>
  <v-app id="app" class="d-flex flex-column">
    <AppNavBar v-if="showNavigation" />
    <v-main>
      <div class="d-flex fill-height">
        <router-view class="flex-grow-1" />
      </div>
    </v-main>
  </v-app>
</template>

<script lang="ts">
import AppNavBar from '@/components/AppNavBar.vue'
import { Component, Vue } from 'vue-property-decorator'

@Component({
  components: {
    AppNavBar
  }
})
export default class App extends Vue {
  async mounted(): Promise<void> {
    // if (!this.$router.currentRoute.path.startsWith('/login') && !(await this.$store.dispatch('check_log_in'))) {
    //   this.$router.push({ path: '/login' })
    // }
  }

  get showNavigation(): boolean {
    return !(this.$route.meta.hideNavigation === true)
  }
}
</script>

<style lang="scss">
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

#nav {
  padding: 30px;

  a {
    font-weight: bold;
    color: #2c3e50;

    &.router-link-exact-active {
      color: #42b983;
    }
  }
}
</style>
