import Quill from 'quill';

let Block = Quill.import('blots/block');

class DivisionBlot extends Block { }
DivisionBlot.blotName = 'division';
DivisionBlot.tagName = 'div';

export default DivisionBlot;


// TODO check TEI ou html5
// TODO garder ou supprimer
