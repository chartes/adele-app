var SimpleFormatMixin = {

  data() {
    return {
      editorHasFocus: false
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
      console.group("Selected formats", formats);
      for (let key in this.buttons) {
        console.log(key, formats[key], !!formats[key])
        this.buttons[key] = !!formats[key];
      }
      console.groupEnd();
    },

  }
}


export default SimpleFormatMixin;