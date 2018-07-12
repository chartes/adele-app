<template>
    <div>
        <h1 class="title">Parties du discours</h1>
        <div class="editor-area">
            <div class="editor-controls" ref="controls">
                <div class="editor-controls-group">
                    <label>Structure éditoriale</label>
                    <editor-button :active="isSpeechpartButtonActive" :callback="setSpeechpartEditModeNew" :format="'speechpart'"/>
                </div>
            </div>
            <div class="editor-container">
                <div class="quill-editor" ref="editor" spellcheck="false"></div>
                <speechpart-actions
                        v-show="selectedSpeechpartId && this.editor.hasFocus()"
                        :style="actionsPosition"
                        refs="speechpartActions"
                        :edit="setSpeechpartEditModeEdit"
                        :delete="setSpeechpartEditModeDelete"/>
            </div>

            <speechpart-form
                    v-if="speechpartEditMode == 'new' || speechpartEditMode == 'edit'"
                    :speechpart="currentSpeechpart"
                    :speechpartId="selectedSpeechpartId"
                    :submit="updateSpeechpart"
                    :cancel="closeSpeechpartEdit"
            />
            <modal-confirm-note-delete
                    v-if="speechpartEditMode == 'delete'"
                    :cancel="closeSpeechpartEdit"
                    :submit="deleteSpeechpart"
            />

        </div>
    </div>
</template>

<script>

    import { mapGetters } from 'vuex';
    import EditorButton from './EditorButton.vue';
    import EditorMixins from '../../mixins/EditorMixins'
    import InEditorActions from './InEditorActions';
    import SaveBar from "../ui/save-bar";
    import SpeechpartForm from "../forms/SpeechpartForm";
    import SpeechpartActions from "../ui/speechpart-actions";

    export default {
        name: "speechparts-editor",
        props: ['initialContent'],
        mixins: [EditorMixins],
        components: {
            SpeechpartActions,
            SpeechpartForm,
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
                speechpartEditMode: null,
                selectedSpeechpartId: null,
                currentSpeechpart: null,
                defineNewSpeechpart: false,
                buttons: {
                    speechpart: false,
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
                    if (!!formats.speechpart) {
                        this.onSpeechpartSelected(formats.speechpart, range);
                        this.buttons.speechpart = false;
                    } else {
                        this.selectedSpeechpartId = null;
                        this.buttons.speechpart = true;
                    }
                }
            },
            onSpeechpartSelected (speechpart, range) {
                console.log("onSpeechpartSelected", speechpart, range.index, range.length)

                if (!range.length) return;
                this.selectedSpeechpartId = speechpart;
                console.log("onSpeechpartSelected => ", this.selectedSpeechpartId)

                var deltas = this.editor.getContents().ops;
                var length = deltas.length;

            },

            updateSpeechpart(sp) {
                const isNewSpeechpart = this.speechpartEditMode === 'new';
                const action = isNewSpeechpart ? 'add' : 'update';
                console.log('updateSpeechpart', sp, action)
                this.$store.dispatch('speechparts/'+action, sp).then(()=>{
                    if (isNewSpeechpart) {
                        console.log('editor set format', this.newSpeechpart);
                        this.editor.format('speechpart', this.newSpeechpart.id);
                        this.selectedSpeechpartId = this.newSpeechpart.id;
                    }
                    this.closeSpeechpartEdit();
                })
            },
            deleteSpeechpart() {
                console.log('deleteSpeechpart')
                this.editor.format('speechpart', false);
                this.selectedSpeechpartId = null;
                this.closeSpeechpartEdit();
            },


            setSpeechpartEditModeDelete() {
                this.speechpartEditMode = 'delete';
            },
            setSpeechpartEditModeNew() {
                this.speechpartEditMode = 'new';
                this.currentSpeechpart = { transcription_id: this.transcription.id };
                console.log("setSpeechpartEditModeNew", this.transcription.id, this.currentSpeechpart);
                this.newSpeechpartChoiceClose();
            },
            setSpeechpartEditModeEdit() {
                this.speechpartEditMode = 'edit';
                this.currentSpeechpart = this.$store.getters['speechparts/getSpeechpartById'](this.selectedSpeechpartId);
            },

            newSpeechpartChoiceOpen() {
                this.defineNewSpeechpart = true;
            },
            newSpeechpartChoiceClose() {
                this.defineNewSpeechpart = false;
            },

            closeSpeechpartEdit() {
                console.log("closeSpeechpartEdit")
                this.speechpartEditMode = null;
                this.currentSpeechpart = null;
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
                console.log(event.keyCode)
                if (event.keyCode < 37 || event.keyCode > 40) {
                    event.preventDefault();
                }
            }

        },

        computed: {
            isSpeechpartButtonActive () {
                console.log('isSpeechpartButtonActive')
                const cond = this.editorHasFocus && this.buttons.speechpart;
                return cond;
            },
            ...mapGetters('transcription', ['transcription']),
            ...mapGetters('speechparts', ['newSpeechpart'])
        }
    }
</script>