<template>
  <div>
    <div class="iiif-map" ref="map"></div>
  </div>
</template>

<script>

  import L from 'leaflet';
  import '../modules/leaflet/leaflet.draw';
  import '../modules/leaflet/Leaflet.Control.Custom';
  import axios from 'axios';
  import tileLayerIiif from '../modules/leaflet/leaflet-iiif';

    export default {
      name: "iiif-map",
      props: ['manifest'],

      data() {
        return {
          map: null,
          baseLayer: null
        }
      },

      mounted() {
        console.log('IIIFMap mounted', this.$refs.map, this.manifest);
        this.map = L.map(this.$refs.map, {
          center: [0, 0],
          crs: L.CRS.Simple,
          zoom: 0
        });

        axios.get(this.manifest)
          .then( (response) => {
            let page = response.data.sequences[0].canvases[0];
            this.mapCreate(page);
          })
          .catch(function (error) {
            console.log(error);
          });

      },

      methods: {
        mapCreate (page) {
          this.baseLayer = tileLayerIiif(page.images[0].resource.service['@id'] + '/info.json')
            .addTo(this.map);

          let editableLayers = new L.FeatureGroup();
          this.map.addLayer(editableLayers);

          const options = {
            position: 'topright',
            draw: {
              polyline: false, /*{
                shapeOptions: {
                    color: '#f357a1',
                    weight: 10
                }
            },*/
              polygon: {
                allowIntersection: false, // Restricts shapes to simple polygons
                drawError: {
                  color: '#e1e100', // Color the shape will turn when intersects
                  message: '<strong>Oh snap!<strong> you can\'t draw that!' // Message that will show when intersect
                },
                shapeOptions: {
                  color: '#bada55'
                }
              },
              circle: true, // Turns off this drawing tool
              circlemarker: false,
              rectangle: {
                shapeOptions: {
                  clickable: false
                }
              }
            },
            edit: {
              featureGroup: editableLayers, //REQUIRED!!
              remove: true
            }
          };

          let drawControl = new L.Control.Draw(options);
          this.map.addControl(drawControl);

          /*L.control.custom({
            position: 'topright',
            content : '<input type="text" id="anno-input" class="btn btn-default" value="Mon Annotation"/>',
            classes : 'btn-group-vertical btn-group-sm',
            style   :
              {
                margin: '10px',
                padding: '0px 0 0 0',
                cursor: 'pointer',
              },
            datas   :
              {
                'foo': 'bar',
              },
            events:
              {
                click: function(data)
                {
                  console.log('wrapper div element clicked');
                  console.log(data);
                },
                dblclick: function(data)
                {
                  console.log('wrapper div element dblclicked');
                  console.log(data);
                },
                contextmenu: function(data)
                {
                  console.log('wrapper div element contextmenu');
                  console.log(data);
                },
              }
          })
            .addTo(this.map);
          */

          this.map.on(L.Draw.Event.CREATED, function (e) {
            var type = e.layerType,
              layer = e.layer;
            console.log(e);

            /*if (layer._tooltip) {
              $("#anno-input").attr("value", layer._tooltip.getContent());
            } else {
              $("#anno-input").attr("value", "");
            }*/

            /*layer.on('click', function(ev) {
              annotations.selected = layer;
              if (layer._tooltip) {
                $("#anno-input").attr("value", layer._tooltip.getContent());
              }
            });

            annotations.selected = layer;*/


            editableLayers.addLayer(layer);
          });
        }
      }

    }
</script>

<style scoped>
  #map {
    background: #eee;
    padding: 1em;
    border: 1px solid #ccc;
  }
</style>
