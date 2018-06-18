/*
 Lieu
 Blot : inline
 TEI : placeName/@ref
 HTML5 : a[@class="placeName"]/@href
 Utilisation : transcription, traduction, commentaire
*/

import Quill from 'quill';

let Inline = Quill.import('blots/inline');

class LocationBlot extends Inline {

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
    if (name === 'location' && data) {
      this.domNode.setAttribute('ref', data);
    } else {
      super.format(name, data);
    }
  }

  formats() {
    let formats = super.formats();
    formats['location'] = LocationBlot.formats(this.domNode);
    return formats;
  }
}
LocationBlot.blotName = 'location';
LocationBlot.tagName = 'placeName';

export default LocationBlot;

