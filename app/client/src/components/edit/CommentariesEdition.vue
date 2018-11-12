<template>
  <div class="columns">

    <div class="column is-half">

      <h2 class="subtitle">Transcription</h2>
      <transcription-read-only-editor  :initialContent="transcriptionWithNotes"/>

    </div>
    <div class="column is-half">

      <h2 class="subtitle">Commentaires</h2>

      <tabs tabs-style="is-toggle">

        <tab :selected="index === 0"
             v-for="comm, index in commentaries"
             :key="comm.type"
             :name="comm.typeLabel"
        >
          <commentary-editor :initialContent="comm.content" :type="comm.type"/>
        </tab>

      </tabs>

      <hr>

      <p>Créer un nouveau commentaire :</p>
      <p>&nbsp;</p>
      <p>
        <a class="button" v-for="ct in missingCommentaryTypes" @click="createNewCommentary(ct.id, ct.label)">
          {{ ct.label }}
        </a>
      </p>
    </div>
  </div>

</template>

<script>

  import { mapGetters, mapState } from 'vuex';
  import IIIFMap from '../IIIFMap';
  import Tabs from "../ui/Tabs";
  import Tab from "../ui/Tab";
  import CommentaryEditor from '../editors/CommentaryEditor';
  import TranscriptionReadOnlyEditor from '../editors/TranscriptionReadOnlyEditor';

  export default {

    name: "commentaries-edition",
    components: {TranscriptionReadOnlyEditor, CommentaryEditor, Tab, Tabs, IIIFMap},

    created () {
      //this.$store.dispatch('commentaryTypes/fetch')
      //  .then (response => this.$store.dispatch('commentary/fetch'))
    },

    methods: {
      createNewCommentary (typeId, typeLabel) {
        console.log("createNewCommentary", typeId, typeLabel)
        this.$store.dispatch('commentaries/add', typeId);
      },
    },

    computed: {
      ...mapState('transcription', ['transcriptionWithNotes', 'referenceTranscription']),
      ...mapState('commentaries', ['commentaries', 'hasCommentaryTypes', 'commentaryTypes']),
      ...mapGetters('commentaries', ['missingCommentaryTypes']),
      ...mapGetters('document', ['manifestURL']),
    }

  }
</script>

<style scoped>

</style>