/*
 Lien
 Blot : inline
 TEI : ref[@target]
 HTML5 : a[@href]
 Utilisation : commentaire
*/

// TODO

import Quill from 'quill';

let Inline = Quill.import('blots/inline');

class LinkBlot extends Inline {
  static create(url) {
    let node = super.create();
    node.setAttribute('href', url);
    node.setAttribute('target', '_blank');
    return node;
  }

  static formats(node) {
    return node.getAttribute('href');
  }
}
LinkBlot.blotName = 'link';
LinkBlot.tagName = 'a';

export default LinkBlot;
