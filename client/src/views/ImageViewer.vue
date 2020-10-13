<template>
  <v-container fluid class="pa-0 d-flex flex-column">
    <v-progress-linear v-if="loading" absolute indeterminate top />
    <v-row justify="center" align="center" class="flex-grow-0">
      <v-col cols="auto" class="mx-2">
        <v-btn outlined :to="{ path: '/gallery' }">
          <v-icon>mdi-arrow-left</v-icon>
          <span class="text--secondary">Back to Gallery</span>
        </v-btn>
      </v-col>
      <v-spacer />
      <v-col v-if="!loading" cols="auto" class="mx-2">
        <v-row justify="center" align="center">
          <span>Objects in image:</span>
        </v-row>
        <v-row justify="center" align="center">
          <v-hover
            v-for="(obj, i) in image.objects" :key="i"
            @input="$set(showSpecificObject, i, arguments[0])"
          >
            <v-chip
              class="ma-2"
            >
              {{ obj.name.charAt(0).toUpperCase() + obj.name.slice(1) }}
            </v-chip>
          </v-hover>
        </v-row>
        <v-row v-if="image.description" justify="center" align="center" class="text-caption font-weight-light text--secondary">
          <span>Generated description: {{ image.description.charAt(0).toUpperCase() + image.description.slice(1) }}</span>
        </v-row>
      </v-col>
      <v-spacer />
      <v-col cols="auto" class="mx-2">
        <v-checkbox
          v-model="showObjects"
          :label="`Show all objects`"
        />
      </v-col>
    </v-row>
    <v-row v-if="!loading" justify="center" class="flex-grow-1">
      <v-col ref="image_container" class="ma-4 pa-0 relative">
        <div v-if="imageLoaded" class="boxes-container" :style="overlayStyle">
          <BoundingBox :display="showObjects || showSpecificObject[i]" :obj="obj" :image_height="imageHeight" :image_width="imageWidth" v-for="(obj, i) in image.objects" :key="i" />
        </div>
        <img ref="image" @load="imageDidLoad" :src="`http://localhost:8000/api/image/${id}/original`" class="pa-0 image">
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import axios, { AxiosResponse } from 'axios'

import { Component, Vue } from 'vue-property-decorator'
import BoundingBox from '@/components/BoundingBox.vue'
import { ImageResponse, ApiImageResponse, ApiImageRequest } from '@/utils/api'

@Component({
  components: {
    BoundingBox
  }
})
export default class ImageViewer extends Vue {
  id: string = this.$route.params.id;
  loading = true;
  imageLoaded = false;
  image?: ImageResponse = undefined;
  showObjects = false;
  showSpecificObject: Array<boolean> = []

  async getImageInfo(): Promise<void> {
    this.loading = true
    const response = await axios.get<ApiImageRequest, AxiosResponse<ApiImageResponse>>(`/api/image/${this.id}`)
    if (response.status >= 200 && response.status < 300) {
      if (!('error' in response.data)) {
        this.image = response.data
        console.log(this.image)
        this.showSpecificObject = new Array(this.image.objects.length).fill(false)
      }
    }
    this.loading = false
  }

  mounted(): void {
    this.getImageInfo()
    this.imageLoaded = false
  }

  imageDidLoad(): void {
    this.imageLoaded = true
  }

  get imageHeight(): number {
    // eslint-disable-next-line no-unused-expressions
    this.imageLoaded
    if (this.$refs.image instanceof Element) {
      return this.$refs.image.clientHeight
    }
    return 0
  }

  get imageWidth(): number {
    // eslint-disable-next-line no-unused-expressions
    this.imageLoaded
    if (this.$refs.image instanceof Element) {
      return this.$refs.image.clientWidth
    }
    return 0
  }

  get overlayStyle(): Record<string, unknown> {
    // eslint-disable-next-line no-unused-expressions
    this.imageLoaded
    if (this.$refs.image instanceof Element && this.$refs.image_container instanceof Element) {
      var parent = this.$refs.image_container.getBoundingClientRect()
      var image = this.$refs.image.getBoundingClientRect()
      return {
        top: `${Math.round(image.top - parent.top)}px`,
        left: `${Math.round(image.left - parent.left)}px`
      }
    }
    return {}
  }
}
</script>

<style scoped>
.image {
  object-fit: contain;
  height: 100%;
}

.relative {
  position: relative;
}

.boxes-container {
  position: absolute;
  width: 100px;
  height: 100px;
}
</style>
