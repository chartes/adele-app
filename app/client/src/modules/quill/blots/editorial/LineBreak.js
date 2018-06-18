import Break from 'quill/blots/break';
import Embed from 'quill/blots/embed';

/*class LineBreak extends Break {
  length () {
    return 1
  }
  value () {
    return '\n'
  }

  insertInto(parent, ref) {
    Embed.prototype.insertInto.call(this, parent, ref)
  }
}*/

import Parchment from 'parchment';

class LineBreak extends Parchment.Embed {
  static create(value) {
    let node = super.create(value);
    node.innerHTML = '<span class="br"></span><span class="segment-bullet"></span>';
    return node;
  }
  length () {
    return 1
  }

  insertInto(parent, ref) {
    Embed.prototype.insertInto.call(this, parent, ref)
  }
}

LineBreak.blotName = 'linebreak';
LineBreak.tagName = 'lb';

export default LineBreak;