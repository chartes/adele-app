<template>
    <div class="modal is-active">
        <div class="modal-background" @click="cancel" />
        <div class="modal-card">
            <header class="modal-card-head">
                <p class="modal-card-title">Définir une nouvelle note</p>
                <button class="delete" aria-label="close" @click="cancel"></button>
            </header>
            <section class="modal-card-body">
                <div class="new-note-actions">
                    <div class="field">
                        <p class="control">
                            <a class="button is-primary" @click="modeNew">
                                <span class="icon is-small">
                                    <i class="fas fa-plus"></i>
                                </span>
                                <span>Lier à une nouvelle note</span>
                            </a>
                        </p>
                    </div>
                    <div class="field">
                        <p class="control">
                            <a class="button is-info" @click="modeLink">
                                <span class="icon is-small">
                                    <i class="fas fa-link"></i>
                                </span>
                                <span>Lier à une note existante</span>
                            </a>
                        </p>
                    </div>
                </div>
            </section>
            <footer class="modal-card-foot">
                <button class="button" @click="cancel">Annuler</button>
            </footer>
        </div>
    </div>
</template>

<script>
  export default {
    name: "new-note-actions",
    props: {
      modeNew: {
        type: Function,
        required: true
      },
      modeLink: {
        type: Function,
        required: true
      },
      cancel: {
        type: Function,
        //required: true
      }
    },
    methods: {
      chooseModeNew () {
        this.$props.modeNew();
      },
      chooseModeLink () {
        this.$props.modeLink();
      },
      chooseModeAction () {
        this.$props.chooseMode();
      },
      cancelAction () {
        this.$props.cancel();
      }
    }
  }
</script>