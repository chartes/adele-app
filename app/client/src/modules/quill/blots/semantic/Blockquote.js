/*
 citations bloc
 Blot : block
 TEI : quote
 HTML5 : blockquote
 Utilisation : commentaire
*/

import Quill from 'quill';

let Block = Quill.import('blots/block');

class Blockquote extends Block { }
Blockquote.blotName = 'blockquote';
Blockquote.tagName = 'blockquote';

export default Blockquote;
