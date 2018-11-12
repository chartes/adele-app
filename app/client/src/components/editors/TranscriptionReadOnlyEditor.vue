<template>
    <div class="editor-area">

        <div class="editor-container">
            <div class="quill-editor" id="transcription-editor" ref="editor" spellcheck="false"></div>
        </div>

    </div>
</template>

<script>

  import { mapState } from 'vuex'
  import EditorMixins from '../../mixins/EditorMixins'

  export default {
    name: "transcription-read-only-editor",
    props: ['initialContent'],
    mixins: [EditorMixins],
    data() {
      return {
        storeActions: {
          changed: 'transcription/changed'
        },
        delta: null,
        buttons: {
          bold: false,
          italic: false,
          superscript: false,
          smallcaps: false,
          underline: false,
          del: false,
          expan: false,
          person: false,
          location: false,
          note: false,
          segment: false,
          paragraph: false,
        }
      }
    },
    mounted () {

      this.initEditor(this.$refs.editor, this.$props.initialContent);
      this.editor.enable(false);

    },
    beforeDestroy () {
      this.deactivateEvents();
    },
    computed: {
      ...mapState('transcription', ['transcriptionSaved']),
      ...mapState('translation', ['translationSaved']),
    }
  }
</script>