<template>
    <div class="columns">
        <div class="column is-half">

            <alignment-editor :initialContent="transcriptionHTML" :type="'transcription'"/>

        </div>
        <div class="column is-half">

            <alignment-editor :initialContent="translationHTML" :type="'translation'"/>

        </div>
    </div>
</template>

<script>

  import { mapGetters } from 'vuex'
  import TranslationEditor from '../editors/TranslationEditor'
  import AlignmentEditor from "../editors/AlignmentEditor";

  export default {
    name: "alignment-edition",
    components: {
      AlignmentEditor,
      TranslationEditor },
    computed: {
      ...mapGetters(['transcriptionHTML','translationHTML'])
    }
  }
</script>

<style scoped>

</style>