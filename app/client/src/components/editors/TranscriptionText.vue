<template>
    <div>
        <div class="editor-controls" ref="controls">

            <editor-button :selected="buttons.bold" :active="editorHasFocus" :callback="simpleFormat" :format="'bold'"/>
            <editor-button :selected="buttons.italic" :active="editorHasFocus" :callback="simpleFormat" :format="'italic'"/>
            <editor-button :selected="buttons.superscript" :active="editorHasFocus" :callback="simpleFormat" :format="'superscript'"/>
            <editor-button :selected="buttons.smallcaps" :active="editorHasFocus" :callback="simpleFormat" :format="'smallcaps'"/>
            <editor-button :selected="buttons.underline" :active="editorHasFocus" :callback="simpleFormat" :format="'underline'"/>
            <editor-button :selected="buttons.del" :active="editorHasFocus" :callback="simpleFormat" :format="'del'"/>
            <editor-button :selected="buttons.expan" :active="editorHasFocus" :callback="simpleFormat" :format="'expan'"/>
            <editor-button :selected="buttons.perso" :active="editorHasFocus" :callback="simpleFormat" :format="'person'"/>
            <editor-button :selected="buttons.location" :active="editorHasFocus" :callback="simpleFormat" :format="'location'"/>

        </div>
        <div class="quill-editor" ref="editor" v-html="'test'" spellcheck="false"></div>

    </div>
</template>

<script>

  import Quill from '../../modules/quill/AdeleQuill';
  import EditorButton from './EditorButton.vue';
  import EditorMixins from '../../mixins/EditorMixins'

  export default {
    name: "transcription-text",
    props: ['initialContent'],
    mixins: [EditorMixins],
    components: { EditorButton },
    data() {
      return {
        editor: null,
        rendered: null,
        delta: null,
        lastOperations: null,
        buttons: {
          bold: false,
          italic: false,
          superscript: false,
          smallcaps: false,
          underline: false,
          del: false,
          expan: false,
          perso: false,
          location: false,

        }
      }
    },
    mounted () {

      this.$refs.editor.innerHTML = this.$props.initialContent;

      this.editor = new Quill(this.$refs.editor);

      this.editor.on('selection-change', this.onSelection);
      this.editor.on('selection-change', this.onFocus);
      this.editor.on('text-change', this.onTextChange);


      this.updateContent();

    },
    methods: {

      onTextChange (delta, oldDelta, source) {
        console.log('onTranscriptionTextChange', delta, oldDelta, source)
        this.lastOperations = delta;
        this.updateContent();
      },
      onSelection (range, oldRange, source) {
        if (range) {
          let formats = this.editor.getFormat(range.index, range.length);
          this.updateButtons(formats)
        }
      },
      onFocus () {
        console.log('onFocus', this.editor.hasFocus())
        this.editorHasFocus = this.editor.hasFocus();
      },



      updateContent () {
        console.log("updateContent", this.editor)
        /*this.transcription.delta = this.transcription.editor.getContents().ops;
        this.transcription.rendered = this.$refs.transcriptionEd.childNodes[0].innerHTML;
        this.translation.delta = this.translation.editor.getContents().ops;
        this.speechparts.delta = this.speechparts.editor.getContents().ops;
        this.speechparts.rendered = this.$refs.speechPartsEd.childNodes[0].innerHTML;*/
      },

    }
  }
</script>

<style scoped>

</style>