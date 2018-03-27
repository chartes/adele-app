/*
 citations inline
 Blot : inline
 TEI : quote
 HTML5 : q
 Utilisation : commentaire
*/

import Quill from 'quill';

let Inline = Quill.import('blots/inline');

class Inlinequote extends Inline { }
Inlinequote.blotName = 'inlinequote';
Inlinequote.tagName = 'q';

export default Inlinequote;
