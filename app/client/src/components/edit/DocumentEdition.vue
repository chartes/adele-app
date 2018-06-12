<template>

    <div>

        <tabs>

            <tab name="Transcription" :selected="true">

                <h1 class="title">Transcription</h1>
                <transcription-edition/>
            </tab>

            <tab name="Traduction">
                <h1 class="title">Traduction</h1>
                <translation-edition/>
            </tab>

            <tab name="Alignement">
                <h1 class="title">Alignement</h1>
                <alignment-edition/>
            </tab>

            <tab name="Facsimilé">
                <h1 class="title">Facsimilé</h1>
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
      console.log('DocumentEdition.mounted')
      console.log(' $store', this.$store)
      console.log(' actions', this.$store._actions)
      console.log(' getters', this.$store.getters)
      this.$store.dispatch('transcription/fetchTranscription');
      this.$store.dispatch('translation/fetchTranslation');
    }
  }
</script>

<style scoped>

</style>
