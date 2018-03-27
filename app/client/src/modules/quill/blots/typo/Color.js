import Quill from 'quill';

let Inline = Quill.import('blots/inline');

class Color extends Inline { }
Color.blotName = 'expan';
Color.tagName = 'abbr';

export default Color;
