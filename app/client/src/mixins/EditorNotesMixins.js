var EditorNotesMixin = {

  data() {
    return {
      selectedNoteId: null,
      currentNote: null,
      noteEditMode: null,
      defineNewNote: false,
    }
  },

  methods: {

    onNoteSelected (note, range) {
      console.log("onNoteSelected", note, range.index, range.length)

      if (!range.length) return;
      this.selectedNoteId = note;

      var deltas = this.editor.getContents().ops;
      var length = deltas.length;

    },

    updateNoteId(newId) {
      console.log('TranslationEditor.updateNote', newId)
      this.editor.format('note', newId);
      this.selectedNoteId = newId;
      this.closeNoteEdit();
    },
    updateNote(note) {
      console.log('TranslationEditor.updateNote', note);
      this.$store.dispatch('addNote', note).then(()=>{
        console.log('TranslationEditor.updateNote DONE')
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


  },

  computed: {
    isNoteButtonActive () {
      const cond = this.editorHasFocus && this.buttons.note;
      return cond;
    }
  }

}


export default EditorNotesMixin;