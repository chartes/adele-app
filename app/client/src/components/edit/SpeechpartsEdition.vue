<template>
    <div class="columns">
        <div class="column is-half">

            <speechparts-editor :initialContent="transcriptionWithSpeechparts" />

        </div>
        <div class="column is-half">
            <div v-if="mouseOver" class="speechpart-tooltip" :style="tooltipPosition">
                <p class="speechpart-tooltip-title"><strong>{{mouseOver.speech_part_type.label}}</strong></p>
                <p v-if="hasDefinition" class="speechpart-tooltip-definition"><em>{{mouseOver.speech_part_type.definition}}</em></p>
                <div class="speechpart-tooltip-note"><em v-html="mouseOver.note"></em></div>
            </div>
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
      hasDefinition() {
        return this.mouseOver.speech_part_type && this.mouseOver.speech_part_type.definition && this.this.mouseOver.speech_part_type.definition.length > 0
      },
      tooltipPosition () {
        return 'position:fixed;top: '+this.mouseOverY+'px;left:50%;'
      },
      ...mapState('transcription', ['transcriptionWithSpeechparts']),
      ...mapState('speechparts', ['mouseOver', 'mouseOverY']),
    }
  }
</script>

<style scoped>

</style>