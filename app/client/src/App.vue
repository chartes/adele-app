<template>
    <div id="app">
        <div v-if="!!document">
            <document-edition></document-edition>
        </div>
    </div>
</template>

<script>

  import { mapGetters } from 'vuex'
  import DocumentEdition from './components/edit/DocumentEdition';

  export default {

    name: 'app',
    components: { DocumentEdition },
    props: ['doc_id', 'auth_token'],
    created () {
      this.$store.dispatch('user/setAuthToken', this.auth_token).then(() => {
          this.$store.dispatch('user/getCurrentUser').then(() => {
            return this.$store.dispatch('document/fetch', this.doc_id)
          });
      });

    },
    computed: {
      ...mapGetters('document', ['document'])
    }
  }
</script>

<style>
    #app {
        min-height: 100vh;
    }
</style>
