<template>
  <div id="app">
    <p>Document : {{ doc_id }}</p>
    <div v-if="document">
      <IIIFMap :manifest="manifestURL"></IIIFMap>
    </div>
    <!--<editor></editor>-->
  </div>
</template>

<script>

    import { mapGetters } from 'vuex'
    import Editor from './components/Editor';
    import IIIFMap from './components/IIIFMap';

    export default {

        name: 'app',
        components: { Editor, IIIFMap },
        props: ['doc_id'],
        computed: {
            ...mapGetters(['document', 'manifestURL'])
    }
    }
</script>

<style>
</style>
