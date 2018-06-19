<template>
    <div>
        <div v-if="!error" class="iiif-map" ref="map"></div>
        <a-message v-if="error" :title="'Erreur'" :body="error" :type="'is-danger'"/>
    </div>
</template>

<script>

    import L from 'leaflet';
    import '../modules/leaflet/leaflet.draw';
    import '../modules/leaflet/Leaflet.Control.Custom';
    import axios from 'axios';
    import tileLayerIiif from '../modules/leaflet/leaflet-iiif';
    import LeafletIIIFAnnotation from '../modules/leaflet/leaflet-iiif-annotation';
    import IIIFAnnotationLoader from '../modules/leaflet/iiif-annotation-loader';
    import AMessage from './ui/AMessage';

    export default {
        components: {AMessage},
        name: "iiif-map",
        props: ['manifest', 'drawMode', 'displayAnnotationsMode'],

        data() {
            return {
                map: null,
                baseLayer: null,
                editableLayers: null,
                drawControls: null,
                error: undefined
            }
        },

        mounted() {
            axios.get(this.manifest)
                .then(response => {
                    console.log(response.data.sequences);
                    let page = response.data.sequences[0].canvases[0];
                    this.mapCreate(page);

                    this.editableLayers = new L.FeatureGroup();
                    this.map.addLayer(this.editableLayers);

                    LeafletIIIFAnnotation.initialize(this.map, this.editableLayers);
                    this.annotationsLoader = IIIFAnnotationLoader.initialize(response.data);

                    this.toggleDisplayAnnotations();
                    this.toggleDrawControls();

                })
            /*.catch( error => {
              console.log(error)
              this.error = "Impossible de charger le manifeste : <br>" +this.manifest;
            });*/
        },

        methods: {
            mapCreate(page) {

                this.map = L.map(this.$refs.map, {
                    center: [0, 0],
                    crs: L.CRS.Simple,
                    zoom: 0,
                    attributionControl: false
                });

                this.page = page;

                this.baseLayer = tileLayerIiif(this.page.images[0].resource.service['@id'] + '/info.json')
                    .addTo(this.map);

            },

            createDrawControls() {

                console.log("IIIFMap createDrawControls");

                const options = {
                    position: 'topright',
                    draw: {
                        polyline: false,
                        polygon: {
                            allowIntersection: false, // Restricts shapes to simple polygons
                            drawError: {
                                color: '#e1e100', // Color the shape will turn when intersects
                                message: '<strong>Oups !</strong> vous ne pouvez pas dessiner cette forme' // Message that will show when intersect
                            },
                            shapeOptions: {
                                color: '#bada55'
                            }
                        },
                        //circle: true, // Turns off this drawing tool
                        circlemarker: false,
                        marker: false,
                        rectangle: {
                            shapeOptions: {
                                clickable: false
                            }
                        }
                    },
                    edit: {
                        featureGroup: this.editableLayers, //REQUIRED!!
                        remove: true
                    }
                };

                let drawControls = new L.Control.Draw(options);

                L.drawLocal = {
                    draw: {
                        toolbar: {
                            actions: {
                                title: 'Annuler',
                                text: 'Annuler'
                            },
                            finish: {
                                title: 'Terminer',
                                text: 'Terminer'
                            },
                            undo: {
                                title: 'Supprimer le dernier point ajouté',
                                text: 'Supprimer le dernier point ajouté'
                            },
                            buttons: {
                                polyline: 'Ajouter un polyline',
                                polygon: 'Ajouter un polygone',
                                rectangle: 'Ajouter un rectangle',
                                circle: 'Ajouter un cercle',
                                marker: 'Ajouter un marqueur',
                                circlemarker: 'Ajouter un marqueur circulaire'
                            }
                        },
                        handlers: {
                            circle: {
                                tooltip: {
                                    start: 'Cliquer et glisser pour dessiner un cercle.'
                                },
                                radius: 'Rayon'
                            },
                            circlemarker: {
                                tooltip: {
                                    start: 'Cliquer sur la carte pour ajouter un marqueur circulaire.'
                                }
                            },
                            marker: {
                                tooltip: {
                                    start: 'Cliquer sur la carte pour ajouter un marqueur'
                                }
                            },
                            polygon: {
                                tooltip: {
                                    start: 'Cliquer pour commencer à dessiner un polygone',
                                    cont: 'Cliquer pour continuer ce polygone',
                                    end: 'Cliquer sur le premier point pour terminer ce polygone.'
                                }
                            },
                            polyline: {
                                error: '<strong>Error:</strong> shape edges cannot cross!',
                                tooltip: {
                                    start: 'Cliquer pour commencer à dessiner une ligne',
                                    cont: 'Cliquer pour continuer la ligne.',
                                    end: 'Cliquer le dernier point pour finir la ligne.'
                                }
                            },
                            rectangle: {
                                tooltip: {
                                    start: 'Cliquer et glisser pour dessiner un rectangle.'
                                }
                            },
                            simpleshape: {
                                tooltip: {
                                    end: 'Relâcher la souris pour finir de dessiner.'
                                }
                            }
                        }
                    },
                    edit: {
                        toolbar: {
                            actions: {
                                save: {
                                    title: 'Sauvegarder les changements',
                                    text: 'Sauvegarder'
                                },
                                cancel: {
                                    title: 'Annuler les changements apportés',
                                    text: 'Annnuler'
                                },
                                clearAll: {
                                    title: 'Tout supprimer',
                                    text: 'Tout supprimer'
                                }
                            },
                            buttons: {
                                edit: 'Éditer les dessins',
                                editDisabled: 'Aucun dessin à éditer',
                                remove: 'Supprimer un dessin',
                                removeDisabled: 'Aucun dessin à supprimer'
                            }
                        },
                        handlers: {
                            edit: {
                                tooltip: {
                                    text: 'Déplacer les poignées pour éditer les dessins.',
                                    subtext: 'Cliquer sur le bouton Annuler pour annuler les changements.'
                                }
                            },
                            remove: {
                                tooltip: {
                                    text: 'Cliquer sur un dessin pour le supprimer.'
                                }
                            }
                        }
                    }
                };

                /*
                    Add the saveAnnotations callbaback
                */
                let saveCallback = this.saveAnnotations;
                drawControls._toolbars.edit._save = function () {

                    saveCallback().then((response) => {
                        if (response) {
                            drawControls._toolbars.edit._activeMode.handler.save();
                            if (drawControls._toolbars.edit._activeMode) {
                                drawControls._toolbars.edit._activeMode.handler.disable();
                            }
                            console.log("annotations saving succeeded");
                        }
                        else {
                            // save failed on the server side
                            console.log("saving annotations has failed on the server side");
                        }
                    });
                };

                this.drawControls = drawControls;
            },
            addDrawControls() {

                if (!this.drawControls) {
                    this.createDrawControls();
                }

                this.map.addControl(this.drawControls);
                this.map.on(L.Draw.Event.CREATED, this.drawCreatedhandler);

            },
            removeDrawControls() {

                if (this.drawControls) this.map.removeControl(this.drawControls);
                this.map.off(L.Draw.Event.CREATED, this.drawCreatedhandler);

            },
            toggleDrawControls() {
                if (this.drawMode) {
                    this.addDrawControls();
                } else {
                    this.removeDrawControls();
                }
            },
            _saveZones(doc_id, user_id, annotations) {
                const new_annotations = [];
                for (let anno of annotations) {
                    const newAnnotation = {
                        manifest_url: this.$store.getters['document/manifestURL'],
                        img_id: this.page.images[0].resource["@id"],
                        coords: anno.region.coords,
                        content: anno.annotation_type.label === "annotation" ? anno.content : "",
                        zone_type_id: anno.annotation_type.id
                    };
                    new_annotations.push(newAnnotation);
                }
                return axios.delete(`/api/1.0/documents/${doc_id}/annotations/from-user/${user_id}`,
                    this.$store.getters['user/authHeader'])
                    .then((response) => {
                        return axios.post(`/api/1.0/documents/${doc_id}/annotations`, {"data": new_annotations},
                            this.$store.getters['user/authHeader']
                        );
                    });
            },
            _saveAlignments(doc_id, user_id, annotations) {
                return axios.delete(`/api/1.0/documents/${doc_id}/transcriptions/alignments/images/from-user/${user_id}`,
                    this.$store.getters['user/authHeader'])
                    .then((response) => {
                        let data = {
                            username: "AdminJulien",
                            manifest_url: "http://193.48.42.68/adele/iiif/manifests/man20.json",
                            img_id: "http://193.48.42.68/loris/adele/dossiers/20.jpg/full/full/0/default.jpg",
                            alignments: [
                                {
                                    "zone_id": 15,
                                    "ptr_start": 1,
                                    "ptr_end": 89
                                },
                                {
                                    "zone_id": 26,
                                    "ptr_start": 90,
                                    "ptr_end": 220
                                }
                            ]
                        };
                        for (let anno of annotations) {
                            // TODO : get alignments ptrs
                        }
                        return axios.post(`/api/1.0/documents/${doc_id}/transcriptions/alignments/images`, {"data": data},
                            this.$store.getters['user/authHeader']
                        );
                    });
            },
            saveAnnotations() {
                /*
                  - Read annotations from LeafletIIIFAnnotation
                  - call the API to post the new data (zones & alignments)
                  - eventually redraw with correctly updated data from the API side
                 */
                const annotations = LeafletIIIFAnnotation.getAnnotations();

                const doc_id = this.$store.getters['document/document'].id;
                const user_id = this.$store.getters['user/currentUser'].id;

                return this._saveZones(doc_id, user_id, annotations)
                    .then((response) => {
                        return this._saveAlignments(doc_id, user_id, annotations)
                    })
                    .then((response) => {
                        console.log("facsimile saved");
                        return true
                    });
            },
            setAnnotations() {
                console.log("set annotations");
                this.annotationsLoader.then(function () {
                    LeafletIIIFAnnotation.setAnnotations(IIIFAnnotationLoader.annotationLists);
                });
            },
            clearAnnotations() {
                console.log("clear annotations");
                this.editableLayers.clearLayers();
            },
            toggleDisplayAnnotations() {
                if (this.displayAnnotationsMode) {
                    this.setAnnotations();
                } else {
                    this.clearAnnotations();
                }
            },

            drawCreatedhandler(e) {
                console.log("IIIFMap drawCreatedhandler", e, this);
                let type = e.layerType,
                    layer = e.layer;
                this.editableLayers.addLayer(layer);
                LeafletIIIFAnnotation.resetMouseOverStyle();
            }
        },
        watch: {
            displayAnnotationsMode: function () {
                if (this.displayAnnotationsMode) {
                    this.setAnnotations();
                } else {
                    this.clearAnnotations();
                }
            },
            drawMode: function () {
                if (this.drawMode) {
                    this.setDrawControls();
                } else {
                    this.removeDrawControls();
                }
            }
        }

    }
</script>

<style scoped>
</style>
