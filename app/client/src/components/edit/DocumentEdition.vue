<template>

  <div id="document-edition">

    <loading-indicator :active="transcriptionLoading || translationLoading" :full-page="true"/>

    <div class="columns">
      <div class="column">
        <h1 class="title is-size-5"  style="display: inline-block; margin-bottom: 0.5em;" >Document {{ document.id }}</h1>
        <a class="button is-link is-small"
           v-if="allowedToSwapAuthor"
           style="margin-left: 20px"
           @click="swapUser = true"
        >
          <i class="fas fa-user-circle" style="margin-right: 8px"></i>{{ author.username }}
        </a>
      </div>
    </div>

    <tabs :on-tab-change="onTabChange" class="is-flex-column">

      <tab name="Édition" :selected="true">
        <transcription-edition/>
      </tab>

      <tab name="Facsimilé" >
        <facsimile-editor v-if="hasTranscription"></facsimile-editor>
        <minimal-message v-else-if="!hasImage" :body="'Aucun manifeste pour le moment. Un manifeste est nécessaire pour éditer le facsimilé.'"/>
        <minimal-message v-else :body="'Aucune transcription pour le moment. Une transcription est nécessaire pour éditer le facsimilé.'"/>
      </tab>

      <tab name="Parties du discours">
        <speechparts-edition  v-if="hasTranscription"/>
        <minimal-message v-else :body="'Aucune transcription pour le moment. Une transcription est nécessaire pour éditer les parties du discours.'"/>
      </tab>

      <tab name="Commentaires">
        <commentaries-edition v-if="hasTranscription"/>
        <minimal-message v-else :body="'Aucune transcription pour le moment. Une transcription est nécessaire pour éditer les commentaires.'"/>
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

  import Tabs from '../ui/Tabs.vue'
  import Tab from '../ui/Tab.vue'
  import FacsimileEditor from './FacsimileEdition';
  import TranscriptionEdition from './TranscriptionEdition';
  import AlignmentEdition from "./AlignmentEdition";
  import SpeechpartsEdition from "./SpeechpartsEdition";
  import NoticeEdition from "./NoticeEdition";
  import {mapState, mapGetters} from 'vuex';
  import LoadingIndicator from "../ui/LoadingIndicator";
  import AuthorSwapListForm from "../forms/AuthorSwapListForm";
  import MinimalMessage from "../ui/MinimalMessage";
  import SaveBar from "../ui/SaveBar";
  import CommentariesEdition from "./CommentariesEdition";

  export default {
    name: "document-edition",

    components: {
      CommentariesEdition,
      SaveBar,
      MinimalMessage,
      AuthorSwapListForm,
      LoadingIndicator,
      NoticeEdition,
      SpeechpartsEdition,
      AlignmentEdition,
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
      },
      onTabChange (oldTabName, newTabName) {
        if (oldTabName !== 'Notice' && this.savingStatus === 'tobesaved') this.save()
      }
    },
    computed: {
      hasTranscription () {
        return !!this.transcription
      },
      hasImage () {
        return !!this.document.images.length
      },
      allowedToSwapAuthor () {
        return (
          this.document.whitelist && !this.currentUserIsStudent
        )
      },
      ...mapState('user', ['author']),
      ...mapState('document', ['document']),
      ...mapState('transcription', ['transcriptionLoading', 'transcription', 'savingStatus', 'referenceTranscription']),
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
  .slide-to-left-enter, .slide-to-left-leave-to {
    transform: translateX(30%);
    opacity: 0;
  }
  .slide-to-right-enter-active {
    transition: all .3s ease;
  }
  .slide-to-right-leave-active {
    transition: all .8s cubic-bezier(1.0, 0.5, 0.8, 1.0);
  }
  .slide-to-right-enter, .slide-to-left-leave-to {
    transform: translateX(30%);
    opacity: 0;
  }
</style>