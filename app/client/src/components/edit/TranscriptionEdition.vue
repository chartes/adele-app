<template>
  <div id="transcription-edition" :class="isNight">

    <p class="has-text-right is-size-7" style="margin-bottom: 1em">
      <span class="tag">
        Affichage : &nbsp;&nbsp;&nbsp;
        <visibility-toggle v-if="hasImage" :action="toggle" :param="'image'" :visible="visibility.image">image</visibility-toggle>
        &nbsp;&nbsp;&nbsp;
        <visibility-toggle :action="toggle" :param="'transcription'" :visible="visibility.transcription">transcription</visibility-toggle>
      </span>
    </p>

    <div class="columns">

      <div class="column is-flex-column" v-show="visibility.image && hasImage" :class="columnSize">
        <h2 class="subtitle">Image</h2>
        <IIIFMap :manifest="manifestURL" :draw-mode="false" :display-annotations-mode="false" class="is-flex-fill" ></IIIFMap>
      </div>

      <div class="column" v-show="visibility.transcription" :class="columnSize">
        <h2 class="subtitle">Transcription

          <!-- Statut de la transcription (validée/non validée) -->
          <button v-if="currentUserIsTeacher && currentUserIsAuthor && document.validation_step_label === 'none'"
             :disabled="!transcriptionSaved"
             style="margin-right: 8px;"
             class="button is-small is-light" @click="validateTranscription">
            non validée
          </button>
          <button v-else-if="currentUserIsTeacher && currentUserIsAuthor && document.validation_step_label !== 'none'"
             style="margin-right: 8px; color: green"
             class="button is-small is-light"
             @click="unvalidateTranscription">validée</button>
          
          <!-- Éditer la transcription d'un élève-->
          <span v-if="currentUserIsTeacher && currentUser.id !== author.id">
            <button v-if="!editStudentTranscription" style="margin-left: 8px" class="button is-light is-small" @click="startEditingStudentTranscription">
              <i class="fas fa-edit" style="margin-right: 8px"></i>
              Éditer
            </button>
            <button v-else style="margin-left: 8px" class="button is-light is-small" :disabled="!transcriptionSaved">
              <i class="fas fa-edit" style="margin-right: 8px"></i>
              Éditer
            </button>
          </span>
          
          <!-- Cloner la transcription d'un élève-->
          <button v-if="currentUserIsTeacher && currentUser.id !== author.id"
                style="margin-left: 8px" class="button is-light is-small"
                @click="openCloneTranscriptionDialog"
                :disabled="!transcriptionSaved">
            <i class="fas fa-copy" style="margin-right: 8px"></i>
            Cloner
          </button>
        </h2>
  
        <!--Le bloc transcription (afficher soit la version readonly soit l'éditeur-->
        <div v-if="isReadOnly && !editStudentTranscription">
          <div v-if="!!transcriptionViewContent" v-html="transcriptionViewContent"></div>
          <div v-else>
            <minimal-message v-if="!transcriptionLoading" :body="'Aucune transcription pour le moment'"/>
          </div>
        </div>
        <transcription-editor v-else-if="displayTranscriptionEditor" :initialContent="transcriptionWithNotes"/>
        <div v-else>
          <minimal-message v-if="!transcriptionLoading" :body="'Aucune transcription pour le moment'"/>
          <p v-if="allowedToCreateTranscription"><a ref="createTranscriptionButton" class="button is-link" @click="createTranscription">Ajouter une transcription</a></p>
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
  import VisibilityToggle from "../ui/VisibilityToggle";
  import MinimalMessage from "../ui/MinimalMessage";
  import EditionColumnsToggleMixins from '../../mixins/EditionColumnsToggle'
  import ModalConfirmCloneTranscription from "../forms/ModalConfirmCloneTranscription";
  import axios from 'axios';
  import initTooltips from "../../modules/utils/tooltips";

  export default {
    name: "transcription-edition",
    mixins: [EditionColumnsToggleMixins],
    components: {
      MinimalMessage,
      VisibilityToggle,
      IIIFMap,
      TranscriptionEditor,
	    ModalConfirmCloneTranscription
    },
    data() {
      return {
        visibility: {
          image: true,
          transcription: true,
          translation: false,
        },
	      cloneTranscriptionMode: false,
	      transcriptionViewContent: false,
	      editStudentTranscription: false
      }
    },
    created() {
      this.getTranscriptionViewContent();
    },
    methods: {
    	getTranscriptionViewContent() {
		    const viewUrl = this.currentUserIsAuthor ? `view/transcription` : `view/transcription/from-user/${this.author.id}`;
		    this.transcriptionViewContent = false;
		    this.stopEditingStudentTranscription();
		    axios.get(viewUrl).then(response => {
			    this.transcriptionViewContent = response.data;
			    setTimeout(initTooltips, 1000);
		    });
      },
      createTranscription () {
        this.$refs.createTranscriptionButton.setAttribute('disabled','disabled');
        this.$store.dispatch('transcription/create')
          .then(data => {
            this.$store.dispatch('transcription/fetch');
          });
      },
      openCloneTranscriptionDialog() {
      	this.cloneTranscriptionMode = "clone";
      },
	    closeCloneTranscriptionMode() {
		    this.cloneTranscriptionMode = false;
	    },
	    cloneTranscription() {
		    this.$store.dispatch('transcription/cloneContent')
			    .then(data => {
				    location.reload();
				    //this.closeCloneTranscriptionMode();
			    });
	    },
	    validateTranscription() {
		    this.$store.dispatch('transcription/validate')
			    .then(data => {
				    console.log(data);
			    });
	    },
	    unvalidateTranscription() {
		    this.$store.dispatch('transcription/unvalidate')
			    .then(data => {
				    console.log(data);
			    });
	    },
      startEditingStudentTranscription() {
    		this.editStudentTranscription = true;
      },
	    stopEditingStudentTranscription() {
		    this.editStudentTranscription = false;
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
      isReadOnly() {
      	return !this.currentUserIsAuthor || (this.currentUserIsTeacher && this.document.validation_step_label !== 'none') || (!this.currentUserIsTeacher && this.document.validation_step_label !== 'none')
      },
      displayTranscriptionEditor () {
        return !!this.transcriptionWithNotes && !this.transcriptionLoading
      },

      allowedToCreateTranscription () {
        return (
          !this.transcriptionLoading
          &&
          this.currentUserIsAuthor
          && (this.hasReferenceTranscription || this.currentUserIsAdmin)
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
      displayReferenceTranscription () {
        return this.hasReferenceTranscription && this.currentUserIsStudent
      },
      ...mapGetters('document', ['manifestURL']),
      ...mapState('document', ['document']),
      ...mapState('transcription', ['transcriptionContent', 'transcriptionWithNotes', 'transcriptionWithSpeechparts', 'referenceTranscription', 'transcriptionLoading', 'transcriptionSaved']),
      ...mapState('user', ['currentUser', 'author']),
      ...mapGetters('user', ['currentUserIsAuthor', 'currentUserIsStudent', 'currentUserIsTeacher', 'currentUserIsAdmin']),
    },
    watch: {
    	document() {
		    this.getTranscriptionViewContent();
      },
	    author() {
    		console.warn("author changed");
		    this.getTranscriptionViewContent();
	    },
	    transcriptionSaved(newval, oldval) {
    		if (newval && !oldval)
		      this.stopEditingStudentTranscription();
	    }
    }
  }
</script>
