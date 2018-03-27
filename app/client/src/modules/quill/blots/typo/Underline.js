/*
 Souligné
 TEI : hi[@rend="u"]
 HTML5 : u
 Utilisation : transcription, traduction, commentaire, annotation facsimile
*/

import Quill from 'quill';

let Inline = Quill.import('blots/inline');

class Underline extends Inline { }
Underline.blotName = 'underline';
Underline.tagName = 'u';

export default Underline;
