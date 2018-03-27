<template>

  <div class="box is-info">

    <slot></slot>

  </div>

</template>

<script>
    export default {
        name: "message"
    }
</script>

<style scoped>
  .box {
    background: #eee;
    padding: 1em;
    border: 1px solid #ccc;
  }
</style>
