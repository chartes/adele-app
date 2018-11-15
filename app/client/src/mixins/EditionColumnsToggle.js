const EditionColumnsToggleMixins = {

  methods: {
    toggle (what) {
      this.visibility[what] = !this.visibility[what];
    },
  },
  computed: {
    nbCols () {
      let size = 0;
      if (this.visibility.image) size++;
      if (this.visibility.transcription) size++;
      if (this.visibility.translation) size++;
      return size;
    },
    columnSize () {
      if (this.nbCols == 2) {
        return 'is-half'
      } else if (this.nbCols == 3) {
        return 'is-one-third'
      }
      return false;
    },
    isNight () {
      return this.nbCols ? 'is-night' : '';
    },
  }

}

export default EditionColumnsToggleMixins;