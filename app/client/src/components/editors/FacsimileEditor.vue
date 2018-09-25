<template>
    <div class="columns">
        <div class="column is-half">
            <IIIFMap :manifest="manifestURL" :draw-mode="true" :display-annotations-mode="true" ></IIIFMap>
        </div>
        <div class="column is-half">
            <h1>Transcription</h1>
        </div>
        <loading-indicator :active="loading" :full-page="true"/>
    </div>
</template>

<script>

  import { mapGetters, mapState } from 'vuex'
  import IIIFMap from '../IIIFMap';
  import LoadingIndicator from "../ui/LoadingIndicator";

  export default {
    name: "transcription-editor",
    components: { LoadingIndicator, IIIFMap },
    data () {
      return {  }
    },
    created() {
      console.log("FacsimileEditor.created")
      this.$store.dispatch('facsimile/fetchCanvasNames');
    },
    watch: {
      canvasNames : function (newNames, oldNames) {
        console.log("Canvas names changed");

      }
    },
    computed: {
      ...mapGetters('document', ['manifestURL']),
      ...mapState('facsimile', ['canvasNames', 'currentCanvas', 'loading']),
    }
  }
</script>

<style scoped>

</style>