<template>
  <v-container fill-height fluid class="pa-0">
    <div class="upload-dropzone" ref="upload-dropzone" />
    <v-expand-transition>
      <v-toolbar v-show="imageSelected.some(e => e)" color="blue">
        <v-btn depressed :loading="loadingDeletingImages" @click="resetSelection" class="mr-2">
          Deselect Images
        </v-btn>
        <v-btn depressed :loading="loadingDeletingImages" :disabled="imageSelected.every(e => e)" @click="selectAll">
          Select All
        </v-btn>
        <v-spacer></v-spacer>
        <v-btn depressed color="error" :loading="loadingDeletingImages" @click="handleDeleteImages">
          Delete Selected
        </v-btn>
      </v-toolbar>
    </v-expand-transition>
    <v-progress-linear v-if="loading" absolute indeterminate top />
    <v-row
      v-if="images.length > 0"
      id="gallery"
      align="start"
      justify="start"
      class="px-3 fill-height"
      :style="getStyle"
      @click.stop.prevent="resetSelection"
    >
      <v-col v-for="(image, i) in images" :key="image.id">
        <ImageCard :image="image" @delete="reloadImages" :selected="imageSelected[i]" @click="handleImageClick(i)" />
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
import { ApiImagesRequest, ApiImagesResponse, ImageResponse, ApiDeleteImageRequest, ApiDeleteImageResponse, ApiInfoRequest, ApiInfoResponse } from '@/utils/api'
import axios, { AxiosResponse } from 'axios'

@Component({
  components: {
    ImageCard
  }
})
export default class Gallery extends Vue {
  loading = false
  images: Array<ImageResponse> = []
  imageSelected: Array<boolean> = []
  loadingDeletingImages = false;
  secondClickTimers: Map<number, number> = new Map()
  infoInterval = 0;
  lastUpdate = 0;

  displayError = false
  errorMessage = ''

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
        this.resetSelection()
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

  handleImageClick(index: number): void {
    if (!this.imageSelected[index]) {
      this.secondClickTimers.set(index, setTimeout(() => {
        this.secondClickTimers.delete(index)
      }, 250))
    } else {
      if (this.secondClickTimers.has(index)) {
        this.$router.push({ name: 'ImageViewer', params: { id: this.images[index].id.toString() } })
      }
    }
    this.$set(this.imageSelected, index, !this.imageSelected[index])
  }

  resetSelection(): void {
    this.imageSelected = new Array(this.images.length).fill(false)
    this.secondClickTimers.forEach(timeout => clearTimeout(timeout))
    this.secondClickTimers.clear()
  }

  selectAll(): void {
    this.imageSelected = new Array(this.images.length).fill(true)
  }

  async handleDeleteImages(): Promise<void> {
    this.loadingDeletingImages = true
    const response = await Promise.all(this.imageSelected.map((value, i) => [value, this.images[i].id]).filter(v => v[0]).map(v => v[1]).map(async id => {
      const response = await axios.delete<ApiDeleteImageRequest, AxiosResponse<ApiDeleteImageResponse>>(`/api/image/${id}`)
      if (response.status >= 200 && response.status < 300) {
        return true
      }
      return false
    }))
    if (!response.every(e => e)) {
      console.log('Not all images were deleted')
    }
    this.loadingDeletingImages = false
    this.reloadImages()
  }

  async mounted(): Promise<void> {
    this.hideDropZone()
    this.addDropzoneEvents()

    // this.reloadImages()
    this.checkLastUpdate()
    this.infoInterval = setInterval(this.checkLastUpdate, 3000)
  }

  async checkLastUpdate(): Promise<void> {
    const response = await axios.get<ApiInfoRequest, AxiosResponse<ApiInfoResponse>>('/api/info')
    if (response.status >= 200 && response.status < 300) {
      if (!('error' in response.data)) {
        if (this.lastUpdate < response.data.last_update) {
          this.reloadImages()
        }
        this.lastUpdate = response.data.last_update
      }
    }
  }

  beforeDestroy(): void {
    this.removeDropzoneEvents()
    clearInterval(this.infoInterval)
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
