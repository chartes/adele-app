<template>

    <div>

        <loading-indicator :active="!transcription" :full-page="true"/>

        <div class="columns">
            <div class="column">
                <h1 class="title is-size-5">Document {{ document.id }}</h1>
            </div>
            <div class="column" v-if="$store.getters['user/currentUserIsTeacher']">
                <p class="has-text-right">Le travail affiché est celui de : {{ author.first_name }} {{ author.last_name }} <a class="button is-link is-small" @click="changeAuthor">Changer</a></p>
            </div>
        </div>

        <tabs>

            <tab name="Édition" :selected="true">
                <transcription-edition/>
            </tab>

            <tab name="Facsimilé">
                <facsimile-editor></facsimile-editor>
            </tab>

            <tab name="Parties du discours" v-if="!!transcription">
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
  import {mapState, mapGetters} from 'vuex';
  import LoadingIndicator from "../ui/LoadingIndicator";

  export default {
    name: "document-edition",

    components: {
      LoadingIndicator,
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
    },
    methods: {
      changeAuthor () {
        console.log("changeAuthor");

        var newAuthor = {
        active:true,
        email:"eleve1@gmail.com",
        email_confirmed_at:"2018-03-29 10:29:20",
        first_name:"PrenomEleve1",
        id:5,
        last_name:"NomEleve1",
        //roles:Array[1]
        username:"Eleve1"}

        this.$store.dispatch('user/setAuthor', newAuthor);
        this.$store.dispatch('transcription/fetch');
      }
    },
    computed: {
      ...mapState('user', ['author']),
      ...mapState('document', ['document']),
      ...mapState('transcription', ['transcription']),
      ...mapState('translation', ['translation']),
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
