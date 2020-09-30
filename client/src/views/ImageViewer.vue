<template>
  <v-container fluid fill-height class="pa-0">
    <v-row justify="center">
      <v-col cols="auto" class="mx-2">
        <v-btn outlined :to="{ path: '/gallery' }">
          <span class="text--secondary">Back to Gallery</span>
        </v-btn>
      </v-col>
      <v-spacer />
    </v-row>
    <v-row justify="center">
      <v-col cols="auto" class="d-flex pa-4">
        <v-img :src="`http://localhost:8000/api/image/${id}/original`" contain height="100%" width="100%" class="flex-grow-1"/>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

@Component
export default class ImageViewer extends Vue {
  id: string = this.$route.params.id;
}
</script>
