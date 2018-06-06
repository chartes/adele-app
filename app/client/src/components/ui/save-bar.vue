<template>
    <div class="save-bar" v-show="visible">
        <div class="container">
            <a class="button is-primary" @click="action">Sauvegarder les changements</a>
        </div>
    </div>
</template>

<script>
  export default {
    name: "save-bar",
    props: {
      visible: {
        type: Boolean,
        default: true
      },
      action: {
        type: Function,
        required: true
      }
    }
  }
</script>

<style scoped>

</style>