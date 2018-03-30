import Quill from 'quill';

//import Break from 'quill/blots/break'
import BoldBlot from './blots/typo/Bold';
import ItalicBlot from './blots/typo/Italic';
import SmallCapsBlot from './blots/typo/SmallCaps';
import SuperscriptBlot from './blots/typo/Superscript';

import AbbreviationBlot from './blots/semantic/Abbreviation';
import DelBlot from './blots/semantic/Del';
import LinkBlot from './blots/semantic/Link';
import BlockquoteBlot from './blots/semantic/Blockquote';
import InlinequoteBlot from './blots/semantic/Inlinequote';

import DivisionBlot from './blots/editorial/Division';
import { LayoutCol } from './blots/editorial/Division';
import List from 'quill/formats/list';

import SpeechpartBlot from './blots/SpeechpartBlot';

let Inline = Quill.import('blots/inline');
let Block = Quill.import('blots/block');
let BlockEmbed = Quill.import('blots/block/embed');



//Quill.register(Break, true);

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

// editorial
Quill.register(DivisionBlot, true);
Quill.register(LayoutCol, true);
//Quill.register(List, true);
//Quill.register(ListItem, true);

// other
Quill.register(SpeechpartBlot, true);

export default Quill;
export {

  BoldBlot,
  ItalicBlot,
  SmallCapsBlot,

  AbbreviationBlot,
  LinkBlot,
  BlockquoteBlot,
  InlinequoteBlot,

  SpeechpartBlot
}
