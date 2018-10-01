<template>
    <div class="columns">

        <div class="column is-half">

            <h2 class="subtitle">Image</h2>
            <IIIFMap :manifest="manifestURL" :draw-mode="false" :display-annotations-mode="false" ></IIIFMap>

        </div>
        <div class="column is-half">

            <h2 class="subtitle">Commentaires</h2>

            <tabs tabs-style="is-toggle">

                <tab :selected="index == 0"
                     v-for="comm, index in commentaries"
                     :key="comm.type.label"
                     :name="comm.type.label"
                >
                    {{ comm.content }}
                </tab>

            </tabs>

            <hr>

            <p>Créer un nouveau commentaire :</p>
            <div>
                <a class="button" v-for="ct in missingCommentaryTypes">
                    {{ ct.label }}
                </a>
            </div>
        </div>
    </div>

</template>

<script>

    import { mapGetters, mapState } from 'vuex';
    import IIIFMap from '../IIIFMap';
    import Tabs from "../ui/Tabs";
    import Tab from "../ui/Tab";

  export default {

    name: "commentaries-edition",
    components: {Tab, Tabs, IIIFMap},

    created () {
        //this.$store.dispatch('commentaryTypes/fetch')
        //  .then (response => this.$store.dispatch('commentary/fetch'))
    },

    computed: {
      ...mapState('commentaries', ['commentaries', 'hasCommentaryTypes', 'commentaryTypes']),
      ...mapGetters('commentaries', ['missingCommentaryTypes']),
      ...mapGetters('document', ['manifestURL']),
    }

  }
</script>

<style scoped>

</style>