<template>
  <v-container fill-height fluid class="pa-0">
    <div class="upload-dropzone" ref="upload-dropzone" />
    <v-progress-linear v-if="loading" absolute indeterminate top />
    <v-row
      v-if="images.length > 0"
      id="gallery"
      align="start"
      justify="start"
      class="px-3"
      :style="getStyle"
    >
      <v-col v-for="image in images" :key="image.id">
        <ImageCard :image="image" @delete="reloadImages" />
      </v-col>
    </v-row>
    <v-row
      v-if="!loading && images.length === 0"
      id="gallery"
      align="center"
      justify="center"
      class="px-3"
      :style="getStyle"
    >
      <v-col align-self-center>
        <span class="font-weight-light text--secondary">No images to show</span>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import ImageCard from '@/components/ImageCard.vue'
import { ApiImagesRequest, ApiImagesResponse, ImageResponse } from '@/utils/api'
import axios, { AxiosResponse } from 'axios'

@Component({
  components: {
    ImageCard
  }
})
export default class Gallery extends Vue {
  loading = false;
  images: Array<ImageResponse> = []

  displayError = false;
  errorMessage = '';

  showDropZone(): void {
    const dropzone = this.$refs['upload-dropzone']
    if (dropzone && dropzone instanceof HTMLElement) {
      dropzone.style.display = 'block'
    }
  }

  hideDropZone(): void {
    const dropzone = this.$refs['upload-dropzone']
    if (dropzone && dropzone instanceof HTMLElement) {
      dropzone.style.display = 'none'
    }
  }

  preventDefaults(e: Event): void {
    if (e && e instanceof DragEvent && e.dataTransfer) {
      e.dataTransfer.dropEffect = 'copy'
    }
    e.preventDefault()
    e.stopPropagation()
  }

  async handleDrop(e: Event): Promise<void> {
    this.hideDropZone()

    if (e && e instanceof DragEvent && e.dataTransfer) {
      const filesLength = e.dataTransfer.files.length
      const files = e.dataTransfer.files
      for (var i = 0; i < filesLength; i++) {
        await this.uploadFile(files[i])
      }
    }
    this.reloadImages()
  }

  async uploadFile(file: File): Promise<void> {
    const formData = new FormData()
    formData.append('file', file)
    await axios.put('/api/image', formData)
  }

  addDropzoneEvents(): void {
    window.addEventListener('dragenter', this.showDropZone)
    const dropzone = this.$refs['upload-dropzone']
    if (dropzone instanceof HTMLElement) {
      ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, this.showDropZone)
      })

      ;['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, this.hideDropZone)
      })

      ;['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, this.preventDefaults)
      })

      dropzone.addEventListener('drop', this.handleDrop)
    }
  }

  removeDropzoneEvents(): void {
    window.removeEventListener('dragenter', this.showDropZone)
    const dropzone = this.$refs['upload-dropzone']
    if (dropzone instanceof HTMLElement) {
      ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.removeEventListener(eventName, this.showDropZone)
      })

      ;['dragleave', 'drop'].forEach(eventName => {
        dropzone.removeEventListener(eventName, this.hideDropZone)
      })

      ;['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropzone.removeEventListener(eventName, this.preventDefaults)
      })

      dropzone.removeEventListener('drop', this.handleDrop)
    }
  }

  async reloadImages(): Promise<void> {
    this.loading = true
    const response = await axios.get<ApiImagesRequest, AxiosResponse<ApiImagesResponse>>('/api/images')
    if (response.status >= 200 && response.status < 300) {
      if ('error' in response.data) {
        if (response.data.error) {
          this.displayError = true
          this.errorMessage = response.data.error_message
        }
      } else {
        this.images = response.data
      }
    }
    this.loading = false
  }

  get getStyle(): string {
    if (this.loading) {
      return 'opacity: 50%;'
    } else {
      return ''
    }
  }

  async mounted(): Promise<void> {
    this.hideDropZone()
    this.addDropzoneEvents()

    this.reloadImages()
  }

  beforeDestroy(): void {
    this.removeDropzoneEvents()
  }
}
</script>

<style lang="scss" scoped>
$colorBlue: #60a7dc;

.upload-dropzone {
  box-sizing: border-box;
  display: none;
  position: fixed;
  width: 100%;
  height: 100%;
  left: 0;
  top: 0;
  z-index: 99999;

  background: rgba($colorBlue, 0.8);
  border: 11px dashed $colorBlue;
}

#gallery {
  transition: opacity 0.3s;
}
</style>
