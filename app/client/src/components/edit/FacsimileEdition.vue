<template>
    <div class="columns">
        <div class="column is-half">
            <h2 class="subtitle">Image</h2>
            <IIIFMap :manifest="manifestURL" :draw-mode="true" :display-annotations-mode="true" ></IIIFMap>
        </div>
        <div class="column is-half">
            <h2 class="subtitle">Transcription</h2>
            <facsimiles-editior :initialContent="transcriptionWithFacsimile" />
        </div>
    </div>
</template>

<script>

  import { mapGetters, mapState } from 'vuex'
  import IIIFMap from '../IIIFMap';
  import LoadingIndicator from "../ui/LoadingIndicator";
  import FacsimilesEditior from "../editors/FacsimileEditor";

  export default {
    name: "transcription-edition",
    components: {FacsimilesEditior, LoadingIndicator, IIIFMap },
    data () {
      return {  }
    },
    created() {
      console.log("FacsimileEditor.created")
      //this.$store.dispatch('facsimile/fetchCanvasNames');
    },
    watch: {
      canvasNames : function (newNames, oldNames) {
        console.log("Canvas names changed");

      }
    },
    computed: {
      ...mapGetters('document', ['manifestURL']),
      ...mapState('facsimile', ['canvasNames', 'currentCanvas']),
      ...mapState('transcription', ['transcriptionWithFacsimile']),
    }
  }
</script>

<style scoped>

</style>