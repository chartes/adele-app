import Break from 'quill/blots/break';
import Embed from 'quill/blots/embed';

class LineBreak extends Break {
  length () {
    return 1
  }
  value () {
    return '\n'
  }

  insertInto(parent, ref) {
    Embed.prototype.insertInto.call(this, parent, ref)
  }
}

LineBreak.blotName = 'break';
LineBreak.tagName = 'BR';

export default LineBreak;

/*
var quill = new Quill('.editor', options);

var length = quill.getLength()
var text = quill.getText(length - 2, 2)

// Remove extraneous new lines
if (text === '\n\n') {
  quill.deleteText(quill.getLength() - 2, 2)
}
*/