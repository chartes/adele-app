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
     //console.log("onNoteSelected", note, range.index, range.length)

      if (!range.length) return;
      this.selectedNoteId = note;

      var deltas = this.editor.getContents().ops;
      var length = deltas.length;

    },

    updateNoteId(newId) {
      this.editor.format('note', newId);
      this.selectedNoteId = newId;
      this.closeNoteEdit();
    },
    updateNote(note) {
      const isNewNote = this.noteEditMode === 'new';
      const action = isNewNote ? 'addNote' : 'updateNote';
      this.$store.dispatch(action, note).then(()=>{
        if (isNewNote) {
          this.editor.format('note', this.$store.getters.newNote.id);
          this.selectedNoteId = this.$store.getters.newNote.id;
        }
        this.closeNoteEdit();
      })
    },
    unlinkNote() {
     //console.log('unlinkNote')
      this.editor.format('note', false);
      this.selectedNoteId = null;
    },
    deleteNote() {
     //console.log('deleteNote')
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
      this.currentNote = this.$store.getters['notes/getNoteById'](this.selectedNoteId)
    },
    closeNoteEdit() {
     //console.log("closeNoteEdit")
      this.noteEditMode = null;
      this.currentNote = null;
      this.editor.focus();
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