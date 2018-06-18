<template>

    <modal-form
            :title="'Choisissez une note'"
            :cancel="cancelAction"
            :submit="submitAction"
            :valid="!!selected"
    >
        <div class="NoteForm">
            <a class="notes-list-item"
               v-for="note in notes"
               :key="note.id"
               @click="selectItem(note.id)"
               :class="{ selected: note.id == selected }"
            >
                <p class="content" v-html="note.content"></p>
            </a>
        </div>
    </modal-form>



</template>

<script>

  import { mapGetters } from 'vuex'
  import ModalForm from './ModalForm';

  export default {
    name: "note-form",
    props: ['title', 'noteId', 'cancel', 'submit'],
    components: {
      ModalForm
    },
    data() {
      console.log('NoteListForm data');
      return {
        selected: null
      }
    },
    mounted () {
      console.log('NoteListForm mounted', this.noteId)
      this.selected = this.noteId
    },
    methods: {
      selectItem (noteId) {
        this.selected = noteId;
      },
      submitAction () {
        console.log("NotesListForm.submitAction", this.selected)
        this.$props.submit(this.selected);
      },
      cancelAction () {
        this.$props.cancel();
      }
    },
    computed: {
      ...mapGetters('notes', ['notes'])
    }
  }
</script>
