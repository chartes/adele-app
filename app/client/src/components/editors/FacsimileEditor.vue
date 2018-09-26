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
                        v-show="selectedFacsimileId && this.editor.hasFocus()"
                        :style="actionsPosition"
                        refs="facsimileActions"
                        :edit="setFacsimileEditModeEdit"
                        :delete="setFacsimileEditModeDelete"/>
            </div>


            <save-bar :action="save"/>

            <facsimile-zone-list-form
                    v-if="facsimileEditMode == 'new' || facsimileEditMode == 'edit'"
                    :facsimile="currentFacsimile"
                    :facsimileId="selectedFacsimileId"
                    :submit="updateFacsimile"
                    :cancel="closeFacsimileEdit"
            />
            <modal-confirm-facsimile-delete
                    v-if="facsimileEditMode == 'delete'"
                    :cancel="closeFacsimileEdit"
                    :submit="deleteFacsimile"
            />

        </div>
    </div>
</template>

<script>

  import { mapState } from 'vuex';
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
        selectedFacsimileId: null,
        currentFacsimile: null,
        defineNewFacsimile: false,
        buttons: {
          facsimile: false,
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
          if (!!formats.facsimile) {
            this.onFacsimileSelected(formats.facsimile, range);
            this.buttons.facsimile = false;
          } else {
            this.selectedFacsimileId = null;
            this.buttons.facsimile = true;
          }
        }
      },
      onFacsimileSelected (facsimile, range) {
        if (!range.length) return;
        this.selectedFacsimileId = facsimile;
      },

      updateFacsimile(sp) {
        const isNewFacsimile = this.facsimileEditMode === 'new';
        const action = isNewFacsimile ? 'add' : 'update';
        sp.speech_part_type = this.getFacsimileTypeById(sp.type_id);
        this.editor.format('facsimile',  this.$store.state.facsimiles.facsimiles.length);
        this.$store.dispatch('facsimiles/add', sp);
        this.closeFacsimileEdit();
      },
      deleteFacsimile() {
        this.editor.format('facsimile', false);
        this.selectedFacsimileId = null;
        this.closeFacsimileEdit();
      },


      setFacsimileEditModeDelete() {
        this.facsimileEditMode = 'delete';
      },
      setFacsimileEditModeNew() {
        console.log("setFacsimileEditModeNew");
        this.facsimileEditMode = 'new';
        this.currentFacsimile = { transcription_id: this.transcription.id };
        this.newFacsimileChoiceClose();
      },
      setFacsimileEditModeEdit() {
        this.facsimileEditMode = 'edit';
        this.currentFacsimile = this.$store.state.facsimiles.facsimiles[this.selectedFacsimileId];
      },

      newFacsimileChoiceClose() {
        this.defineNewFacsimile = false;
      },

      closeFacsimileEdit() {
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
        const cond = this.editorHasFocus && this.buttons.facsimile;
        return cond;
      },
      ...mapState('transcription', ['transcription']),
      ...mapState('facsimile', ['newFacsimileZone', '']),
    }
  }
</script>