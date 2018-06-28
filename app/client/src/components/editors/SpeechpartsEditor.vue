<template>
    <div>
        <h1 class="title">Parties du discours</h1>
        <div class="editor-area">
            <div class="editor-controls" ref="controls">
                <div class="editor-controls-group">
                    <label>Structure éditoriale</label>
                    <editor-button :active="isSpeechpartButtonActive" :callback="setSpeechpartEditModeNew" :format="'speechpart'"/>
                </div>
            </div>
            <div class="editor-container">
                <div class="quill-editor" ref="editor" spellcheck="false"></div>
            </div>

            <speechpart-form
                    v-if="speechpartEditMode == 'new' || speechpartEditMode == 'edit'"
                    :note="currentSpeechpart"
                    :noteId="selectedSpeechpartId"
                    :submit="updateSpeechpart"
                    :cancel="closeSpeechpartEdit"
            />

        </div>
    </div>
</template>

<script>

  import EditorButton from './EditorButton.vue';
  import EditorMixins from '../../mixins/EditorMixins'
  import InEditorActions from './InEditorActions';
  import SaveBar from "../ui/save-bar";
  import SpeechpartForm from "../forms/SpeechpartForm";

  export default {
    name: "speechparts-editor",
    props: ['initialContent'],
    mixins: [EditorMixins],
    components: {
      SpeechpartForm,
      SaveBar,
      InEditorActions,
      EditorButton,
    },
    data() {
      return {
        storeActions: {
          save: 'transcription/save',
          changed: 'transcription/changed'
        },
        delta: null,
        speechpartEditMode: null,
        selectedSpeechpartId: null,
        currentSpeechpart: null,
        defineNewSpeechpart: false,
        buttons: {
          speechpart: false,
        }
      }
    },
    mounted () {

      this.initEditor(this.$refs.editor, this.$props.initialContent);
      this.preventKeyboard();

    },
    beforeDestroy () {
      this.allowKeyboard();
    },
    methods: {

      updateContent () {
        this.delta = this.editor.getContents().ops;

      },

      updateButtons (formats) {
        for (let key in this.buttons) {
          this.buttons[key] = !!formats[key];
        }
      },
      onSelection (range) {
        if (range) {
          this.setRangeBound(range);
          let formats = this.editor.getFormat(range.index, range.length);
          this.updateButtons(formats);
          if (!!formats.speechpart) {
            this.buttons.speechpart = false;
          } else {
            this.selectedSpeechpartId = null;
            this.buttons.speechpart = true;
          }
        }
      },

      updateSpeechpart(note) {
        const isNewSpeechpart = this.noteEditMode === 'new';
        const action = isNewSpeechpart ? 'addSpeechpart' : 'updateSpeechpart';
        this.$store.dispatch(action, note).then(()=>{
          if (isNewSpeechpart) {
            this.editor.format('note', this.$store.getters.newSpeechpart.id);
            this.selectedSpeechpartId = this.$store.getters.newSpeechpart.id;
          }
          this.closeSpeechpartEdit();
        })
      },

      setSpeechpartEditModeDelete() {
        this.speechpartEditMode = 'delete';
      },
      setSpeechpartEditModeNew() {
        this.speechpartEditMode = 'new';
        this.newSpeechpartChoiceClose();
      },
      setSpeechpartEditModeEdit() {
        this.speechpartEditMode = 'edit';
        this.currentSpeechpart = this.$store.getters.getSpeechpartById(this.selectedSpeechpartId)
      },

      newSpeechpartChoiceOpen() {
        this.defineNewSpeechpart = true;
      },
      newSpeechpartChoiceClose() {
        this.defineNewSpeechpart = false;
      },

      closeSpeechpartEdit() {
        console.log("closeSpeechpartEdit")
        this.speechpartEditMode = null;
        this.currentSpeechpart = null;
        this.editor.focus();
      },

      /*
        Prevent keyboard methods
       */
      preventKeyboard () {
        document.addEventListener('keydown', this.keyboardPreventHandler, true)
      },
      allowKeyboard () {
        document.removeEventListener('keydown', this.keyboardPreventHandler, true)

      },
      keyboardPreventHandler (event) {
        if (!this.editor.hasFocus()) return;
        console.log(event.keyCode)
        if (event.keyCode < 37 || event.keyCode > 40) {
          console.log('prevent')
          event.preventDefault();
        }
      }

    },

    computed: {
      isSpeechpartButtonActive () {
        console.log('isSpeechpartButtonActive')
        const cond = this.editorHasFocus && this.buttons.speechpart;
        return cond;
      }
    }
  }
</script>