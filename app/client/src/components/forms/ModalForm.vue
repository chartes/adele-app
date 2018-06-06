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
            </footer>
        </div>
    </div>
</template>

<script>

  export default {
    name: "modal-form",
    props: ['title', 'cancel', 'submit', 'valid', 'submitText', 'submitting'],
  }
</script>