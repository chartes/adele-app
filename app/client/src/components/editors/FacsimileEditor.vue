<template>
    <div>
        <div class="editor-area">
            <div class="editor-controls" ref="controls">
                <div class="editor-controls-group">
                    <label>Structure éditoriale</label>
                    <editor-button :active="isZoneButtonActive" :callback="setFacsimileEditModeNew" :format="'zone'"/>
                </div>
            </div>
            <div class="editor-container">
                <div class="quill-editor" ref="editor" spellcheck="false"></div>
                <in-editor-actions
                        v-show="selectedZoneId && this.editor.hasFocus()"
                        :style="actionsPosition"
                        refs="facsimileActions"
                        :edit="setFacsimileEditModeEdit"
                        :delete="setFacsimileEditModeDelete"/>
            </div>


            <save-bar :action="save"/>

            <facsimile-zone-list-form
                    v-if="facsimileEditMode == 'new' || facsimileEditMode == 'edit'"
                    :facsimile="currentFacsimile"
                    :facsimileId="selectedZoneId"
                    :submit="updateAlignment"
                    :cancel="closeFragmentsListEdit"
            />
            <modal-confirm-facsimile-delete
                    v-if="facsimileEditMode == 'delete'"
                    :cancel="closeFragmentsListEdit"
                    :submit="deleteTextAlignment"
            />

        </div>
    </div>
</template>

<script>

  import { mapState, mapGetters } from 'vuex';
  import EditorButton from './EditorButton.vue';
  import EditorMixins from '../../mixins/EditorMixins'
  import InEditorActions from './InEditorActions';
  import SaveBar from "../ui/save-bar";
  import ModalConfirmFacsimileDelete from "../forms/ModalConfirmFacsimileDelete";
  import FacsimileZoneListForm from "../forms/FacsimileZoneListForm";

  export default {
    name: "facsimiles-editior",
    props: ['initialContent'],
    mixins: [EditorMixins],
    components: {
      FacsimileZoneListForm,
      ModalConfirmFacsimileDelete,
      SaveBar,
      InEditorActions,
      EditorButton,
    },
    data() {
      return {
        storeActions: {
          save: 'transcription/save',
          changed: 'transcription/changed'
        },
        delta: null,
        facsimileEditMode: null,
        selectedZoneId: null,
        currentFacsimile: null,
        defineNewFacsimile: false,
        buttons: {
          zone: false,
        }
      }
    },
    mounted () {

      this.initEditor(this.$refs.editor, this.$props.initialContent);
      this.preventKeyboard();

    },
    beforeDestroy () {
      this.allowKeyboard();
    },
    methods: {

      updateContent () {
        this.delta = this.editor.getContents().ops;

      },

      updateButtons (formats) {
        for (let key in this.buttons) {
          this.buttons[key] = !!formats[key];
        }
      },
      onSelection (range) {
        if (range) {
          this.setRangeBound(range);
          let formats = this.editor.getFormat(range.index, range.length);
          this.updateButtons(formats);
          if (!!formats.zone) {
            this.onTextAlignmentSelected(formats.zone, range);
            this.selectedZoneId = formats.zone;
            this.buttons.zone = false;
          } else {
            this.selectedZoneId = null;
            this.buttons.zone = true;
          }
        }
      },
      onTextAlignmentSelected (zone, range) {
        if (!range.length) return;
        this.selectedZoneId = zone;
      },

      updateAlignment(z) {
        const isNewZone = this.facsimileEditMode === 'new';
        const action = isNewZone ? 'add' : 'update';
        this.editor.format('zone',  z);
        this.$store.dispatch('facsimile/addAlignment', z);
        this.closeFragmentsListEdit();
      },
      deleteTextAlignment() {
        this.editor.format('zone', false);
        this.selectedZoneId = null;
        this.closeFragmentsListEdit();
      },


      setFacsimileEditModeDelete() {
        this.facsimileEditMode = 'delete';
      },
      setFacsimileEditModeNew() {
        console.log("setFacsimileEditModeNew");
        this.facsimileEditMode = 'new';
        this.currentFacsimile = { zone_id: this.selectedZoneId };
        this.newFacsimileChoiceClose();
      },
      setFacsimileEditModeEdit() {
        this.facsimileEditMode = 'edit';
        this.currentFacsimile = this.selectedZoneId;
      },

      newFacsimileChoiceClose() {
        this.defineNewFacsimile = false;
      },

      closeFragmentsListEdit() {
        this.facsimileEditMode = null;
        this.currentFacsimile = null;
        this.editor.focus();
      },

      /*
        Prevent keyboard methods
       */
      preventKeyboard () {
        document.addEventListener('keydown', this.keyboardPreventHandler, true)
      },
      allowKeyboard () {
        document.removeEventListener('keydown', this.keyboardPreventHandler, true)

      },
      keyboardPreventHandler (event) {
        if (!this.editor.hasFocus()) return;
        if (event.keyCode < 37 || event.keyCode > 40) {
          event.preventDefault();
        }
      },


    },

    computed: {
      isZoneButtonActive () {
        return this.editorHasFocus && this.buttons.zone;
      },
      ...mapState('transcription', ['transcription']),
      ...mapState('facsimile', ['newFacsimileZone', 'fragments']),
      ...mapGetters('facsimile', ['getZoneById']),
    }
  }
</script>