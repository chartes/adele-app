<template>
  <span v-if="status === 'normal'" :key="'normal'" class="icon is-small">
    <i class="fas fa-save"></i>
  </span>
  <span v-else-if="status === 'success'" :key="'success'" class="icon is-small">
    <i class="fas fa-check"></i>
  </span>
  <span v-else-if="status === 'error'" :key="'error'" class="icon is-small">
    <i class="fas fa-exclamation-triangle"></i>
  </span>
</template>

<script>
  export default {
    name: 'SaveButtonIcon',
    props: {
      status: { type: String, default: 'normal'}
    }
  }
</script>

<style scoped>
</style>