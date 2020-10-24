<template>
  <v-card :class="classes" max-width="400" @click.native.stop.prevent="$emit('click', arguments[0])">
    <v-img
      class="text-right"
      height="250px"
      :src="`http://localhost:8000/api/image/${image.id}/small`"
    >
      <v-row justify="end" no-gutters class="mx-1 my-1">
        <v-col>
          <v-btn fab small :to="{ name: 'ImageViewer', params: { id: image.id }}">
            <v-icon>mdi-fullscreen</v-icon>
          </v-btn>
        </v-col>
      </v-row>
      <v-row justify="end" no-gutters class="mx-1">
        <v-col>
          <v-menu bottom auto offset-y>
            <template v-slot:activator="{ on, attrs }">
              <v-btn fab small v-bind="attrs" v-on="on">
                <v-icon>mdi-dots-horizontal</v-icon>
              </v-btn>
            </template>

            <v-list>
              <v-list-item @click="deleteImage" dense class="px-0 text-center">
                <v-list-item>Delete</v-list-item>
              </v-list-item>
            </v-list>
          </v-menu>
        </v-col>
      </v-row>
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
        <v-col v-if="image.objects">
          <div>
            <b>Objects</b><br />
            {{ image.objects.length }}
          </div>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import { ImageResponse, ApiDeleteImageRequest, ApiDeleteImageResponse } from '@/utils/api'
import axios, { AxiosResponse } from 'axios'

@Component
export default class ImageCard extends Vue {
  @Prop() private image!: ImageResponse;
  @Prop() private selected!: boolean;

  async deleteImage(): Promise<void> {
    const response = await axios.delete<ApiDeleteImageRequest, AxiosResponse<ApiDeleteImageResponse>>(`/api/image/${this.image.id}`)
    if (response.status >= 200 && response.status < 300) {
      if (!('error' in response.data)) {
        this.$emit('delete')
      }
    }
  }

  get classes(): Record<string, boolean> {
    return {
      'mx-auto': true,
      selected: this.selected
    }
  }
}
</script>

<style lang="scss" scoped>
@import '~vuetify/src/styles/styles.sass';

.selected {
  background: map-get($blue, 'lighten-1') !important;
  outline: 4px solid map-get($blue, 'darken-1') !important;
}
</style>
