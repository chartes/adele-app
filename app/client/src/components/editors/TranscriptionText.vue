<template>
    <div class="editor-area">
        <div class="editor-controls" ref="controls">
            <editor-button :selected="buttons.bold" :active="editorHasFocus" :callback="simpleFormat" :format="'bold'"/>
            <editor-button :selected="buttons.italic" :active="editorHasFocus" :callback="simpleFormat" :format="'italic'"/>
            <editor-button :selected="buttons.superscript" :active="editorHasFocus" :callback="simpleFormat" :format="'superscript'"/>
            <editor-button :selected="buttons.smallcaps" :active="editorHasFocus" :callback="simpleFormat" :format="'smallcaps'"/>
            <editor-button :selected="buttons.underline" :active="editorHasFocus" :callback="simpleFormat" :format="'underline'"/>
            <editor-button :selected="buttons.del" :active="editorHasFocus" :callback="simpleFormat" :format="'del'"/>
            <editor-button :selected="buttons.expan" :active="editorHasFocus" :callback="simpleFormat" :format="'expan'"/>
            <editor-button :selected="buttons.person" :active="editorHasFocus" :callback="displayPersonForm" :format="'person'"/>
            <editor-button :selected="buttons.location" :active="editorHasFocus" :callback="displayLocationForm" :format="'location'"/>
            <editor-button :active="isNoteButtonActive" :callback="newNoteChoiceOpen" :format="'note'"/>
        </div>
        <div class="editor-container">
            <div class="quill-editor" ref="editor" spellcheck="false"></div>
            <note-actions
                v-show="selectedNoteId"
                refs="noteActions"
                :style="actionsPosition"
                :newNote="setNoteEditModeNew"
                :edit="setNoteEditModeEdit"
                :updateLink="setNoteEditModeList"
                :unlink="unlinkNote"
                :delete="setNoteEditModeDelete"/>
            <new-note-actions
                v-show="defineNewNote"
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

        <save-bar :action="() => { console.log('save')}"/>

        <!--<small><pre>{{ delta }}</pre></small>-->

    </div>
</template>

