import Quill from 'quill';

let Inline = Quill.import('blots/inline');

class SpeechpartBlot extends Inline {
  static create(data) {
    let node = super.create();
    node.setAttribute('id', data.id);
    node.setAttribute('type', data.type);
    node.setAttribute('note', data.note);
    ////console.log('static SpeechpartBlot.create', data);
    return node;
  }

  static formats(domNode) {
    //console.log('static SpeechpartBlot.formats', domNode);
    let id = domNode.getAttribute('id');
    let type = domNode.getAttribute('type');
    let note = domNode.getAttribute('note');
    return { id, type, note } || true;
  }

  format(name, data) {
    if (name === 'firstname' && data) {
      //console.log('SpeechpartBlot.format', name, data);
      this.domNode.setAttribute('id', data.id);
      this.domNode.setAttribute('type', data.type);
      this.domNode.setAttribute('comment', data.note);
    } else {
      super.format(name, data);
    }
  }

  formats() {
    let formats = super.formats();
    formats['speechpart'] = SpeechpartBlot.formats(this.domNode);
    //console.log('SpeechpartBlot.formats', formats);
    return formats;
  }
}
SpeechpartBlot.blotName = 'speechpart';
SpeechpartBlot.tagName = 'speechpart';

export default SpeechpartBlot;
