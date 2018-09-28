<template>
    <div>
        <div id="liiiflet-map" v-if="!error" class="iiif-map" ref="map"></div>
        <a-message v-if="error" :title="'Erreur'" :body="error" :type="'is-danger'"/>
    </div>
</template>

<script>

    import axios from 'axios';
    import '../../../static/js/liiiflet';

    import AMessage from './ui/AMessage';

    export default {
        components: {AMessage},
        name: "iiif-map",
        props: ['manifest', 'drawMode', 'displayAnnotationsMode'],
        data() {
            return {
                error: undefined,
                refreshInterval: null,
            }
        },

        mounted() {
            const auth_header = this.$store.getters['user/authHeader'];
            const doc_id = this.$store.getters['document/document'].id;

            const store = this.$store;
            function getAuthorId() {
                return store.getters['user/author'].id;
            }
            /*
                Comment recharger Liiiflet quand on change de user :
                - Faire une méthode Liiiflet.reset et pouvoir l'appeler depuis swapAuthor de Vue ?
            */

            const liiiflet = new Liiiflet(
                "liiiflet-map",
                {
                    loadManifest: function() {
                        const author_id =  getAuthorId();
                        const manifest_url = `/adele/api/1.0/documents/${doc_id}/manifest/from-user/${author_id}`;
                        console.log("IIIFMAP: manifest_url: ", manifest_url);
                        return axios.get(manifest_url, auth_header).then(response => {
                            //console.log("IIIFMAP: ", response);
                            // unbox the JSONAPI format
                            return new Promise(resolve => resolve(response.data.data));}
                        );
                    },
                    loadAnnotations: function(annotation_list_url) {
                        return axios.get(annotation_list_url, auth_header).then(response => {
                            return new Promise(resolve => resolve(response.data));}
                        );
                    },
                    saveAnnotations: function(annotations) {
                        /*
                            should I overwrite annotations' user_id(username?) field
                            so it is not saved under the current user id ?
                         */
                        return axios.post(
                            `/adele/api/1.0/documents/${doc_id}/annotations`,
                            {"data": annotations},
                            auth_header
                        );
                    },
                    loadDefaultAnnotationType: function() {
                       return axios.get('/adele/api/1.0/annotation-types', null).then((response) => {
                           // unbox the JSONAPI format & find the "annotation" type
                           // (== not the transcription zone type but the free annotations)
                           for (let a of response.data.data) {
                               if (a.label === "transcription") {
                                   return new Promise(resolve => resolve(a));
                               }
                           }
                           return new Promise(resolve => resolve(response.data.data[0]));
                       });
                    },
                    saveAnnotationAlignments: function(annotations) {
                        //TODO
                        console.log("SAVE ANNOTATIONS ALIGNMENTS");
                        for(let a of annotations) {
                            console.log(a);
                        }
                    }
                },
                { direction: "center", className: "facsimileToolTip"},
                this.drawMode
            );

          this.refreshInterval = setInterval(() =>  {if (liiiflet.map) liiiflet.map.invalidateSize(true)}, 400);
        },

      beforeDestroy () {
          clearInterval(this.refreshInterval);
      }

    }
</script>

<style scoped>
</style>
