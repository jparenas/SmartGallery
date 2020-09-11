<template>
  <v-card class="mx-auto" max-width="400">
    <v-img
      class="text-right"
      height="200px"
      :src="`http://localhost:8000/api/image/small/${image.id}`"
      contain
    >
      <v-btn fab small class="ma-2">
        <v-icon>mdi-fullscreen</v-icon>
      </v-btn>
    </v-img>

    <v-card-text class="text--primary">
      <v-row dense no-gutters>
        <v-col>
          <div>
            <b>Owner</b><br />
            {{ image.owner }}
          </div>
        </v-col>
        <v-col>
          <div>
            <b>Image name</b><br />
            {{ image.original_filename }}
          </div>
        </v-col>
        <v-col v-if="image.original_width">
          <div>
            <b>Width</b><br />
            {{ image.original_width }}px
          </div>
        </v-col>
        <v-col v-if="image.original_height">
          <div>
            <b>Height</b><br />
            {{ image.original_height }}px
          </div>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import { ImageResponse } from '@/utils/api'

@Component
export default class ImageCard extends Vue {
  @Prop() private image!: ImageResponse;
}
</script>
