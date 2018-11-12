import Parchment from 'parchment';

class ColumnBreakBlot extends Parchment.Embed {
  static create(value) {
    let node = super.create();
    return node;
  }
}
ColumnBreakBlot.blotName = 'colbreak';
ColumnBreakBlot.tagName = 'cb';

export default ColumnBreakBlot;