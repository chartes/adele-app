<template>
    <div class="columns">
        <div class="column is-half">
            <IIIFMap :manifest="manifestURL" :draw-mode="false"></IIIFMap>
            <div  v-if="!!transcription">

                <div class="box" v-for="note in transcription.notes"></div>

            </div>
            <div  v-if="!!transcription" v-html="transcription.content"></div>
        </div>
        <div class="column is-half">
            <text-editor v-if="!!transcription" :initialContent="transcription.content"></text-editor>
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
      ...mapGetters(['manifestURL', 'transcription'])
    },
    created () {
      console.log("TranscriptionEditor mounted")
        this.$store.dispatch('getTranscription')
    }
  }
</script>

<style scoped>

</style>