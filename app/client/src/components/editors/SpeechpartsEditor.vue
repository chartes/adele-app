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
                <in-editor-actions
                        class="speechpart-actions"
                        v-show="selectedSpeechpartId && this.editor.hasFocus()"
                        :style="actionsPosition"
                        refs="speechpartActions"
                        :edit="setSpeechpartEditModeEdit"
                        :delete="setSpeechpartEditModeDelete"
                        :editText="'Éditer la partie du discours'"
                        :deleteText="'Supprimer la partie du discours'"
                />
            </div>


            <save-bar :action="save"/>

            <speechpart-form
                    v-if="speechpartEditMode == 'new' || speechpartEditMode == 'edit'"
                    :speechpart="currentSpeechpart"
                    :speechpartId="selectedSpeechpartId"
                    :submit="updateSpeechpart"
                    :cancel="closeSpeechpartEdit"
            />
            <modal-confirm-speechpart-delete
                    v-if="speechpartEditMode == 'delete'"
                    :cancel="closeSpeechpartEdit"
                    :submit="deleteSpeechpart"
            />

        </div>
    </div>
</template>

<script>

  import { mapGetters } from 'vuex';
  import EditorButton from './EditorButton.vue';
  import EditorMixins from '../../mixins/EditorMixins'
  import InEditorActions from './InEditorActions';
  import SaveBar from "../ui/SaveBar";
  import SpeechpartForm from "../forms/SpeechpartForm";
  import ModalConfirmSpeechpartDelete from "../forms/ModalConfirmSpeechpartDelete";

  export default {
    name: "speechparts-editior",
    props: ['initialContent'],
    mixins: [EditorMixins],
    components: {
      ModalConfirmSpeechpartDelete,
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
      this.activateMouseOver()

    },
    beforeDestroy () {
      this.allowKeyboard();
      this.deactivateMouseOver();
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
            this.onSpeechpartSelected(formats.speechpart, range);
            this.buttons.speechpart = false;
          } else {
            this.selectedSpeechpartId = null;
            this.buttons.speechpart = true;
          }
        }
      },
      onSpeechpartSelected (speechpart, range) {
        if (!range.length) return;
        this.selectedSpeechpartId = speechpart;
      },

      updateSpeechpart(sp) {
        const isNewSpeechpart = this.speechpartEditMode === 'new';
        const action = isNewSpeechpart ? 'add' : 'update';
        sp.speech_part_type = this.getSpeechpartTypeById(sp.type_id);
        this.editor.format('speechpart',  this.$store.state.speechparts.speechparts.length);
        this.$store.dispatch('speechparts/add', sp);
        this.closeSpeechpartEdit();
      },
      deleteSpeechpart() {
        this.editor.format('speechpart', false);
        this.selectedSpeechpartId = null;
        this.closeSpeechpartEdit();
      },


      setSpeechpartEditModeDelete() {
        this.speechpartEditMode = 'delete';
      },
      setSpeechpartEditModeNew() {
        this.speechpartEditMode = 'new';
        this.currentSpeechpart = { transcription_id: this.transcription.id };
        this.newSpeechpartChoiceClose();
      },
      setSpeechpartEditModeEdit() {
        this.speechpartEditMode = 'edit';
        this.currentSpeechpart = this.$store.state.speechparts.speechparts[this.selectedSpeechpartId];
      },

      newSpeechpartChoiceClose() {
        this.defineNewSpeechpart = false;
      },

      closeSpeechpartEdit() {
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
        if (event.keyCode < 37 || event.keyCode > 40) {
          event.preventDefault();
        }
      },

      /* Speechpart mouse over */
      activateMouseOver () {
        this.$refs.editor.addEventListener('mouseover', this.mouseOverHandler)
        this.$refs.editor.addEventListener('mouseout', this.mouseOutHandler)
        //.querySelectorAll('speechpart')
      },
      deactivateMouseOver () {

        this.$refs.editor.removeEventListener('mouseover', this.mouseOverHandler)
        this.$refs.editor.removeEventListener('mouseout', this.mouseOutHandler)
      },
      mouseOverHandler (e) {
        let id = null;
        if (e.target.tagName.toLowerCase() === 'speechpart') {
          id = parseInt(e.target.getAttribute('id'));
        } else if (e.target.parentNode.tagName.toLowerCase() === 'speechpart') {
          id = parseInt(e.target.parentNode.getAttribute('id'));
        }
        if (id === null) return;
        this.$store.dispatch('speechparts/mouseover', {speechpart: this.$store.state.speechparts.speechparts[id], posY: e.clientY});

      },
      mouseOutHandler (e) {
        this.$store.dispatch('speechparts/mouseover', {speechpart: false, posY: 0});
      },

    },

    computed: {
      isSpeechpartButtonActive () {
        const cond = this.editorHasFocus && this.buttons.speechpart;
        return cond;
      },
      ...mapGetters('transcription', ['transcription']),
      ...mapGetters('speechparts', ['newSpeechpart']),
      ...mapGetters('speechpartTypes', ['getSpeechpartTypeById']),
    }
  }
</script>