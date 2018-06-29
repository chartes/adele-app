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

                <p><a href="#" @click.prevent="debug.content=!debug.content">Content</a></p>
                <small v-if="debug.content" v-text="transcriptionContent"></small>

                <p><a href="#" @click.prevent="debug.speechparts=!debug.speechparts">Speechparts</a></p>
                <small v-if="debug.speechparts" v-text="transcriptionWithSpeechparts"></small>

                <IIIFMap :manifest="manifestURL" :draw-mode="false" :display-annotations-mode="false" ></IIIFMap>

            </div>
            <div class="column" v-show="visibility.transcription" :class="columnSize">

                <h2 class="subtitle">Transcription</h2>

                <transcription-editor v-if="!!transcriptionWithNotes" :initialContent="transcriptionWithNotes"/>

            </div>
            <div class="column" v-show="visibility.translation" :class="columnSize">

                <h2 class="subtitle">Traduction</h2>

                <translation-editor v-if="!!translationWithNotes" :initialContent="translationWithNotes"/>

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

  export default {
    name: "transcription-edition",
    components: {
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
        debug: {
          content: false,
          notes: false,
          align: false,
          speechparts: false
        }
      }
    },
    methods: {
      toggle (what) {
        console.log('toggle', what)
        this.visibility[what] = !this.visibility[what];
      }
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
      ...mapGetters('document', ['manifestURL']),
      ...mapState('transcription', ['transcriptionContent', 'transcriptionWithNotes', 'transcriptionWithSpeechparts']),
      ...mapGetters('translation', ['translationWithNotes'])
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
    .fade-enter-active {
        transition: all 1s ease;
    }
    .fade-leave-active {
        transition: all .5s ease;
    }
    .fade-enter, .fade-leave-to {
        opacity: 0;
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