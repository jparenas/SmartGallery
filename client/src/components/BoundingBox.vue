<template>
  <div class="absolute border" :style="style">
    <span class="border text ma-0 pa-0">{{ obj.name }}</span>
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import { ImageObject } from '@/utils/api'

@Component
export default class BoundingBox extends Vue {
   @Prop() private obj!: ImageObject;
   @Prop() private display!: boolean;
   // eslint-disable-next-line camelcase
   @Prop() private image_height!: number;
   // eslint-disable-next-line camelcase
   @Prop() private image_width!: number;

   get style(): Record<string, unknown> {
     const top = Math.min(this.image_height * this.obj.y1, this.image_height)
     const left = Math.min(this.image_width * this.obj.x1, this.image_width)
     return {
       top: `${Math.round(top)}px`,
       left: `${Math.round(left)}px`,
       width: `${Math.round(Math.min((this.image_width * this.obj.x2) - left, this.image_width - left))}px`,
       height: `${Math.round(Math.min((this.image_height * this.obj.y2) - top, this.image_height - top))}px`,
       display: this.display ? 'block' : 'none'
     }
   }
}
</script>

<style scoped>
.absolute {
  position: absolute;
}

.border {
  border: 3px solid #000000;
}

.text {
  background: #000000;
  color: white;
  left: 0;
  top: 0;
  position: absolute;
}
</style>
