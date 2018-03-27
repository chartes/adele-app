import Quill from 'quill';

let Block = Quill.import('blots/block');

class HeaderBlot extends Block {
  static formats(node) {
    return HeaderBlot.tagName.indexOf(node.tagName) + 1;
  }
}
HeaderBlot.blotName = 'header';
HeaderBlot.tagName = ['H1', 'H2', 'H3', 'H4', 'H5', 'H6'];


// TODO check TEI ou html5
