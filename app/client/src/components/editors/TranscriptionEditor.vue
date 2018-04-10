<template>
    <div class="columns">
        <div class="column is-half">

            <IIIFMap :manifest="manifestURL" :draw-mode="false" :display-annotations-mode="false" ></IIIFMap>

        </div>
        <div class="column is-half">

            <text-editor v-if="!!transcriptionFormatted" :initialContent="transcriptionFormatted"></text-editor>

        </div>
    </div>
</template>

<script>

  import { mapGetters } from 'vuex'
  import IIIFMap from '../IIIFMap';
  import TextEditor from './TranscriptionText'

  export default {
    name: "transcription-editor",
    components: { IIIFMap,TextEditor },
    computed: {
      ...mapGetters(['manifestURL', 'transcription', 'transcriptionFormatted'])
    },
    created () {
      console.log("TranscriptionEditor mounted")
        this.$store.dispatch('getTranscription')
    }
  }
</script>

<style scoped>

</style>