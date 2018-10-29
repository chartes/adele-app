<template>
    <div class="editor-area">
        <div class="editor-controls" ref="controls">
            <div class="editor-controls-group">
                <label>Structure éditoriale</label>
                <editor-button :selected="buttons.paragraph" :active="editorHasFocus" :callback="simpleFormat" :format="'paragraph'"/>
                <editor-button :selected="buttons.verse" :active="editorHasFocus" :callback="simpleFormat" :format="'verse'"/>
                <editor-button :active="isNoteButtonActive" :callback="newNoteChoiceOpen" :format="'note'"/>
            </div>
            <div class="editor-controls-group">
                <label>Enrichissements typographiques</label>
                <editor-button :selected="buttons.bold" :active="editorHasFocus" :callback="simpleFormat" :format="'bold'"/>
                <editor-button :selected="buttons.italic" :active="editorHasFocus" :callback="simpleFormat" :format="'italic'"/>
                <editor-button :selected="buttons.superscript" :active="editorHasFocus" :callback="simpleFormat" :format="'superscript'"/>
                <editor-button :selected="buttons.smallcaps" :active="editorHasFocus" :callback="simpleFormat" :format="'smallcaps'"/>
                <editor-button :selected="buttons.underline" :active="editorHasFocus" :callback="simpleFormat" :format="'underline'"/>
            </div>
            <div class="editor-controls-group">
                <label>Enrichissements sémantiques</label>
                <editor-button :selected="buttons.del" :active="editorHasFocus" :callback="simpleFormat" :format="'del'"/>
                <editor-button :selected="buttons.expan" :active="editorHasFocus" :callback="simpleFormat" :format="'expan'"/>
                <editor-button :selected="buttons.person" :active="editorHasFocus" :callback="displayPersonForm" :format="'person'"/>
                <editor-button :selected="buttons.location" :active="editorHasFocus" :callback="displayLocationForm" :format="'location'"/>
            </div>
        </div>
        <div class="editor-container">
            <div class="quill-editor" id="commentary-editor" ref="editor" spellcheck="false"></div>
            <note-actions
                v-show="selectedNoteId && this.editor.hasFocus()"
                refs="noteActions"
                :style="actionsPosition"
                :newNote="setNoteEditModeNew"
                :edit="setNoteEditModeEdit"
                :updateLink="setNoteEditModeList"
                :unlink="unlinkNote"
                :delete="setNoteEditModeDelete"/>
            <new-note-actions
                v-if="defineNewNote"
                :modeNew="setNoteEditModeNew"
                :modeLink="setNoteEditModeList"
                :cancel="newNoteChoiceClose"
            />
        </div>

        <notes-list-form
            v-if="noteEditMode == 'list'"
            :noteId="selectedNoteId"
            :submit="updateNoteId"
            :cancel="closeNoteEdit"
        />
        <textfield-form
            v-if="formTextfield"
            :title="formTextfield.title"
            :label="formTextfield.label"
            :value="formTextfield.value"
            :submit="submitTextfieldForm"
            :cancel="cancelTextfieldForm"/>
        <note-form
                v-if="noteEditMode == 'new' || noteEditMode == 'edit'"
                :title="noteEditMode == 'new' ? 'nouvelle note' : 'Éditer la note'"
                :note="currentNote"
                :noteId="selectedNoteId"
                :submit="updateNote"
                :cancel="closeNoteEdit"
        />
        <modal-confirm-note-delete
                v-if="noteEditMode == 'delete'"
                :cancel="closeNoteEdit"
                :submit="deleteNote"
        />
        <p>&nbsp;</p>
        <p class="has-text-centered">
            <save-button :status="status" :text="'Enregistrer les modifications'" :action="save"/>
        </p>
    </div>
</template>

<script>

  import { mapState } from 'vuex'
  import EditorButton from './EditorButton.vue';
  import EditorMixins from '../../mixins/EditorMixins'
  import EditorNotesMixins from '../../mixins/EditorNotesMixins'
  import InEditorActions from './InEditorActions';
  import NoteActions from './NoteActions';
  import NewNoteActions from './NewNoteActions';
  import NoteForm from '../forms/NoteForm';
  import NotesListForm from '../forms/NotesListForm';
  import ModalConfirmNoteDelete from '../forms/ModalConfirmNoteDelete';
  import SaveBar from "../ui/SaveBar";
  import TextfieldForm from "../forms/TextfieldForm";
  import SaveButton from '../ui/SaveButton';

  export default {
    name: "commentary-editor",
    props: ['initialContent', 'type'],
    mixins: [EditorMixins, EditorNotesMixins],
    components: {
      SaveButton,
      TextfieldForm,
      SaveBar,
      NewNoteActions,
      InEditorActions,
      EditorButton,
      ModalConfirmNoteDelete,
      NoteActions,
      NotesListForm,
      NoteForm,
    },
    data() {
      return {
        status: '',
        storeActions: {
          changed: 'commentaries/changed'
        },
        delta: null,
        buttons: {
          bold: false,
          italic: false,
          superscript: false,
          smallcaps: false,
          underline: false,
          del: false,
          expan: false,
          person: false,
          location: false,
          note: false,
          segment: false,
          paragraph: false,
        }
      }
    },
    mounted () {

      this.initEditor(this.$refs.editor, this.$props.initialContent);

    },
    beforeDestroy () {
      this.deactivateEvents();
    },

    methods: {

      onTextChange (delta, oldDelta, source) {
        console.warn('onTranscriptionTextChange', this.type)
        this.lastOperations = delta;
        if (this.editorInited) this.$store.dispatch(this.storeActions.changed,
          {type: this.type, content: this.editorContentElement.children[0].innerHTML})
      },

      updateContent () {
        this.delta = this.editor.getContents().ops;

      },

      save () {
        console.log("SAVE", this.type, this.editorContentElement.children[0].innerHTML)
        this.$store.dispatch('commentaries/save', this.type)
      }

    },

    computed: {
      ...mapState('transcription', ['transcriptionSaved']),
      ...mapState('translation', ['translationSaved']),
    }
  }
</script>