<template>

    <modal-form
            :title="'Choisissez une note'"
            :cancel="cancelAction"
            :submit="submitAction"
            :valid="!!selected"
    >
        <div class="NoteForm">
            <a class="notes-list-item"
               v-for="note in $store.getters.notes"
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

    import ModalForm from './ModalForm';

  export default {
    name: "note-form",
    props: ['title', 'noteId', 'cancel', 'submit'],
    components: {
      ModalForm
    },
    data() {
      console.log('NoteForm data');
      return {
        selected: null
      }
    },
    mounted () {
      console.log('NoteForm mounted', this.noteId)
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
    }
  }
</script>
