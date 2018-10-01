<template>
    <div id="transcription-edition" :class="isNight">

        <transition name="fade">
            <div id="joke" v-if="nbCols === 0">
                <img id="astronaut" src="/adele/static/images/astronaut.svg"/>
            </div>
        </transition>

        <p class="has-text-right is-size-7" style="margin-bottom: 1em">
            <span class="tag">
                Affichage : &nbsp;&nbsp;&nbsp;
                <visibility-toggle :action="toggle" :param="'image'" :visible="visibility.image">image</visibility-toggle>
                &nbsp;&nbsp;&nbsp;
                <visibility-toggle :action="toggle" :param="'transcription'" :visible="visibility.transcription">transcription</visibility-toggle>
                &nbsp;&nbsp;&nbsp;
                <visibility-toggle :action="toggle" :param="'translation'" :visible="visibility.translation">traduction</visibility-toggle>
            </span>
        </p>

        <div class="columns">

            <div class="column" v-show="visibility.image" :class="columnSize">

                <h2 class="subtitle">Image</h2>
                <IIIFMap :manifest="manifestURL" :draw-mode="false" :display-annotations-mode="false" ></IIIFMap>

            </div>

            <div class="column" v-show="visibility.transcription" :class="columnSize">

                <h2 class="subtitle">Transcription</h2>
                <transcription-editor v-if="displayTranscriptionEditor" :initialContent="transcriptionWithNotes"/>
                <div v-else>
                    <minimal-message v-if="!transcriptionLoading" :body="'Aucune transcription pour le moment'"/>
                    <p v-if="allowedToCreateTranscription"><a ref="createTranscriptionButton" class="button is-link" @click="createTranscription">Ajouter une transcription</a></p>
                </div>

            </div>

            <div class="column" v-show="visibility.translation" :class="columnSize">

                <h2 class="subtitle">Traduction</h2>
                <translation-editor v-if="displayTranslationEditor" :initialContent="translationWithNotes"/>
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

  export default {
    name: "transcription-edition",
    components: {
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
      toggle (what) {
        this.visibility[what] = !this.visibility[what];
      },
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
        if (this.visibility.image) size++;
        if (this.visibility.transcription) size++;
        if (this.visibility.translation) size++;
        return size;
      },
      columnSize () {
        if (this.nbCols == 2) {
          return 'is-half'
        } else if (this.nbCols == 3) {
          return 'is-one-third'
        }
        return false;
      },
      isNight () {
        return this.nbCols ? 'is-night' : '';
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
      hasReferenceTranscription () {
        return !!this.referenceTranscription
      },

      ...mapGetters('document', ['manifestURL']),
      ...mapState('transcription', ['transcriptionContent', 'transcriptionWithNotes', 'transcriptionWithSpeechparts', 'referenceTranscription', 'transcriptionLoading']),
      ...mapState('translation', ['translationWithNotes', 'translationLoading']),
      ...mapState('user', ['currentUser', 'author']),
      ...mapGetters('user', ['currentUserIsAuthor', 'currentUserIsStudent', 'currentUserIsTeacher']),
    }
  }
</script>

<style scoped>
    #joke {
        background: #000 url(/adele/static/images/solar-system.svg) no-repeat 50% 50%;
        background-size: cover;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1;
    }
    #astronaut {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%) rotate(-30deg);
        animation: astronaut-rotation 5s infinite linear;
    }
    @keyframes astronaut-rotation {
        0% {
            transform: translate(-50%, -50%) rotate(-30deg);
        }
        100% {
            transform: translate(-50%, -50%) rotate(330deg);
        }
    }
</style>