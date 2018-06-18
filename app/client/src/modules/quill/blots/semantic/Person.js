/*
 Personne
 Blot : inline
 TEI : persName/@ref
 HTML5 : a[@class="persName"]/@href
 Utilisation : transcription, traduction, commentaire
*/

import Quill from 'quill';

let Inline = Quill.import('blots/inline');

class PersonBlot extends Inline {

  static create(data) {
    let node = super.create();
    node.setAttribute('ref', data);
    return node;
  }

  static formats(domNode) {
    let ref = domNode.getAttribute('ref');
    return ref || true;
  }



  format(name, data) {
    if (name === 'person' && data) {
      this.domNode.setAttribute('ref', data);
    } else {
      super.format(name, data);
    }
  }

  formats() {
    let formats = super.formats();
    formats['person'] = PersonBlot.formats(this.domNode);
    return formats;
  }
}
PersonBlot.blotName = 'person';
PersonBlot.tagName = 'persName';

export default PersonBlot;

