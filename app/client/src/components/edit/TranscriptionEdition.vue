<template>
    <div class="columns">
        <div class="column is-one-third">

            <IIIFMap :manifest="manifestURL" :draw-mode="false" :display-annotations-mode="false" ></IIIFMap>

        </div>
        <div class="column is-one-third">

            <transcription-editor v-if="!!transcriptionWithNotes" :initialContent="transcriptionWithNotes"/>

        </div>
        <div class="column is-one-third">

            <translation-editor v-if="!!translationWithNotes" :initialContent="translationWithNotes"/>

        </div>
    </div>
</template>

<script>

  import { mapGetters } from 'vuex'
  import IIIFMap from '../IIIFMap';
  import TranscriptionEditor from '../editors/TranscriptionEditor'
  import TranslationEditor from "../editors/TranslationEditor";

  export default {
    name: "transcription-edition",
    components: {
      IIIFMap,
      TranslationEditor,
      TranscriptionEditor
    },
    computed: {
      ...mapGetters('document', ['manifestURL']),
      ...mapGetters('transcription', ['transcription', 'transcriptionWithNotes']),
      ...mapGetters('translation', ['translationWithNotes'])
    }
  }
</script>

<style scoped>

</style>