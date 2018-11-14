<template>
    <div class="modal is-active">
        <div class="modal-background" @click="cancel"></div>
        <div class="modal-card">
            <header class="modal-card-head">
                <p class="modal-card-title" v-html="title"></p>
                <button class="delete" aria-label="close" @click="cancel"></button>
            </header>
            <section class="modal-card-body">
                <slot></slot>
            </section>
            <footer class="modal-card-foot">
                <button class="button is-success" :disabled="!valid || submitting" @click="submit">Valider</button>
                <button class="button" :disabled="submitting" @click="cancel">Annuler</button>
                <div style="float: right;width: 100%;text-align: right;" v-if="remove">
                    <button class="button is-danger" :disabled="submitting" @click="remove">Supprimer</button>
                </div>
            </footer>
        </div>
    </div>
</template>

<script>

  export default {
    name: "modal-form",
    props: {
      title: { type: String, default: ''},
      cancel: { type: Function, required: true},
      submit: { type: Function, required: true},
      remove: { type: Function},
      valid: { type: Boolean, required: true},
      submitText: { type: String, default: 'Soumettre'},
      submitting: { type: Boolean, default: false},
    }
  }
</script>