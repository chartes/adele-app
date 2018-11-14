<template>
    <div class="modal is-active">
        <div class="modal-background" @click="cancel"></div>
        <div class="modal-card">
            <header class="modal-card-head" >
                <p class="modal-card-title">{{ title }}</p>
                <button class="delete" aria-label="close" @click="cancel"></button>
            </header>
            <section class="modal-card-body">
                <slot></slot>
            </section>
            <footer class="modal-card-foot">
                <button class="button" @click="cancel">Annuler</button>
                <button class="button is-danger" @click="submit">{{ submitText }}</button>
            </footer>
        </div>
    </div>
</template>

<script>

  export default {
    name: "modal-form",
    props: {
      type: {type: String},
      title: {type: String},
      submitText: {type: String},
      submit: {type: Function},
      cancel: {type: Function},
    }
  }
</script>

<style scoped>

</style>