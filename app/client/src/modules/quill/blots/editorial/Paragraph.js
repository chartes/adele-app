import Quill from 'quill';

let Block = Quill.import('blots/block');

class ParagraphBlot extends Block { }
ParagraphBlot.blotName = 'paragraph';
ParagraphBlot.tagName = 'p';

export default ParagraphBlot;