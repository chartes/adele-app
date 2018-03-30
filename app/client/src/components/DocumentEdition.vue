<template>

  <div>

    <tabs>

      <tab name="Transcription" :selected="true">

        <h1 class="title">Transcription</h1>

        <transcription-editor></transcription-editor>

      </tab>

      <tab name="Traduction">

        <h1 class="title">Traduction</h1>

      </tab>

      <tab name="Alignement">
        <h1 class="title">Alignement</h1>

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


    import Quill from 'quill';
    import '../modules/quill/AdeleQuill';

    import Tabs from './ui/tabs.vue'
    import Tab from './ui/tab.vue'
    import FacsimileEditor from "./editors/FacsimileEditor";
    import TranscriptionEditor from "./editors/TranscriptionEditor";

    export default {
        name: "document-edition",

        components: {
            FacsimileEditor,
            TranscriptionEditor,
            Tabs,
            Tab
        },

        data () {
            return {

            }
        }

    }
</script>

<style scoped>

</style>
