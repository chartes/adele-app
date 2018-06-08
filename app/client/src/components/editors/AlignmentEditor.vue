<template>
    <div class="editor-area">
        <div class="editor-container">
            <div class="quill-editor" ref="editor" spellcheck="false"></div>
        </div>

        <save-bar :action="save"/>

    </div>
</template>

<script>

  import Quill from '../../modules/quill/AdeleQuill';
  import EditorMixins from '../../mixins/EditorMixins'
  import SaveBar from "../ui/save-bar";

  export default {
    name: "alignment-editor",
    props: ['initialContent','type'],
    mixins: [EditorMixins],
    components: {
      SaveBar,
    },
    data() {
      return {
        storeActions: {
          save: 'saveTranslation',
          changed: 'translationChanged'
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
        }
      }
    },
    mounted () {

      this.initEditor(this.$refs.editor, this.$props.initialContent);
      //this.editor.enable(false);
      this.editor.on('selection-change', this.onAlignSelection);
      this.editor.on('text-change', this.onAlignTextChange);
    },
    beforeDestroy () {
      console.log('beforeDestroy')
      this.editor.off('selection-change', this.onAlignSelection);
      this.editor.off('text-change', this.onAlignTextChange);
    },
    methods: {

      updateContent () {
        this.delta = this.editor.getContents().ops;

      },
      onAlignSelection (range) {
        if (range) {
          let beforeCharDelta = this.editor.getContents(range.index - 1, 1);
          let isAfterSegment = false;
          beforeCharDelta.ops.forEach(op => {
            if (op.insert && op.insert.segment) isAfterSegment = true;
          })
          if (range.length === 0 && isAfterSegment) {
            this.allowBackspace();
          } else {
            this.preventBackspace();
          }
        }
      },
      onAlignTextChange (delta, oldDelta, source) {
        const range = this.editor.getSelection();
        this.onAlignSelection(range);
      },
      preventBackspace () {
        document.addEventListener('keydown', this.backspacePreventHandler, true)
      },
      allowBackspace () {
        document.removeEventListener('keydown', this.backspacePreventHandler, true)

      },
      backspacePreventHandler (event) {
        if (event.keyCode === 8) {
          event.preventDefault();
        }
      }

    },

    computed: {
    }
  }
</script>