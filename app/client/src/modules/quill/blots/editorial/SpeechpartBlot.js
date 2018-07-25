import Quill from 'quill';

let Inline = Quill.import('blots/inline');

class SpeechpartBlot extends Inline {
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
    if (name === 'speechpart' && data) {
      this.domNode.setAttribute('id', data);
    } else {
      super.format(name, data);
    }
  }

  formats() {
    let formats = super.formats();
    formats['speechpart'] = SpeechpartBlot.formats(this.domNode);
    return formats;
  }
}
SpeechpartBlot.blotName = 'speechpart';
SpeechpartBlot.tagName = 'speechpart';

export default SpeechpartBlot;
