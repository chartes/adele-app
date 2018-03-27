import Quill from 'quill';

let Inline = Quill.import('blots/inline');

class ItalicBlot extends Inline { }
ItalicBlot.blotName = 'italic';
ItalicBlot.tagName = 'i';

export default ItalicBlot;
