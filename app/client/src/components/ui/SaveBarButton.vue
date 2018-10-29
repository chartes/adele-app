<template>
    <transition name="fade"  mode="out-in">

            <a class="button is-fullwidth"
               :class="buttonClass"
               @click="action"
               :key="status"
            >
              <save-button-icon :status="status"/> &nbsp {{ buttonText }}
            </a>

    </transition>
</template>

<script>
  import SaveButtonIcon from './SaveButtonIcon';
  export default {

    name: "save-bar-button",
    components: {SaveButtonIcon},
    props: {
      visible: {
        type: Boolean,
        default: true
      },
      status: {
        type: String,
        default: true
      },
      action: {
        type: Function,
        required: true
      }
    },
    computed: {
      buttonText () {
        switch (this.status) {
          case 'normal': return 'Sauvegarder les changements'
          case 'working': return 'Sauvegarde en cours...'
          case 'success': return 'Le document a bien été sauvegardé'
          case 'error': return 'La sauvegarde a échoué...'
        }
      },
      buttonClass () {
        switch (this.status) {
          case 'normal': return 'is-primary'
          case 'working': return 'is-loading disabled save-bar__working'
          case 'success': return 'disabled disabled save-bar__message has-text-success'
          case 'error': return 'disabled disabled save-bar__error has-text-danger'
        }
      },
    }
  }
</script>

<style scoped>
    a.disabled { pointer-events: none; }
</style>