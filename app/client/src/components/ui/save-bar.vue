<template>
    <transition name="slideup">
        <div class="save-bar" v-show="visible">
            <div class="container">
                <button class="button is-primary is-full-width" :disabled="disabled" @click="action">Sauvegarder les changements</button>
            </div>
        </div>
    </transition>
</template>

<script>
  export default {
    name: "save-bar",
    props: {
      visible: {
        type: Boolean,
        default: true
      },
      disabled: {
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
    a { pointer-events: none; }
</style>