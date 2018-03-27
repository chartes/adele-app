/*
 développement abréviation
 Blot : inline
 TEI : ex
 HTML5 : span[@class="ex"], ins ?
 Utilisation : transcription
*/

import Quill from 'quill';

let Inline = Quill.import('blots/inline');

class Abbreviation extends Inline { }
Abbreviation.blotName = 'expan';
Abbreviation.tagName = 'abbr';

export default Abbreviation;
