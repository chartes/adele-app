<template>
    <div>
        <div id="liiiflet-map" v-if="!error" class="iiif-map" ref="map"></div>
        <a-message v-if="error" :title="'Erreur'" :body="error" :type="'is-danger'"/>
    </div>
</template>

<script>

  import axios from 'axios';
  import {mapGetters, mapState} from 'vuex';
  import '../../../static/js/liiiflet';

  import AMessage from './ui/AMessage';

  export default {
    components: {AMessage},
    name: "iiif-map",
    props: ['manifest', 'drawMode', 'displayAnnotationsMode'],
    data() {
      return {
        liiiflet: null,
        error: undefined,
        refreshInterval: null,
      }
    },

    mounted() {
      /*
          Comment recharger Liiiflet quand on change de user :
          - Faire une méthode Liiiflet.reset et pouvoir l'appeler depuis swapAuthor de Vue ?
      */

      this.liiiflet = new Liiiflet(
        "liiiflet-map",
        {
          loadManifest: this.loadManifest,
          loadAnnotations: this.loadAnnotations,
          saveAnnotations: this.saveAnnotations,
          onDeleteAnnotation: this.onDeleteAnnotation,
          getAnnotationId: this.getAnnotationId,
          loadDefaultAnnotationType: this.loadDefaultAnnotationType,
          saveAnnotationAlignments: this.saveAnnotationAlignments
        },
        { direction: "center", className: "facsimileToolTip"},
        this.drawMode,
        {zoomControl: true}
      );

      this.refreshInterval = setInterval(() =>  {
        if (this.liiiflet && this.liiiflet.map) this.liiiflet.map.invalidateSize(true)
      }, 400);
    },

    methods: {
      loadManifest() {
        //const author_id =  getAuthorId();
        const manifest_url = `/adele/api/1.0/documents/${this.document.id}/manifest/from-user/${this.$store.state.user.author.id}`;
        console.log("IIIFMAP: manifest_url: ", manifest_url);
        return axios.get(manifest_url, this.authHeader).then(response => {
          //console.log("IIIFMAP: ", response);
          // unbox the JSONAPI format
          return new Promise(resolve => resolve(response.data.data))
        })
      },
      loadAnnotations (annotation_list_url) {
        return axios.get(annotation_list_url, this.authHeader).then(response => {
          return new Promise(resolve => resolve(response.data))
        })
      },
      saveAnnotations: function(canvas_name, annotations) {
        return  axios.post(`/adele/api/1.0/documents/${this.document.id}/annotations/${canvas_name}`,
          {"data": annotations},
          this.authHeader)
      },
      onDeleteAnnotation (zone_id) {
        console.log("propagate deletion of image zone: ", zone_id);
      },
      getAnnotationId (annotation) {
        let zone_id
        try {
          zone_id = annotation.resource["@id"].split("/")
          zone_id = zone_id[zone_id.length - 3]
        } catch(e) {
          zone_id = null
        }
        return zone_id
      },
      loadDefaultAnnotationType () {
        return axios.get('/adele/api/1.0/annotation-types', null).then(response => {
          console.log('loadDefaultAnnotationType', response)
          // unbox the JSONAPI format & find a default annotation type
          for (let a of response.data.data) {
            if (a.label === "transcription") {
              return new Promise(resolve => resolve(a));
            }
          }
          return new Promise(resolve => resolve(response.data.data[0]));
        });
      },
      saveAnnotationAlignments: function(annotations) {
        console.log("SAVE ANNOTATIONS ALIGNMENTS");
        this.$store.dispatch("transcription/save");

      }

    },
    watch: {
      savingStatus (newStatus, oldStatus) {
        console.info("transcription status", oldStatus, '=>', newStatus)
        if (oldStatus === 'saving' && newStatus === 'uptodate') {
          this.liiiflet.refresh()
        }
      }
    },

    computed: {

      ...mapGetters('user', ['authHeader']),
      ...mapState('document', ['document']),
      ...mapState('transcription', ['savingStatus']),

    },

    beforeDestroy () {
      clearInterval(this.refreshInterval);
    }

}
</script>