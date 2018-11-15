<template>
    <div class="tab">

      <slot v-if="isActive"></slot>

    </div>
</template>

<script>
  export default {
    name: "tab",
    props: {
        name: { required: true },
        selected: { default: false }
    },
    data () {
      return {
        isActive: this.selected
      }
    }
  }
</script>
