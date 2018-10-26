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
                    <div class="field" v-if="!notes || notes.length === 0">
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
    import {mapState} from 'vuex'
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
    mounted () {
      if (!this.notes || this.notes.length === 0) {
          console.log('=> new and first')
        this.chooseModeNew()
      }
    },
    methods: {
      chooseModeNew () {
        this.modeNew();
      },
      chooseModeLink () {
        this.modeLink();
      },
      chooseModeAction () {
        this.chooseMode();
      },
      cancelAction () {
        this.cancel();
      }
    },
    computed: {
      ...mapState('notes', ['notes'])
    }
  }
</script>