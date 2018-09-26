import Quill from 'quill';

let Inline = Quill.import('blots/inline');

class ZoneBlot extends Inline {

  static create(data) {
    let node = super.create();
    node.setAttribute('id', data);
    return node;
  }

  static formats(domNode) {
    let id = domNode.getAttribute('id');
    return id || true;
  }



  format(name, data) {
    if (name === 'note' && data) {
      this.domNode.setAttribute('id', data);
    } else {
      super.format(name, data);
    }
  }

  formats() {
    let formats = super.formats();
    formats['zone'] = ZoneBlot.formats(this.domNode);
    return formats;
  }
}
ZoneBlot.blotName = 'note';
ZoneBlot.tagName = 'note';

export default ZoneBlot;
