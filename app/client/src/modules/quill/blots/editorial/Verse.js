import Quill from 'quill';

let Block = Quill.import('blots/block');

class VerseBlot extends Block { }
VerseBlot.blotName = 'verse';
VerseBlot.tagName = 'l';

export default VerseBlot;