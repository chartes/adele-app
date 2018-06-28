<template>

    <div>

        <tabs>

            <tab name="Édition!!!" :selected="true">
                <transcription-edition/>
            </tab>

            <tab name="Facsimilé">
                <facsimile-editor></facsimile-editor>
            </tab>

            <tab name="Parties du discours">
                <speechparts-edition/>
            </tab>

            <tab name="Notice">
                <h1>Notice</h1>
                <notice-edition/>
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
  import SpeechpartsEditor from "../editors/SpeechpartsEditor";
  import SpeechpartsEdition from "./SpeechpartsEdition";
  import NoticeEdition from "./NoticeEdition";

  export default {
    name: "document-edition",

    components: {
      NoticeEdition,
      SpeechpartsEdition,
      SpeechpartsEditor,
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
    .slide-to-left-enter-active {
        transition: all .3s ease;
    }
    .slide-to-left-leave-active {
        transition: all .8s cubic-bezier(1.0, 0.5, 0.8, 1.0);
    }
    .slide-to-left-enter, .slide-to-left-leave-to
        /* .slide-fade-leave-active below version 2.1.8 */ {
        transform: translateX(30%);
        opacity: 0;
    }
    .slide-to-right-enter-active {
        transition: all .3s ease;
    }
    .slide-to-right-leave-active {
        transition: all .8s cubic-bezier(1.0, 0.5, 0.8, 1.0);
    }
    .slide-to-right-enter, .slide-to-left-leave-to
        /* .slide-fade-leave-active below version 2.1.8 */ {
        transform: translateX(30%);
        opacity: 0;
    }
</style>
