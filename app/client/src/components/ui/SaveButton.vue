<template>
    <button class="save-button button" @click.prevent="clickHandler" :class="statusClass">{{ statustext }}</button>
</template>

<script>
  export default {
    name: "save-button",
    props: ['status', 'text', 'action'],
    methods: {
      clickHandler () {
        this.$el.blur();
        this.action();
      },
    },
    computed: {

      statusClass () {
        if (this.status === 'saving') {
          return 'is-loading is-primary is-outlined';
        } else if (this.status === 'error') {
          return 'is-danger is-outlined';
        } else if (this.status === 'success') {
          return 'is-success is-outlined';
        }
        return 'is-primary';
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

</style>