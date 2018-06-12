import Quill from 'quill';
import Delta from 'quill-delta';

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
import LocationBlot from './blots/semantic/Location';
import SegmentBlot from './blots/semantic/Segment';

import LineBreak from './blots/editorial/LineBreak';
import Paragraph from './blots/editorial/Paragraph';
import Verse from './blots/editorial/Verse';
import NoteBlot from './blots/editorial/Note';
import List from 'quill/formats/list';

import SpeechpartBlot from './blots/SpeechpartBlot';

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
Quill.register(PersonBlot, true);
Quill.register(SegmentBlot, true);

// editorial
Quill.register(Paragraph, true);
Quill.register(Verse, true);
Quill.register(NoteBlot, true);
//Quill.register(List, true);
//Quill.register(ListItem, true);

// other
Quill.register(SpeechpartBlot, true);

function lineBreakMatcher() {
  var newDelta = new Delta();
  newDelta.insert({'break': ''});
  return newDelta;
}

const options = {
  modules: {

    clipboard: {
      matchers: [
        ['BR', lineBreakMatcher]
      ]
    },
    keyboard: {
      bindings: {
        linebreak: {
          key: 13,
          shiftKey: true,
          handler: function (range) {
            let currentLeaf = this.quill.getLeaf(range.index)[0]
            let nextLeaf = this.quill.getLeaf(range.index + 1)[0]

            this.quill.insertEmbed(range.index, 'break', true, 'user');

            // Insert a second break if:
            // At the end of the editor, OR next leaf has a different parent (<p>)
            if (nextLeaf === null || (currentLeaf.parent !== nextLeaf.parent)) {
              this.quill.insertEmbed(range.index, 'break', true, 'user');
            }

            // Now that we've inserted a line break, move the cursor forward
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

export default Quill;
export {

  getNewQuill,

  options,

  BoldBlot,
  ItalicBlot,
  SmallCapsBlot,

  AbbreviationBlot,
  LinkBlot,
  BlockquoteBlot,
  InlinequoteBlot,

  SpeechpartBlot
}
