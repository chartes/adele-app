<template>
    <div>
        <p class="has-text-right is-size-7" style="margin-bottom: 1em">
            <span class="tag">
            Affichage : &nbsp;&nbsp;&nbsp;
            <visibility-toggle :action="toggle" :param="'image'" :visible="visibility.image">image</visibility-toggle>
            &nbsp;&nbsp;&nbsp;
            <visibility-toggle :action="toggle" :param="'transcription'" :visible="visibility.transcription">transcription</visibility-toggle>
            &nbsp;&nbsp;&nbsp;
            <visibility-toggle :action="toggle" :param="'translation'" :visible="visibility.translation">traduction</visibility-toggle>
        </span>
        </p>
        <div class="columns">
            <div class="column" v-show="visibility.image" :class="columnSize">

                <h2 class="subtitle">Image</h2>

                <p><a href="#" @click.prevent="debug.content=!debug.content">Content</a></p>
                <small v-if="debug.content" v-text="transcriptionContent"></small>

                <p><a href="#" @click.prevent="debug.speechparts=!debug.speechparts">Speechparts</a></p>
                <small v-if="debug.speechparts" v-text="transcriptionWithSpeechparts"></small>

                <IIIFMap :manifest="manifestURL" :draw-mode="false" :display-annotations-mode="false" ></IIIFMap>

            </div>
            <div class="column" v-show="visibility.transcription" :class="columnSize">

                <h2 class="subtitle">Transcription</h2>

                <transcription-editor v-if="!!transcriptionWithNotes" :initialContent="transcriptionWithNotes"/>

            </div>
            <div class="column" v-show="visibility.translation" :class="columnSize">

                <h2 class="subtitle">Traduction</h2>

                <translation-editor v-if="!!translationWithNotes" :initialContent="translationWithNotes"/>

            </div>
        </div>
    </div>
</template>

<script>

  import { mapGetters, mapState } from 'vuex'
  import IIIFMap from '../IIIFMap';
  import TranscriptionEditor from '../editors/TranscriptionEditor'
  import TranslationEditor from "../editors/TranslationEditor";
  import VisibilityToggle from "../ui/VisibilityToggle";

  export default {
    name: "transcription-edition",
    components: {
      VisibilityToggle,
      IIIFMap,
      TranslationEditor,
      TranscriptionEditor
    },
    data() {
      return {
        visibility: {
          image: true,
          transcription: true,
          translation: true,
        },
        debug: {
          content: false,
          notes: false,
          align: false,
          speechparts: false
        }
      }
    },
    methods: {
      toggle (what) {
        console.log('toggle', what)
        this.visibility[what] = !this.visibility[what];
      }
    },
    computed: {
      columnSize () {
        let size = 0;
        if (this.visibility.image) size++;
        if (this.visibility.transcription) size++;
        if (this.visibility.translation) size++;
        if (size == 2) {
          return 'is-half'
        } else if (size == 3) {
          return 'is-one-third'
        }
        return false;
      },
      ...mapGetters('document', ['manifestURL']),
      ...mapState('transcription', ['transcriptionContent', 'transcriptionWithNotes', 'transcriptionWithSpeechparts']),
      ...mapGetters('translation', ['translationWithNotes'])
    }
  }
</script>

<style scoped>

</style>