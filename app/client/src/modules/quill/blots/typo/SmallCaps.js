/*
 Petites capitales
 TEI : hi[@rend="sc"]
 HTML5 : span[@class="sc"]
 Utilisation : transcription, traduction, commentaire
*/

import Quill from 'quill';

let Inline = Quill.import('blots/inline');

class SmallCaps extends Inline { }
SmallCaps.blotName = 'smallcaps';
SmallCaps.tagName = 'smallcaps';

export default SmallCaps;
