<template>
  <div id="translation-edition" :class="isNight">

    <p class="has-text-right is-size-7" style="margin-bottom: 1em">
      <span class="tag">
        Affichage : &nbsp;&nbsp;&nbsp;
        <visibility-toggle :action="toggle" :param="'transcription'" :visible="visibility.transcription">transcription</visibility-toggle>
        &nbsp;&nbsp;&nbsp;
        <visibility-toggle :action="toggle" :param="'translation'" :visible="visibility.translation">traduction</visibility-toggle>
      </span>
    </p>

    <div v-if="!!transcriptionViewContent" class="columns">
  
      <div class="column is-flex-column" v-show="visibility.transcription" :class="columnSize" id="transcriptionContainer">
        <h2 class="subtitle">Transcription
          <a style="margin-right: 8px; color: green" class="button is-small is-light" disabled>validée</a>
        </h2>
        <div v-html="transcriptionViewContent"></div>
      </div>

      <div class="column" v-show="visibility.translation" :class="columnSize">

        <h2 class="subtitle">Traduction
          <button v-if="currentUserIsTeacher && currentUserIsAuthor && document.validation_stage_label === 'none'"
             :disabled="!translationSaved"
             style="margin-right: 8px;"
             class="button is-small is-light" @click="validateTranslation">
            non validée
          </button>
          <button v-else-if="currentUserIsTeacher && currentUserIsAuthor && document.validation_stage_label !== 'none'"
             style="margin-right: 8px; color: green"
             class="button is-small is-light"
             @click="unvalidateTranslation">validée
          </button>

          <!-- Éditer la traduction d'un élève-->
          <span v-if="currentUserIsTeacher && currentUser.id !== author.id">
            <button v-if="!editStudentTranslation" style="margin-left: 8px" class="button is-light is-small"
                    @click="startEditingStudentTranslation">
              <i class="fas fa-edit" style="margin-right: 8px"></i>
              Éditer
            </button>
            <button v-else style="margin-left: 8px" class="button is-light is-small" :disabled="!translationSaved">
              <i class="fas fa-edit" style="margin-right: 8px"></i>
              Éditer
            </button>
          </span>
          
          <button v-if="currentUserIsTeacher && currentUser.id !== author.id" style="margin-left: 8px"
                  :disabled="savingStatus !== 'uptodate'"
                class="button is-light is-small" @click="openCloneTranslationDialog">
            <i class="fas fa-copy" style="margin-right: 8px"></i>
            Cloner
          </button>
        </h2>
        <div v-if="displayReferenceTranslation" v-html="referenceTranslation.content"></div>
        <translation-editor v-else-if="displayTranslationEditor" :initialContent="translationWithNotes"/>
        <div v-else>
          <minimal-message v-if="!translationLoading" :body="'Aucune traduction pour le moment'"/>
          <p v-if="allowedToCreateTranslation"><a ref="createTranslationButton" class="button is-link" @click="createTranslation">Ajouter une traduction</a></p>
        </div>

      </div>
    </div>
    <div v-else>
      <minimal-message :body="'Aucune transcription validée pour le moment.'"/>
    </div>
    
    <modal-confirm-clone-translation
        v-if="cloneTranslationMode === 'clone'"
        :cancel="closeCloneTranslationMode"
        :submit="cloneTranslation">
    </modal-confirm-clone-translation>
    
  </div>
</template>

<script>

  import { mapGetters, mapState } from 'vuex'
  import IIIFMap from '../IIIFMap';
  import TranslationEditor from "../editors/TranslationEditor";
  import VisibilityToggle from "../ui/VisibilityToggle";
  import MinimalMessage from "../ui/MinimalMessage";
  import EditionColumnsToggleMixins from '../../mixins/EditionColumnsToggle'
  import ModalConfirmCloneTranslation from "../forms/ModalConfirmCloneTranslation";
  import axios from 'axios';
  import initTooltips from "../../modules/utils/tooltips";

  export default {
    name: "translation-edition",
    mixins: [EditionColumnsToggleMixins],
    components: {
      MinimalMessage,
      VisibilityToggle,
      IIIFMap,
      TranslationEditor,
	    ModalConfirmCloneTranslation
    },
    data() {
      return {
        visibility: {
          image: false,
          transcription: true,
          translation: true,
        },
	      cloneTranslationMode: false,
        transcriptionViewContent: false,
	      editStudentTranslation: false
      }
    },
    created() {
    	this.getTranscriptionViewContent()
    },
    methods: {
	    getTranscriptionViewContent() {
		    const viewUrl = this.currentUserIsAuthor ? `view/transcription` : `view/transcription/from-user/${this.author.id}`;
		    this.transcriptionViewContent = false;
		    axios.get(viewUrl).then(response => {
			    this.transcriptionViewContent = response.data;
			    setTimeout(initTooltips, 1000);
		    });
	    },
      createTranslation () {
        this.$refs.createTranslationButton.setAttribute('disabled','disabled');
        this.$store.dispatch('translation/create')
          .then(data => {
            this.$store.dispatch('translation/fetch');
          });
      },
      openCloneTranslationDialog() {
      	this.cloneTranslationMode = "clone";
      },
	    closeCloneTranslationMode() {
		    this.cloneTranslationMode = false;
	    },
	    cloneTranslation() {
		    this.$store.dispatch('translation/cloneContent')
			    .then(data => {
				    location.reload();
				    //this.closeCloneTranslationMode();
			    });
	    },
	    validateTranslation() {
		    this.$store.dispatch('translation/validate')
			    .then(data => {
				    console.log(data);
			    });
	    },
	    unvalidateTranslation() {
		    this.$store.dispatch('translation/unvalidate')
			    .then(data => {
				    console.log(data);
			    });
	    },
	    startEditingStudentTranslation() {
		    this.editStudentTranslation = true;
	    },
	    stopEditingStudentTranslation() {
		    this.editStudentTranslation = false;
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
      displayTranslationEditor () {
        return !!this.translationWithNotes && !this.translationLoading
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
      hasImage () {
        return !!this.document.images.length;
      },
      hasReferenceTranscription () {
        return !!this.referenceTranscription
      },
      hasReferenceTranslation () {
        return !!this.referenceTranslation
      },
      displayReferenceTranslation () {
        return this.hasReferenceTranslation && this.currentUserIsStudent
      },

      ...mapGetters('document', ['manifestURL']),
      ...mapState('document', ['document']),
      ...mapState('transcription', ['transcriptionContent', 'transcriptionWithNotes', 'transcriptionWithSpeechparts' ]),
      ...mapState('translation', ['translationWithNotes', 'translationLoading', 'referenceTranslation', 'translationSaved']),
      ...mapState('user', ['currentUser', 'author']),
      ...mapGetters('user', ['currentUserIsAuthor', 'currentUserIsStudent', 'currentUserIsTeacher', 'currentUserIsAdmin']),
    },
	  watch: {
		  document() {
			  this.getTranscriptionViewContent();
		  },
		  translationSaved(newval, oldval) {
			  if (newval && !oldval)
				  this.stopEditingStudentTranslation();
		  }
	  }
  }
</script>
