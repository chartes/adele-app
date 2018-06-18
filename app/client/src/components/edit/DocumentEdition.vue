<template>

    <div>

        <tabs>

            <tab name="Transcription" :selected="true">
                <transcription-edition/>
            </tab>

            <tab name="Facsimilé">
                <facsimile-editor></facsimile-editor>
            </tab>

            <tab name="Parties du discours">
                <h1 class="title">Parties du discours</h1>
            </tab>

        </tabs>

    </div>

</template>

<script>


  import Tabs from '../ui/tabs.vue'
  import Tab from '../ui/tab.vue'
  import FacsimileEditor from '../editors/FacsimileEditor';
  import TranscriptionEdition from './TranscriptionEdition';
  import TranslationEdition from "./TranslationEdition";
  import AlignmentEdition from "./AlignmentEdition";

  export default {
    name: "document-edition",

    components: {
      AlignmentEdition,
      TranslationEdition,
      FacsimileEditor,
      TranscriptionEdition,
      Tabs,
      Tab
    },
    created() {
      this.$store.dispatch('transcription/fetch');
      //this.$store.dispatch('translation/fetch');
    }
  }
</script>

<style scoped>

</style>
