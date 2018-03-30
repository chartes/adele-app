<template>
    <div class="columns">
        <div class="column is-half">
            <IIIFMap :manifest="manifestURL" :draw-mode="false"></IIIFMap>
        </div>
        <div class="column is-half">
            <h1>Transcription</h1>
        </div>
    </div>
</template>

<script>

    import { mapGetters } from 'vuex'
    import IIIFMap from '../IIIFMap';

    export default {
        name: "transcription-editor",
        components: { IIIFMap },
        computed: {
            ...mapGetters(['manifestURL'])
        }
    }
</script>

<style scoped>

</style>