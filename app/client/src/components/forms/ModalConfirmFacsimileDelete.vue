<template>

    <modal-confirm
            :title="'Supprimer l\'alignement ?'"
            :submitText="'Oui je veux le supprimer'"
            :cancel="cancelAction"
            :submit="submitAction"
    >
        <article class="message is-danger">
            <div class="message-header">
                <p>Danger</p>
            </div>
            <div class="message-body">
                <p>Vous êtes sur le point de supprimer un alignement image/texte.</p>
                <p><strong>Cette action ne peut pas être annulée.</strong></p>

            </div>
        </article>
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
