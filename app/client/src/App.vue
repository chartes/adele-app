<template>
  <div id="app">
    <IIIFMap manifest="http://193.48.42.68/adele/iiif/manifests/man95.json"></IIIFMap>
    <editor></editor>
  </div>
</template>

<script>

  import Editor from './components/Editor';
  import IIIFMap from './components/IIIFMap';

  export default {

    name: 'app',
    components: { Editor, IIIFMap },

  }
</script>

<style>
</style>
