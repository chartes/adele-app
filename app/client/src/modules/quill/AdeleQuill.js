import Quill from 'quill';
import Delta from 'quill-delta';

import PlainClipboard from './PlainClipboard'

import BoldBlot from './blots/typo/Bold';
import ItalicBlot from './blots/typo/Italic';
import SmallCapsBlot from './blots/typo/SmallCaps';
import SuperscriptBlot from './blots/typo/Superscript';

import AbbreviationBlot from './blots/semantic/Abbreviation';
import DelBlot from './blots/semantic/Del';
import LinkBlot from './blots/semantic/Link';
import BlockquoteBlot from './blots/semantic/Blockquote';
import InlinequoteBlot from './blots/semantic/Inlinequote';
import PersonBlot from './blots/semantic/Person';
import CiteBlot from './blots/semantic/Cite';
import LocationBlot from './blots/semantic/Location';
import SegmentBlot from './blots/semantic/Segment';

import LineBreak from './blots/editorial/LineBreak';
import Paragraph from './blots/editorial/Paragraph';
import Verse from './blots/editorial/Verse';
import NoteBlot from './blots/editorial/Note';
import ZoneBlot from './blots/editorial/Zone';
import List from 'quill/formats/list';

import SpeechpartBlot from './blots/editorial/SpeechpartBlot';
import ColumnBreakBlot from './blots/editorial/ColumnBreak';

//import Inline from 'quill/blots/inline';

let Inline = Quill.import('blots/inline');
let Embed = Quill.import('blots/embed');

// Lower index means deeper in the DOM tree, since not found (-1) is for embeds
Inline.order = [
  'cursor', 'expan', 'inline',   // Must be lower
  'underline', 'strike', 'italic', 'bold', 'script',
  'del', 'link', 'code',
  'person', 'location', 'note', 'zone', 'speechpart',          // Must be higher
];

Quill.register('modules/clipboard', PlainClipboard, true);

Quill.register(LineBreak, true);

// typo
Quill.register(BoldBlot, true);
Quill.register(ItalicBlot, true);
Quill.register(SmallCapsBlot, true);
Quill.register(SuperscriptBlot, true);

// semantic
Quill.register(AbbreviationBlot, true);
Quill.register(DelBlot, true);
Quill.register(LinkBlot, true);
Quill.register(BlockquoteBlot, true);
Quill.register(InlinequoteBlot, true);
Quill.register(LocationBlot, true);
Quill.register(CiteBlot, true);
Quill.register(PersonBlot, true);
Quill.register(SegmentBlot, true);

// editorial
Quill.register(Paragraph, true);
Quill.register(Verse, true);
Quill.register(NoteBlot, true);
Quill.register(ZoneBlot, true);
Quill.register(ColumnBreakBlot, true);
//Quill.register(List, true);
//Quill.register(ListItem, true);

// other
Quill.register(SpeechpartBlot, true);

function lineBreakMatcher() {
  var newDelta = new Delta();
  newDelta.insert({'linebreak': ''});
  return newDelta;
}

const options = {
  modules: {

    clipboard: {
      matchers: [
        ['lb', lineBreakMatcher]
      ]
    },
    keyboard: {
      bindings: {
        linebreak: {
          key: 13,
          shiftKey: true,
          handler: function (range) {
            this.quill.insertEmbed(range.index, 'linebreak', true, 'user');
            this.quill.setSelection(range.index + 1, Quill.sources.SILENT);
          }
        }
      }
    }
  }
};


function getNewQuill (elt, opt = null) {

  let opts = opt || options;

  let quill = new Quill(elt, options);
  var length = quill.getLength()
  var text = quill.getText(length - 2, 2)

  // Remove extraneous new lines
  if (text === '\n\n') {
    quill.deleteText(quill.getLength() - 2, 2)
  }
  return quill;
}

export {

  getNewQuill,

  Inline,
  Embed,

  options,

  BoldBlot,
  ItalicBlot,
  SmallCapsBlot,

  AbbreviationBlot,
  LinkBlot,
  BlockquoteBlot,
  InlinequoteBlot,

  SpeechpartBlot,
  ZoneBlot,

  Quill as default
}
