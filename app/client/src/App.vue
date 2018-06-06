<template>
    <div id="app">
        <div v-if="!!document">
            <document-edition></document-edition>
        </div>
        <div v-if="!document">
            <a class="button is-loading">Loading</a>
        </div>
    </div>
</template>

<script>

  import { mapGetters } from 'vuex'
  import DocumentEdition from './components/DocumentEdition';

  export default {

    name: 'app',
    components: { DocumentEdition },
    props: ['doc_id', 'auth_token'],
    created () {
      this.$store.dispatch('getCurrentUser').then(() => {
        return this.$store.dispatch('getDocument', this.doc_id)
      });
      this.$store.dispatch('setAuthToken', this.auth_token)
    },
    computed: {
      ...mapGetters(['document'])
    }
  }
</script>

<style>
</style>
