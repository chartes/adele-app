<template>
  <button class="save-button button" @click.prevent="clickHandler" :class="buttonClass">
    <save-button-icon :status="status"/>
     &nbsp; {{ statustext }}
  </button>
</template>

<script>
  import SaveButtonIcon from './SaveButtonIcon';
  export default {
    name: "save-button",
    components: {SaveButtonIcon},
    props: {
      status: {
        type: String,
        default: 'normal'
      },
      text: {
        type: String,
        default: 'Enregistrer'
      },
      action: {
        type: Function,
        required: true
      }
    },
    methods: {
      clickHandler () {
        this.$el.blur();
        this.action();
      },
    },
    computed: {

      buttonClass () {
        switch (this.status) {
          case 'normal': return 'is-primary'
          case 'working': return 'is-loading disabled save-bar__working'
          case 'success': return 'disabled disabled save-bar__message has-text-success'
          case 'error': return 'disabled disabled save-bar__error has-text-danger'
        }
      },
      statustext () {
        if (this.status === 'loading') {
          return 'Enregistrement...';
        } else if (this.status === 'error') {
          return 'Erreur';
        } else if (this.status === 'success') {
          return 'Enregistrement terminé';
        }
        return this.text;
      }
    }
  }
</script>

<style scoped>
  button.disabled { pointer-events: none; }
</style>