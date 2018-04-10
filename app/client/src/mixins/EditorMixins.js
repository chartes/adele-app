var SimpleFormatMixin = {

  data() {
    return {
      editorHasFocus: false,
      currentSelection: null
    }
  },

  methods: {
    simpleFormat(formatName) {
      let selection = this.editor.getSelection();
      let format = this.editor.getFormat(selection.index, selection.length);
      let value = !format[formatName];
      this.editor.format(formatName, value);
      let formats = this.editor.getFormat(selection.index, selection.length);
      this.updateButtons(formats);
    },

    updateButtons (formats) {
      for (let key in this.buttons) {
        this.buttons[key] = !!formats[key];
      }
    },

    onFocus () {
      console.log('onFocus', this.editor.hasFocus())
      this.editorHasFocus = this.editor.hasFocus();
    },

  }
}


export default SimpleFormatMixin;