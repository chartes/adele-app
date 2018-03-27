/*
 Gras
 TEI : hi[@rend="b"]
 HTML5 : strong
 Utilisation : transcription, traduction, commentaire, annotation facsimile
*/

import Quill from 'quill';

let Inline = Quill.import('blots/inline');

class Bold extends Inline { }
Bold.blotName = 'bold';
Bold.tagName = 'strong';


/*
class Bold extends Inline {
  static create(url) {
    let node = super.create();
    node.setAttribute('href', url);
    node.setAttribute('target', '_blank');
    return node;
  }
  /*static create(value: any): Node {
    if (this.tagName == null) {
      throw new Registry.ParchmentError('Blot definition missing tagName');
    }
    let node;
    if (Array.isArray(this.tagName)) {
      if (typeof value === 'string') {
        value = value.toUpperCase();
        if (parseInt(value).toString() === value) {
          value = parseInt(value);
        }
      }
      if (typeof value === 'number') {
        node = document.createElement(this.tagName[value - 1]);
      } else if (this.tagName.indexOf(value) > -1) {
        node = document.createElement(value);
      } else {
        node = document.createElement(this.tagName[0]);
      }
    } else {
      node = document.createElement(this.tagName);
    }
    if (this.className) {
      node.classList.add(this.className);
    }
    return node;
  }*/
/*
  static formats(node) {
    return node.getAttribute('href');
  }
}
*/
export default Bold;
