/*
 Exposant
 TEI : hi[@rend="sup"]
 HTML5 : sup
 Utilisation : transcription, traduction, commentaire, annotation facsimile
*/

import Quill from 'quill';

let Inline = Quill.import('blots/inline');

class Superscript extends Inline { }
Superscript.blotName = 'superscript';
Superscript.tagName = 'sup';

export default Superscript;
