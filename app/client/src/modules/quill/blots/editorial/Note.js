import Quill from 'quill';

let Inline = Quill.import('blots/inline');

class NoteBlot extends Inline {

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
      this.domNode.setAttribute('id', data.id);
    } else {
      super.format(name, data);
    }
  }

  formats() {
    let formats = super.formats();
    formats['note'] = NoteBlot.formats(this.domNode);
    return formats;
  }
}
NoteBlot.blotName = 'note';
NoteBlot.tagName = 'note';

export default NoteBlot;
