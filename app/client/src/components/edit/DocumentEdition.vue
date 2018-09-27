<template>

    <div>

        <loading-indicator :active="transcriptionLoading && translationLoading" :full-page="true"/>

        <div class="columns">
            <div class="column">
                <h1 class="title is-size-5"  style="display: inline-block; margin-bottom: 0.5em;" >Document {{ document.id }}</h1>
                <a class="button is-link is-small" v-if="document.whitelist && !currentUserIsStudent" style="margin-left: 20px" @click="swapUser = true">
                    <i class="fas fa-user-circle" style="margin-right: 8px"></i>{{ author.username }}
                </a>
            </div>
        </div>

        <tabs>

            <tab name="Édition" :selected="true">
                <transcription-edition/>
            </tab>

            <tab name="Facsimilé">
                <div v-if="!!transcription">
                    <facsimile-editor></facsimile-editor>
                </div>
                <minimal-message v-else :body="'Aucune transcription pour le moment. Une transcription est nécessaire pour éditer le facsimilé.'"/>
            </tab>

            <tab name="Parties du discours">
                <div v-if="!!transcription">
                    <speechparts-edition/>
                </div>
                <minimal-message v-else :body="'Aucune transcription pour le moment. Une transcription est nécessaire pour éditer les parties du discours.'"/>
            </tab>

            <tab v-if="!currentUserIsStudent" name="Notice">
                <h1>Notice</h1>
                <notice-edition/>
            </tab>

        </tabs>

        <author-swap-list-form v-if="swapUser" :selected-author="author" :cancel="cancelSwap" :submit="swapAuthor"/>


        <save-bar :action="save"/>

    </div>

</template>

<script>

  import Tabs from '../ui/tabs.vue'
  import Tab from '../ui/tab.vue'
  import FacsimileEditor from './FacsimileEdition';
  import TranscriptionEdition from './TranscriptionEdition';
  import TranslationEdition from "./TranslationEdition";
  import AlignmentEdition from "./AlignmentEdition";
  import SpeechpartsEditor from "../editors/SpeechpartsEditor";
  import SpeechpartsEdition from "./SpeechpartsEdition";
  import NoticeEdition from "./NoticeEdition";
  import {mapState, mapGetters} from 'vuex';
  import LoadingIndicator from "../ui/LoadingIndicator";
  import AuthorSwapListForm from "../forms/AuthorSwapListForm";
  import MinimalMessage from "../ui/MinimalMessage";
  import SaveBar from "../ui/SaveBar";

  export default {
    name: "document-edition",

    components: {
      SaveBar,
      MinimalMessage,
      AuthorSwapListForm,
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
    data () {
      return { swapUser: false }
    },
    created() {
      this.$store.dispatch('transcription/fetch');
    },
    methods: {
      swapAuthor (newAuthor) {
        this.cancelSwap();
        this.$store.dispatch('user/setAuthor', newAuthor);
        this.$store.dispatch('transcription/reset');
        this.$store.dispatch('translation/reset');
        this.$store.dispatch('transcription/fetch');
      },
      cancelSwap () {
        this.swapUser = false;
      },
      save () {
        this.$store.dispatch('transcription/save')
      }
    },
    computed: {
      enabledSwapAuthor () {
        return (
          this.$store.getters['user/currentUserIsTeacher']
          && this.document.whitelist
          && this.document.whitelist.users
          && this.document.whitelist.users.length > 0
        );
      },
      ...mapState('user', ['author']),
      ...mapState('document', ['document']),
      ...mapState('transcription', ['transcriptionLoading', 'transcription']),
      ...mapState('translation', ['translation', 'translationLoading']),
      ...mapGetters('user', ['currentUserIsStudent']),
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
