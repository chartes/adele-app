import Quill from 'quill';

let Embed = Quill.import('blots/embed');

class DivisionBlot extends Embed { }
DivisionBlot.blotName = 'colbreak';
DivisionBlot.tagName = 'cb';

export default DivisionBlot;


// TODO check TEI ou html5
// TODO garder ou supprimer
