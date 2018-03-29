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
  import AMessage from './ui/AMessage'

  export default {
    components: {AMessage},
    name: "iiif-map",
    props: ['manifest','drawMode'],
    componenst: { AMessage },

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
        .then( response => {
          let page = response.data.sequences[0].canvases[0];
          this.mapCreate(page);
        })
        .catch( error => {
          this.error = "Impossible de charger le manifeste : <br>" +this.manifest;
        });

    },

    methods: {
      mapCreate (page) {
        console.log('IIIFMap mapCreate')

        this.map = L.map(this.$refs.map, {
          center: [0, 0],
          crs: L.CRS.Simple,
          zoom: 0,
          attributionControl: false
        });

        this.baseLayer = tileLayerIiif(page.images[0].resource.service['@id'] + '/info.json')
          .addTo(this.map);

        this.editableLayers = new L.FeatureGroup();
        this.map.addLayer(this.editableLayers);

        this.toggleDrawControls();

      },
      createDrawControls () {

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

        this.drawControls = new L.Control.Draw(options);
      },
      addDrawControls () {

        if (!this.drawControls) {
          this.createDrawControls();
        }

        this.map.addControl(this.drawControls);
        this.map.on(L.Draw.Event.CREATED, this.drawCreatedhandler);

      },
      removeDrawControls () {

        if (this.drawControls) this.map.removeControl(this.drawControls);
        this.map.off(L.Draw.Event.CREATED, this.drawCreatedhandler);

      },
      toggleDrawControls () {
        if (this.drawMode) {
          this.addDrawControls();
        } else {
          this.removeDrawControls();
        }
      },
      drawCreatedhandler (e) {
        console.log("IIIFMap drawCreatedhandler", e, this);
        var type = e.layerType,
          layer = e.layer;
        this.editableLayers.addLayer(layer);
      }
    },
    watch: {
      drawMode: function () {
        if (this.drawMode) {
          this.addDrawControls();
        } else {
          this.removeDrawControls();
        }
      }
    }

  }
</script>

<style scoped>
</style>
