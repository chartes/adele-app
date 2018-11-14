<template>

    <modal-confirm
            :title="'Supprimer la note ?'"
            :submitText="'Oui je veux la supprimer'"
            :cancel="cancelAction"
            :submit="submitAction"
            class="has-text-danger"
    >
                <p><b>Danger</b></p>
                <p>Vous êtes sur le point de supprimer une note.</p>
                <p>La note sera également perdue pour la transcription de ce document, sa traduction et ses commentaires.</p>
                <p><b>Cette action ne peut pas être annulée.</b></p>

    </modal-confirm>



</template>

<script>

    import ModalConfirm from './ModalConfirm';

  export default {
    name: "modal-confirm-note-delete",
    props: ['cancel', 'submit'],
    components: {
      ModalConfirm
    },
    methods: {
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
