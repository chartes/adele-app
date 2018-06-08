/*
 Segment
 Blot : embed
 Utilisation : transcription, traduction (indique le début d'un segment de traduction pour l'alignement)
*/

import Quill from 'quill';
import Parchment from 'parchment';

class SegmentBlot extends Parchment.Embed {
  static create(value) {
    let node = super.create();
    return node;
  }
}
SegmentBlot.blotName = 'segment';
SegmentBlot.tagName = 'segment';

export default SegmentBlot;

