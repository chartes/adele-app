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
  import DocumentEdition from './components/edit/DocumentEdition';

  export default {

    name: 'app',
    components: { DocumentEdition },
    props: ['doc_id', 'auth_token'],
    created () {
      this.$store.dispatch('document/fetchDocument', this.doc_id);
      this.$store.dispatch('user/setAuthToken', this.auth_token)
      this.$store.dispatch('user/getCurrentUser');
    },
    computed: {
      ...mapGetters('document', ['document'])
    }
  }
</script>

<style>
</style>
