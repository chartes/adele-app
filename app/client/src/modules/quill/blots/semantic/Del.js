/*
 texte supprimé
 Blot : inline
 TEI : del
 HTML5 : del
 Utilisation : transcription, traduction
*/

import Quill from 'quill';

let Inline = Quill.import('blots/inline');

class Del extends Inline { }
Del.blotName = 'del';
Del.tagName = 'del';

export default Del;
