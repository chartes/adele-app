/*
 citations bloc
 Blot : container
 TEI : quote
 HTML5 : blockquote
 Utilisation : commentaire
*/

import Quill from 'quill';
import {ListItem} from "quill/formats/list";

const Parchment = Quill.import('parchment')
const Container = Quill.import('blots/container');
const Block = Quill.import('blots/block');
const Inline = Quill.import('blots/inline');
const Break = Quill.import('blots/break');
const TextBlot = Quill.import('blots/text');
const BlockEmbed = Quill.import('blots/block/embed');

/*
class Division extends Container {
  static create(value) {
    let tagName = 'SECTION';
    let node = super.create(tagName);
    return node;
  }

  static formats(domNode) {
    if (domNode.tagName === 'OL') return 'ordered';
    if (domNode.tagName === 'UL') {
      if (domNode.hasAttribute('data-checked')) {
        return domNode.getAttribute('data-checked') === 'true' ? 'checked' : 'unchecked';
      } else {
        return 'bullet';
      }
    }
    return undefined;
  }

  constructor(domNode) {
    super(domNode);
    const listEventHandler = (e) => {
      if (e.target.parentNode !== domNode) return;
      let format = this.statics.formats(domNode);
      let blot = Parchment.find(e.target);
      if (format === 'checked') {
        blot.format('list', 'unchecked');
      } else if(format === 'unchecked') {
        blot.format('list', 'checked');
      }
    }

    domNode.addEventListener('touchstart', listEventHandler);
    domNode.addEventListener('mousedown', listEventHandler);
  }

  format(name, value) {
    if (this.children.length > 0) {
      this.children.tail.format(name, value);
    }
  }

  formats() {
    // We don't inherit from FormatBlot
    return { [this.statics.blotName]: this.statics.formats(this.domNode) };
  }

  insertBefore(blot, ref) {
    if (blot instanceof ListItem) {
      super.insertBefore(blot, ref);
    } else {
      let index = ref == null ? this.length() : ref.offset(this);
      let after = this.split(index);
      after.parent.insertBefore(blot, after);
    }
  }

  optimize(context) {
    super.optimize(context);
    let next = this.next;
    if (next != null && next.prev === this &&
      next.statics.blotName === this.statics.blotName &&
      next.domNode.tagName === this.domNode.tagName &&
      next.domNode.getAttribute('data-checked') === this.domNode.getAttribute('data-checked')) {
      next.moveChildren(this);
      next.remove();
    }
  }

  replace(target) {
    if (target.statics.blotName !== this.statics.blotName) {
      let item = Parchment.create(this.statics.defaultChild);
      target.moveChildren(item);
      this.appendChild(item);
    }
    super.replace(target);
  }
}

Division.blotName = 'division';
//Division.scope = Parchment.Scope.BLOCK_BLOT;
Division.tagName = 'SECTION';
Division.defaultChild = 'block';
Division.allowedChildren = [Block, Division];
*/


// TODO check TEI ou html5


class LayoutCol extends Block {
  static create(value) {
    const node = super.create();
    return node;
  }

  static formats(node) {
    const rowId = node.hasAttribute('data-row-id') ? node.getAttribute('data-row-id') : null
    const colId = node.hasAttribute('data-col-id') ? node.getAttribute('data-col-id') : null

    return { rowId, colId };
  }

  optimize() {
    // wrap cols in division
    super.optimize();
    if (this.parent && this.parent.statics.blotName !== 'division') {
      const division = Parchment.create('division', this.statics.formats(this.domNode));
      this.parent.insertBefore(division, this);
      division.appendChild(this);
    }
  }
}
LayoutCol.blotName = 'layout-col';
LayoutCol.className = 'layoutCol';
LayoutCol.tagName = 'div';
LayoutCol.allowedChildren = [Inline, TextBlot, Block, BlockEmbed, Container, Break];


class Division extends Container {
  static create () {
    const node = super.create('section');
    return node
  }
}

Division.blotName = 'division';
Division.scope = Parchment.Scope.BLOCK_BLOT;
Division.tagName = 'section';
Division.className = 'div';
Division.defaultChild = 'layout-col';
Division.allowedChildren = [LayoutCol, Block, BlockEmbed, Container];


export { LayoutCol, Division as default };
