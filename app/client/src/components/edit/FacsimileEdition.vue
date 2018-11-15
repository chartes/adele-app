<template>

  <div id="facsimile-edition" :class="isNight">

    <p class="has-text-right is-size-7" style="margin-bottom: 1em">
      <span class="tag">
        Affichage : &nbsp;&nbsp;&nbsp;
        <visibility-toggle v-if="hasImage" :action="toggle" :param="'image'" :visible="visibility.image">image</visibility-toggle>
        &nbsp;&nbsp;&nbsp;
        <visibility-toggle :action="toggle" :param="'transcription'" :visible="visibility.transcription">transcription</visibility-toggle>
      </span>
    </p>

    <div class="columns">
      <div class="column"  v-show="visibility.image && hasImage" :class="columnSize">
        <h2 class="subtitle">Image</h2>
        <IIIFMap :manifest="manifestURL" :draw-mode="true" :display-annotations-mode="true" ></IIIFMap>
      </div>
      <div class="column" v-show="visibility.transcription" :class="columnSize">
        <h2 class="subtitle">Transcription</h2>
        <facsimiles-editor :initialContent="transcriptionWithFacsimile" />
      </div>
    </div>
  </div>
</template>

<script>

  import { mapGetters, mapState } from 'vuex'
  import IIIFMap from '../IIIFMap';
  import LoadingIndicator from '../ui/LoadingIndicator';
  import FacsimilesEditor from '../editors/FacsimileEditor';
  import VisibilityToggle from "../ui/VisibilityToggle";
  import EditionColumnsToggleMixins from '../../mixins/EditionColumnsToggle'

  export default {
    name: "facsimile-edition",
    mixins: [EditionColumnsToggleMixins],
    components: {FacsimilesEditor, LoadingIndicator, IIIFMap, VisibilityToggle },
    data () {
      return {
        visibility: {
          image: true,
          transcription: true,
        },
      }
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

      nbCols () {
        let size = 0;
        if (this.visibility.image) size++;
        if (this.visibility.transcription) size++;
        return size;
      },
      hasImage () {
        return !!this.document.images.length;
      },

      ...mapGetters('document', ['manifestURL']),
      ...mapState('document', ['document']),
      ...mapState('facsimile', ['canvasNames', 'currentCanvas']),
      ...mapState('transcription', ['transcriptionWithFacsimile']),
    }
  }
</script>

<style scoped>

</style>