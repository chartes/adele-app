<template>
  <div id="transcription-edition" :class="isNight">

    <joke v-if="nbCols === 0"/>

    <p class="has-text-right is-size-7" style="margin-bottom: 1em">
      <span class="tag">
        Affichage : &nbsp;&nbsp;&nbsp;
        <visibility-toggle v-if="hasImage" :action="toggle" :param="'image'" :visible="visibility.image">image</visibility-toggle>
        &nbsp;&nbsp;&nbsp;
        <visibility-toggle :action="toggle" :param="'transcription'" :visible="visibility.transcription">transcription</visibility-toggle>
        &nbsp;&nbsp;&nbsp;
        <visibility-toggle :action="toggle" :param="'translation'" :visible="visibility.translation">traduction</visibility-toggle>
      </span>
    </p>

    <div class="columns">

      <div class="column" v-show="visibility.image && hasImage" :class="columnSize">

        <h2 class="subtitle">Image</h2>
        <IIIFMap :manifest="manifestURL" :draw-mode="false" :display-annotations-mode="false" ></IIIFMap>

      </div>

      <div class="column" v-show="visibility.transcription" :class="columnSize">

        <h2 class="subtitle">Transcription <small v-if="displayReferenceTranscription" class="tag is-dark is-round">Référence</small></h2>
        <div v-if="displayReferenceTranscription" v-html="referenceTranscription.content"></div>
        <transcription-editor v-else-if="displayTranscriptionEditor" :initialContent="transcriptionWithNotes"/>
        <div v-else>
          <minimal-message v-if="!transcriptionLoading" :body="'Aucune transcription pour le moment'"/>
          <p v-if="allowedToCreateTranscription"><a ref="createTranscriptionButton" class="button is-link" @click="createTranscription">Ajouter une transcription</a></p>
        </div>

      </div>

      <div class="column" v-show="visibility.translation" :class="columnSize">

        <h2 class="subtitle">Traduction <small v-if="displayReferenceTranslation" class="tag is-dark is-round">Référence</small></h2>
        <div v-if="displayReferenceTranslation" v-html="referenceTranslation.content"></div>
        <translation-editor v-else-if="displayTranslationEditor" :initialContent="translationWithNotes"/>
        <div v-else>
          <minimal-message v-if="!translationLoading" :body="'Aucune traduction pour le moment'"/>
          <p v-if="allowedToCreateTranslation"><a ref="createTranslationButton" class="button is-link" @click="createTranslation">Ajouter une traduction</a></p>
        </div>

      </div>
    </div>
  </div>
</template>

<script>

  import { mapGetters, mapState } from 'vuex'
  import IIIFMap from '../IIIFMap';
  import TranscriptionEditor from '../editors/TranscriptionEditor'
  import TranslationEditor from "../editors/TranslationEditor";
  import VisibilityToggle from "../ui/VisibilityToggle";
  import MinimalMessage from "../ui/MinimalMessage";
  import Joke from '../ui/Joke';
  import EditionColumnsToggleMixins from '../../mixins/EditionColumnsToggle'

  export default {
    name: "transcription-edition",
    mixins: [EditionColumnsToggleMixins],
    components: {
      Joke,
      MinimalMessage,
      VisibilityToggle,
      IIIFMap,
      TranslationEditor,
      TranscriptionEditor
    },
    data() {
      return {
        visibility: {
          image: true,
          transcription: true,
          translation: true,
        },
      }
    },
    methods: {
      createTranscription () {
        this.$refs.createTranscriptionButton.setAttribute('disabled','disabled');
        this.$store.dispatch('transcription/create')
          .then(data => {
            this.$store.dispatch('transcription/fetch');
          });
      },
      createTranslation () {
        this.$refs.createTranslationButton.setAttribute('disabled','disabled');
        this.$store.dispatch('translation/create')
          .then(data => {
            this.$store.dispatch('translation/fetch');
          });
      },
    },
    computed: {

      nbCols () {
        let size = 0;
        if (this.visibility.image && this.hasImage) size++;
        if (this.visibility.transcription) size++;
        if (this.visibility.translation) size++;
        return size;
      },
      displayTranscriptionEditor () {
        return !!this.transcriptionWithNotes && !this.transcriptionLoading
      },
      displayTranslationEditor () {
        return !!this.translationWithNotes && !this.translationLoading
      },

      allowedToCreateTranscription () {
        return (
          !this.transcriptionLoading
          &&
          this.currentUserIsAuthor
        )
      },
      allowedToCreateTranslation () {
        return (
          !this.translationLoading
          && this.currentUserIsAuthor
          && (
            (this.currentUserIsStudent && this.hasReferenceTranscription)
            || ((!this.currentUserIsStudent) && this.hasTranscription)
          )
        )
      },

      hasTranscription () {
        return !!this.transcriptionWithNotes;
      },
      hasImage () {
        return !!this.document.images.length;
      },
      hasReferenceTranscription () {
        return !!this.referenceTranscription
      },
      hasReferenceTranslation () {
        return !!this.referenceTranslation
      },

      displayReferenceTranscription () {
        return this.hasReferenceTranscription && this.currentUserIsStudent
      },
      displayReferenceTranslation () {
        return this.hasReferenceTranslation && this.currentUserIsStudent
      },

      ...mapGetters('document', ['manifestURL']),
      ...mapState('document', ['document']),
      ...mapState('transcription', ['transcriptionContent', 'transcriptionWithNotes', 'transcriptionWithSpeechparts', 'referenceTranscription', 'transcriptionLoading']),
      ...mapState('translation', ['translationWithNotes', 'translationLoading', 'referenceTranslation']),
      ...mapState('user', ['currentUser', 'author']),
      ...mapGetters('user', ['currentUserIsAuthor', 'currentUserIsStudent', 'currentUserIsTeacher']),
    }
  }
</script>