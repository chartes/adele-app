<template>

    <modal-confirm
            :title="'Supprimer l\'alignement ?'"
            :submitText="'Oui je veux le supprimer'"
            :cancel="cancelAction"
            :submit="submitAction"
            class="has-text-danger"
    >
        <p><b>Danger</b></p>
        <p>Vous êtes sur le point de supprimer un alignement image/texte.</p>
        <p><b>Cette action ne peut pas être annulée.</b></p>
    </modal-confirm>



</template>

<script>

    // TODO: Refactor avec ModalConfirmSpeechpartDelete

    import ModalConfirm from './ModalConfirm';

  export default {
    name: "modal-confirm-facsimile-delete",
    props: ['cancel', 'submit'],
    components: {
      ModalConfirm
    },
    methods: {
      submitAction () {
        this.$props.submit(this.selected);
      },
      cancelAction () {
        this.$props.cancel();
      }
    }
  }
</script>
