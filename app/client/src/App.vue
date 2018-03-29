<template>
  <div id="app">
    <p>Document : {{ doc_id }}</p>
    <div v-if="document">
      <document-edition></document-edition>
    </div>
  </div>
</template>

<script>

    import { mapGetters } from 'vuex'
    import DocumentEdition from './components/DocumentEdition';

    export default {

        name: 'app',
        components: { DocumentEdition },
        props: ['doc_id'],
        computed: {
            ...mapGetters(['document'])
        }
    }
</script>

<style>
</style>
