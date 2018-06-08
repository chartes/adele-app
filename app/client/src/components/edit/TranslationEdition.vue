<template>
    <div class="columns">
        <div class="column is-half">

            <div v-html="transcriptionWithNotes"/>

        </div>
        <div class="column is-half">

            <translation-editor v-if="!!translationWithNotes" :initialContent="translationWithNotes"/>

        </div>
    </div>
</template>

<script>

  import { mapGetters } from 'vuex'
  import TranslationEditor from '../editors/TranslationEditor'

  export default {
    name: "translation-edition",
    components: { TranslationEditor },
    computed: {
      ...mapGetters(['transcriptionWithNotes','translationWithNotes'])
    }
  }
</script>

<style scoped>

</style>