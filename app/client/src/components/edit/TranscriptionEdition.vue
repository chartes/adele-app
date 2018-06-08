<template>
    <div class="columns">
        <div class="column is-half">

            <IIIFMap :manifest="manifestURL" :draw-mode="false" :display-annotations-mode="false" ></IIIFMap>

        </div>
        <div class="column is-half">

            <transcription-editor v-if="!!transcriptionWithNotes" :initialContent="transcriptionWithNotes"/>

        </div>
    </div>
</template>

<script>

  import { mapGetters } from 'vuex'
  import IIIFMap from '../IIIFMap';
  import TranscriptionEditor from '../editors/TranscriptionEditor'

  export default {
    name: "transcription-edition",
    components: { IIIFMap,TranscriptionEditor },
    computed: {
      ...mapGetters(['manifestURL', 'transcription', 'transcriptionWithNotes'])
    }
  }
</script>

<style scoped>

</style>