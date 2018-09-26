<template>

    <modal-form
            :title="'Choisissez une zone'"
            :cancel="cancelAction"
            :submit="submitAction"
            :valid="!!selected"
    >
        <div class="ZoneForm">
            <a class="Zones-list-item"
               v-for="zone in zones"
               :key="zone.id"
               @click="selectItem(zone.id)"
               :class="{ selected: zone.id == selected }"
            >
                <p class="content" v-html="zone.content"></p>
            </a>
        </div>
    </modal-form>



</template>

<script>

  import { mapGetters } from 'vuex'
  import ModalForm from './ModalForm';

  export default {
    name: "facsimile-zone-list-form",
    props: ['title', 'zoneId', 'cancel', 'submit'],
    components: {
      ModalForm
    },
    data() {
      return {
        selected: null
      }
    },
    mounted () {
      console.log('FacsimileZoneListForm mounted', this.noteId)
      this.selected = this.noteId
    },
    methods: {
      selectItem (noteId) {
        this.selected = noteId;
      },
      submitAction () {
        console.log("FacsimileZoneListForm.submitAction", this.selected)
        this.$props.submit(this.selected);
      },
      cancelAction () {
        this.$props.cancel();
      }
    },
    computed: {
      ...mapGetters('facsimile', ['fragments'])
    }
  }
</script>