<script>

  import Quill from '../../modules/quill/AdeleQuill';
  import EditorButton from './EditorButton.vue';
  import EditorMixins from '../../mixins/EditorMixins'
  import InEditorActions from './InEditorActions';
  import NoteActions from './NoteActions';
  import NewNoteActions from './NewNoteActions';
  import NoteForm from '../forms/NoteForm';
  import NotesListForm from '../forms/NotesListForm';
  import ModalConfirmNoteDelete from '../forms/ModalConfirmNoteDelete';
  import SaveBar from "../ui/save-bar";
  import TextfieldForm from "../forms/TextfieldForm";

  export default {
    name: "transcription-text",
    props: ['initialContent'],
    mixins: [EditorMixins],
    components: {
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
        editor: null,
        rendered: null,
        delta: null,
        lastOperations: null,
        hasNote: null,
        selectedNoteId: null,
        currentNote: null,
        noteEditMode: null,
        defineNewNote: false,
        formTextfield: null,
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
        },
        actionsPositions: {
          top: 0, left: 0, right: 0, bottom: 0
        }
      }
    },
    mounted () {

      this.$refs.editor.innerHTML = this.$props.initialContent;

      this.editor = new Quill(this.$refs.editor);

      this.editor.on('selection-change', this.onSelection);
      this.editor.on('selection-change', this.onFocus);
      this.editor.on('text-change', this.onTextChange);

      this.updateContent();

    },
    methods: {

      onTextChange (delta, oldDelta, source) {
        console.log('onTranscriptionTextChange', delta, oldDelta, source)
        this.lastOperations = delta;
        this.updateContent();
        this.$store.dispatch('transcriptionChanged')
      },
      onSelection (range) {
        if (range) {
          this.setRangeBound(range);
          let formats = this.editor.getFormat(range.index, range.length);
          this.updateButtons(formats);
          if (!!formats.note) {
            this.onNoteSelected(formats.note, range);
            this.buttons.note = false;
          } else {
            this.selectedNoteId = null;
            this.buttons.note = true;
          }
        }
      },
      updateContent () {
        this.delta = this.editor.getContents().ops;

      },

      /** get and set the range bound of the selection to locate the actions bar **/
      setRangeBound (range) {
        console.log("setRangeBound", range);
        let rangeBounds = this.editor.getBounds(range);
        this.actionsPositions.left = rangeBounds.left;
        this.actionsPositions.right = rangeBounds.right;
        this.actionsPositions.bottom = rangeBounds.bottom;
      },


      /**************
       *
       * NOTES METHODS
       */

      onNoteSelected (note, range) {
        console.log("onNoteSelected", note, range.index, range.length)

        if (!range.length) return;
        this.selectedNoteId = note;

        var deltas = this.editor.getContents().ops;
        var length = deltas.length;

        /*
        const findDeltaAtIndex  = index => {
          let [leafStart, offsetStart] = this.editor.getLeaf(index);
          let searchStartIndex = this.editor.getIndex(leafStart);
          var i = 0;
          var deltaArrayIndex = 0;
          while(i < length && deltaArrayIndex < searchStartIndex) {
            let d = deltas[i];
            deltaArrayIndex += d.insert.length;
            if (d.attributes && d.attributes.note && d.attributes.note === note) {
              console.log("found", index)
            }
            i++;
          }
          console.log(i, deltas[i])
          return i;
        }
        const findFirstDelta  = deltaIndexAtStart => {
          var i = deltaIndexAtStart;
          console.log('-- findFirstDelta', i, deltas[i].attributes.note, note)
          while(i >= 0 && deltas[i].attributes && deltas[i].attributes.note === note) {
            console.log('--> findFirstDelta', i, deltas[i].attributes, note)
            i--;
          }
          console.log('firstDelta', i+1, deltas[i+1])
        }
        const findLastDelta  = deltaIndexAtStart => {
          var i = deltaIndexAtStart;
          console.log('-- findLastDelta', i, deltas[i].attributes.note, note)
          while(i < deltas.length && deltas[i].attributes && deltas[i].attributes.note === note) {
            console.log('--> findLastDelta', i, deltas[i].attributes, note)
            i++;
          }
          console.log('findLastDelta', i-1, deltas[i-1])
        }
        let deltaIndexAtStart = findDeltaAtIndex(range.index+1);
        findFirstDelta(deltaIndexAtStart);
        findLastDelta(deltaIndexAtStart);
        */

      },

      updateNoteId(newId) {
        console.log('TranscriptionText.updateNote', newId)
        this.editor.format('note', newId);
        this.selectedNoteId = newId;
        this.closeNoteEdit();
      },
      updateNote(note) {
        console.log('TranscriptionText.updateNote', note);
        this.$store.dispatch('addNote', note).then(()=>{
          console.log('DONE')
            /*
            */
            this.editor.format('note', note.id);
            this.selectedNoteId = note.id;
            this.closeNoteEdit();
        })
      },
      unlinkNote() {
        console.log('unlinkNote')
        this.editor.format('note', false);
        this.selectedNoteId = null;
      },
      deleteNote() {
        console.log('deleteNote')
        // TODO delete note
        this.editor.format('note', false);
        this.selectedNoteId = null;
        this.closeNoteEdit();
      },

      setNoteEditModeList() {
        this.noteEditMode = 'list';
        this.newNoteChoiceClose();
      },
      setNoteEditModeDelete() {
        this.noteEditMode = 'delete';
      },
      setNoteEditModeNew() {
        this.noteEditMode = 'new';
        this.newNoteChoiceClose();
      },
      setNoteEditModeEdit() {
        this.noteEditMode = 'edit';
        this.currentNote = this.$store.getters.getNoteById(this.selectedNoteId)
      },
      closeNoteEdit() {
        console.log("closeNoteEdit")
        this.noteEditMode = null;
        this.currentNote = null;
      },
      newNoteChoiceOpen() {
        this.defineNewNote = true;
      },
      newNoteChoiceClose() {
        this.defineNewNote = false;
      },


      displayTextfieldForm (formData) {
        let format = this.editor.getFormat();
        formData.value = format[formData.format];
        this.formTextfield = formData;
      },
      cancelTextfieldForm () {
        this.formTextfield = null;
      },
      submitTextfieldForm (data) {
        console.log("submitTextfieldForm", this.formTextfield, data);
        this.editor.format(this.formTextfield.format, data);
        this.cancelTextfieldForm();
        let formats = this.editor.getFormat();
        this.updateButtons(formats)
      },
      /**************
       *
       * LOCATION METHODS
       */
      displayLocationForm() {
        console.log('displayLocationForm')
        this.displayTextfieldForm ({
          format: 'location',
          attr: 'href',
          title: '<i class="fas fa-map-marker-alt"></i> Identifier un lieu',
          label: 'Nom du lieu'
        });
      },

      /**************
       *
       * PERSON METHODS
       */
      displayPersonForm() {
        this.displayTextfieldForm ({
          format: 'person',
          attr: 'href',
          title: '<i class="fas fa-user"></i> Identifier une personne',
          label: 'Nom de la personne'
        });
      }


    },

    computed: {
      /** get the actions bar position **/
      actionsPosition () {
        let top = this.actionsPositions.bottom + 5;
        let left = (this.actionsPositions.left+this.actionsPositions.right)/2;
        return `top:${top}px;left:${left}px`;
      },
      isNoteButtonActive () {
        const cond = this.editorHasFocus && this.buttons.note;
        return cond;
      }
    }
  }
</script>