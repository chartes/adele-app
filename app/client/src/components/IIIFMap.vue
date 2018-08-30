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
                error: undefined
            }
        },

        mounted() {
            const auth_header = this.$store.getters['user/authHeader'];
            const doc_id = this.$store.getters['document/document'].id;
            const user_id =  this.$store.getters['user/currentUser'].id;
            const manifest_url = this.manifest;
            console.log("THIS", auth_header, doc_id, user_id);
            const liiiflet = new Liiiflet(
                "liiiflet-map",
                {
                    loadManifest: function() {
                        return axios.get(manifest_url, null).then(response => {
                            // unbox the JSONAPI format
                            return new Promise(resolve => resolve(response.data));}
                        );
                    },
                    loadAnnotations: function(annotation_list_url) {
                        return axios.get(annotation_list_url, auth_header).then(response => {
                            // unbox the JSONAPI format
                            return new Promise(resolve => resolve(response.data));}
                        );
                    },
                    saveAnnotations: function(annotations) {
                        return axios.delete(
                            `/adele/api/1.0/documents/${doc_id}/annotations/from-user/${user_id}`,
                            auth_header
                        ).then((response) => {
                           console.log("delete response:", response);
                           //this.handleAPIErrors(response, doc_id);
                           return axios.post(
                               `/adele/api/1.0/documents/${doc_id}/annotations`,
                               {"data": annotations},
                               auth_header
                           );
                        });
                    },
                    loadDefaultAnnotationType: function() {
                       return axios.get('/adele/api/1.0/annotation-types', null).then((response) => {
                           // unbox the JSONAPI format & find the "annotation" type
                           // (== not the transcription zone type but the free annotations)
                           for (let a of response.data.data) {
                               if (a.label === "annotation") {
                                   return new Promise(resolve => resolve(a));
                               }
                           }
                           return new Promise(resolve => resolve(response.data[0]));
                       });
                    },
                    saveAnnotationAlignments: function(annotations) {
                        //TODO
                    }
                },
                { direction: "center", className: "facsimileToolTip"},
                this.drawMode
            );


            setInterval(() => liiiflet.map.invalidateSize(true), 400);
        },

        methods: {

            handleAPIErrors(response) {
                const error_str = JSON.stringify(response.errors);
                if (response.errors) {
                    this.error = error_str;
                    throw new Error(error_str);
                }
            },


        }

    }
</script>

<style scoped>
</style>
