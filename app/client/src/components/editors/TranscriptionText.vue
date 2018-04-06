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
            <editor-button :selected="buttons.note" :active="editorHasFocus" :callback="null" :format="'note'"/>

        </div>
        <div class="quill-editor" ref="editor" spellcheck="false"></div>
        <small><pre>{{ delta }}</pre></small>

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
        hasNote: null,
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
          note: false,

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
          this.updateButtons(formats);
          if (!!formats.note) this.onNoteSelected(formats.note, range);
        }
      },
      onFocus () {
        console.log('onFocus', this.editor.hasFocus())
        this.editorHasFocus = this.editor.hasFocus();
      },

      onNoteSelected (note, range) {
        console.log("onNoteSelected", note, range.index, range.length)
        var deltas = this.editor.getContents().ops;
        var length = deltas.length;

        const findDeltaAtIndex  = index => {
          let [leafStart, offsetStart] = this.editor.getLeaf(index);
          let searchStartIndex = this.editor.getIndex(leafStart);
          var i = 0;
          var deltaArrayIndex = 0;
          while(i < length && deltaArrayIndex < searchStartIndex) {
            let d = deltas[i];
            deltaArrayIndex += d.insert.length;
            if (d.attributes && d.attributes.note && d.attributes.note === note) {
              console.log("found", index)
            }
            i++;
          }
          console.log(i, deltas[i])
          return i;
        }
        const findFirstDelta  = deltaIndexAtStart => {
          var i = deltaIndexAtStart;
          console.log('-- findFirstDelta', i, deltas[i].attributes.note, note)
          while(i >= 0 && deltas[i].attributes && deltas[i].attributes.note === note) {
            console.log('--> findFirstDelta', i, deltas[i].attributes, note)
            i--;
          }
          console.log('firstDelta', i+1, deltas[i+1])
        }
        const findLastDelta  = deltaIndexAtStart => {
          var i = deltaIndexAtStart;
          console.log('-- findLastDelta', i, deltas[i].attributes.note, note)
          while(i < deltas.length && deltas[i].attributes && deltas[i].attributes.note === note) {
            console.log('--> findLastDelta', i, deltas[i].attributes, note)
            i++;
          }
          console.log('findLastDelta', i-1, deltas[i-1])
        }
        let deltaIndexAtStart = findDeltaAtIndex(range.index+1);
        findFirstDelta(deltaIndexAtStart);
        findLastDelta(deltaIndexAtStart);

      },

      updateContent () {
        this.delta = this.editor.getContents().ops;

      },

    }
  }
</script>

<style scoped>

</style>