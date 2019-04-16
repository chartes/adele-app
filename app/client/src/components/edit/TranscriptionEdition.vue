<template>
  <div id="transcription-edition" :class="isNight">

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

      <div class="column is-flex-column" v-show="visibility.image && hasImage" :class="columnSize">

        <h2 class="subtitle">Image</h2>
        <IIIFMap :manifest="manifestURL" :draw-mode="false" :display-annotations-mode="false" class="is-flex-fill" ></IIIFMap>

      </div>

      <div class="column" v-show="visibility.transcription" :class="columnSize">

        <h2 class="subtitle">Transcription <small v-if="displayReferenceTranscription" class="tag is-dark is-round">Référence</small>
          <span v-if="currentUserIsTeacher && currentUser.id !== author.id" style="margin-left: 8px" class="button is-link is-small" @click="openCloneTranscriptionDialog">
            <i class="fas fa-copy" style="margin-right: 8px"></i>
            Cloner
          </span>
        </h2>
        
        
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
  
    <modal-confirm-clone-transcription
        v-if="cloneTranscriptionMode === 'clone'"
        :cancel="closeCloneTranscriptionMode"
        :submit="cloneTranscription">
    </modal-confirm-clone-transcription>
    
  </div>
</template>

<script>

  import { mapGetters, mapState } from 'vuex'
  import IIIFMap from '../IIIFMap';
  import TranscriptionEditor from '../editors/TranscriptionEditor'
  import TranslationEditor from "../editors/TranslationEditor";
  import VisibilityToggle from "../ui/VisibilityToggle";
  import MinimalMessage from "../ui/MinimalMessage";
  import EditionColumnsToggleMixins from '../../mixins/EditionColumnsToggle'
  import ModalConfirmCloneTranscription from "../forms/ModalConfirmCloneTranscription";

  export default {
    name: "transcription-edition",
    mixins: [EditionColumnsToggleMixins],
    components: {
      MinimalMessage,
      VisibilityToggle,
      IIIFMap,
      TranslationEditor,
      TranscriptionEditor,
	    ModalConfirmCloneTranscription
    },
    data() {
      return {
        visibility: {
          image: true,
          transcription: true,
          translation: true,
        },
	      cloneTranscriptionMode: false
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
      openCloneTranscriptionDialog() {
      	this.cloneTranscriptionMode = "clone";
      },
	    closeCloneTranscriptionMode() {
		    console.log("close transcriptipon mode");
		    this.cloneTranscriptionMode = false;
	    },
	    cloneTranscription() {
		    console.log("cloning transcription");
		    this.$store.dispatch('transcription/cloneContent')
			    .then(data => {
				    location.reload();
				    //this.closeCloneTranscriptionMode();
			    });
	    }
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
          && (this.hasReferenceTranscription || this.currentUserIsAdmin)
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
      ...mapGetters('user', ['currentUserIsAuthor', 'currentUserIsStudent', 'currentUserIsTeacher', 'currentUserIsAdmin']),
    }
  }
</script>
