<template>
    <div class="columns">
        <div class="column is-half">

            <speechparts-editor :initialContent="transcriptionWithSpeechparts" />

        </div>
        <div class="column is-half">

        </div>
    </div>
</template>

<script>

  import { mapState } from 'vuex'
  import SpeechpartsEditor from "../editors/SpeechpartsEditor";

  export default {
    name: "speechparts-edition",
    components: {
      SpeechpartsEditor,
    },
    computed: {
      ...mapState('transcription', ['transcriptionWithSpeechparts']),
    }
  }
</script>

<style scoped>

</style>