const parser = new DOMParser();
var xmlSerializer = new XMLSerializer();

const MAPPING_QUILL_TO_TEI = {
  'h1': { tag: 'head', attr: 'type', attrValue:'h1'},
  'h2': { tag: 'head', attr: 'type', attrValue:'h2'},
  'h3': { tag: 'head', attr: 'type', attrValue:'h3'},
  'h4': { tag: 'head', attr: 'type', attrValue:'h4'},
  'h5': { tag: 'head', attr: 'type', attrValue:'h5'},
  'h6': { tag: 'head', attr: 'type', attrValue:'h6'},
  'section': { tag: 'div'},
  'ul': { tag: 'list'},
  'li': { tag: 'item'},
  'br': { tag: 'lb'},
  'i': { tag: 'hi', attr: 'rend', attrValue:'i'},
  'strong': { tag: 'hi', attr: 'rend', attrValue:'b'},
  'sup': { tag: 'hi', attr: 'rend', attrValue:'sup'},
  'smallcaps': { tag: 'hi', attr: 'rend', attrValue:'sc'},
  'u': { tag: 'hi', attr: 'rend', attrValue:'u'},
  // TODO couleur	hi[@style="$color"]	?
  'blockquote': { tag: 'quote', attr: 'rend', attrValue:'block'},
  'q': { tag: 'quote', attr: 'rend', attrValue:'inline'},
  'cite': { tag: 'title'},
  'persname': { tag: 'persName'},
  'placeName': { tag: 'placeName'},
};
const MAPPING_TEI_TO_QUILL = {
  'head': {
    mapping: {
      mapping_type: 'attr', // definit la condition en fonction d'un attribut
      mapping_attr: 'type', // en fonction de l' attribut "rend"
      'type': {
        'h1': {tag: 'h1', removeAttr: 'type'},
        'h2': {tag: 'h2', removeAttr: 'type'},
        'h3': {tag: 'h3', removeAttr: 'type'},
        'h4': {tag: 'h4', removeAttr: 'type'},
        'h5': {tag: 'h5', removeAttr: 'type'},
        'h6': {tag: 'h6', removeAttr: 'type'},
      }
    },
  },
  'div': { tag: 'section'},
  'list': { tag: 'ul'},
  'item': { tag: 'li'},
  'lb': { tag: 'br'},
  'hi': {
    mapping: {
      mapping_type: 'attr', // definit la condition en fonction d'un attribut
      mapping_attr: 'rend,style',
      'rend': {// en fonction de l' attribut "rend"
        'i': {tag: 'i', removeAttr: 'rend'},
        'b': {tag: 'strong', removeAttr: 'rend'},
        'sup': {tag: 'sup', removeAttr: 'rend'},
        'sc': {tag: 'smallcaps', removeAttr: 'rend'},
        'u': {tag: 'u', removeAttr: 'rend'},
      },
      'style': { tag: 'span'}
    }
  },
  'quote': {
    mapping: {
      mapping_type: 'parent', // definit la condition en fonction du parent
      'parent':{
        'doc': {tag: 'blockquote', removeAttr: 'rend'},
        '$default': { tag: 'q'}
      },
    }
  },
  'title': { tag: 'title'},
  'persName': { tag: 'persname'},
  'placeName': { tag: 'placename'},
};

const testQuillToTEI = `<h1>Titre niveau 1</h1>
    <h2>Titre niveau 2</h2>
    <h3>Titre niveau 3</h3>
    <h4>Titre niveau 4</h4>
    <h5>Titre niveau 5</h5>
    <h6>Titre niveau 6</h6>
    <section>Section</section>
    <ul>
      <li>item 1</li>
      <li>item 2</li>
      <li>item 3</li>
    </ul>
    <br/><br />
    <p><i>texte en italique et <strong>gras</strong></i> mais aussi <u>souligné</u> 3<sup>e</sup> <smallcaps>smallcaps</smallcaps></p>
    <blockquote>ceci est un blockquote</blockquote>
    <p>Ce paragraphe comprend une <q>citation</q> une <persname ref="la personne">personne</persname> et un <placename ref="le lieu">lieu</placename></p>`;
const testTEIToQuill = `<head type="h1">Titre niveau 1</head>
    <head type="h2">Titre niveau 2</head>
    <head type="h3">Titre niveau 3</head>
    <head type="h4">Titre niveau 4</head>
    <head type="h5">Titre niveau 5</head>
    <head type="h6">Titre niveau 6</head>
    <div>Section</div>
    <list>
      <item>item 1</item>
      <item>item 2</item>
      <item>item 3</item>
    </list>
    <lb></lb><lb></lb>
    <p><span style="color:#f00">text en couleur</span></p>
    <p><hi rend="i">texte en italique et <hi rend="b">gras</hi></hi> mais aussi <hi rend="u">souligné</hi> 3<hi rend="sup">e</hi> <hi rend="sc">smallcaps</hi></p>
    <quote rend="block">ceci est un blockquote</quote>
    <p>Ce paragraphe comprend une <quote rend="inline">citation</quote> une <persname ref="la personne">personne</persname> et un <placename ref="le lieu">lieu</placename></p>`;
const teiToQuill = (teiString) => {

  const xmlDoc = parser.parseFromString('<doc>'+teiString+'</doc>',"text/xml");

  let newDoc;
  newDoc = recurChange(xmlDoc.documentElement, MAPPING_TEI_TO_QUILL);
  let str = xmlSerializer.serializeToString(newDoc);
  str = str.replace(/<\/?doc([^>]*)>/gi, '');
  str = str.replace(/<(\/?)persname( ref="[^"]*")?>/gmi, '<$1persName$2>');
  str = str.replace(/<(\/?)placename( ref="[^"]*")?>/gmi, '<$1placeName$2>');
  return str;

}

const quillToTEI = quillString => {

  const xmlDoc = parser.parseFromString('<doc>'+quillString+'</doc>',"text/xml");

  let newDoc;
  newDoc = recurChange(xmlDoc.documentElement, MAPPING_QUILL_TO_TEI);
  let str = xmlSerializer.serializeToString(newDoc);
  return str.replace(/<\/?doc([^>]*)>/gi, '');

};

console.log('quillToTEI', quillToTEI(testQuillToTEI));
console.log('teiToQuill', teiToQuill(testTEIToQuill));

function changeElementName (elt, name) {
  var newElt = document.createElement(name);
  newElt.innerHTML = elt.innerHTML;
  copyEltContent(elt, newElt);
  elt.parentNode.replaceChild(newElt, elt);
}
function copyEltContent (sourceElt, destElt) {
  destElt.innerHTML = sourceElt.innerHTML;
}
function copyEltAttributes (sourceElt, destElt) {
  if (sourceElt.hasAttributes()) {
    var attrs = sourceElt.attributes;
    for(var i = attrs.length - 1; i >= 0; i--) {
      destElt.setAttribute(attrs[i].name, attrs[i].value);
    }
  }
}
function recurChange (node, mapping) {
  let newNode;
  if (node.nodeType == 3) {
    return document.createTextNode(node.nodeValue);
  }
  let conversionProps = mapping[node.nodeName];
  if (conversionProps) {
    let replaceTagWith = conversionProps.tag;
    let attrToAdd = conversionProps.attr;
    let attrValue = conversionProps.attrValue || '';

    if (conversionProps.mapping) {

      let mapping = conversionProps.mapping;
      let mappingType = mapping.mapping_type;

      if (mappingType === 'attr') {

        let attrs = mapping.mapping_attr.split(',');
        attrs.forEach(attrName => {
          let attrValue = node.getAttribute(attrName);
          if (attrValue) {
            let conv = mapping[attrName][attrValue];
            replaceTagWith = conv.tag;
            if (conv.removeAttr) {
              node.removeAttribute(conv.removeAttr);
            }
          }
        });

      } else if (mappingType === 'parent') {

        let parentTag = node.parentNode.tagName;
        let conv = mapping.parent[parentTag] ? mapping.parent[parentTag] : mapping.parent['$default'];
        replaceTagWith = conv.tag;
        if (conv.removeAttr) {
          node.removeAttribute(conv.removeAttr);
        }
      }


    }

    newNode = document.createElement(replaceTagWith);
    if (attrToAdd) newNode.setAttribute(attrToAdd, attrValue);

  } else {
    newNode = document.createElement(node.nodeName);
  }
  copyEltAttributes(node, newNode);
  if (node.hasChildNodes()) {
    for (let i = 0; i < node.childNodes.length ;i++) {
      var child = node.childNodes[i];
      newNode.appendChild(recurChange(child, mapping));
    }
  }
  return newNode;
}

String.prototype.insert = function (index, string) {
  if (index > 0)
    return this.substring(0, index) + string + this.substring(index, this.length);
  else
    return string + this;
};

const insertNotes = (text, notes) => {
  let result = text;
  let indexCorrection = 0;
  notes.forEach(note => {
    let opening = `<note id="${note.id}">`;
    let closing = '</note>'
    result = result.insert(note.ptr_start + indexCorrection, opening);
    indexCorrection += opening.length;
    result = result.insert(note.ptr_end + indexCorrection, closing);
    indexCorrection += closing.length;
  })
  return result;
};
const stripNotes  = text => text.replace(/<\/?note( id="\d+")?>/gmi, '');
const stripSegments  = text => text.replace(/<\/?segment>/gmi, '');

const computeNotesPointers  = (htmlWithNotes) => {

  const regexpStart = /<note id="(\d+)">/;
  const regexpEnd = /<\/note>/;
  let resStart, resEnd;
  const notes = [];
  while((resStart = regexpStart.exec(htmlWithNotes)) !== null) {
    htmlWithNotes = htmlWithNotes.replace(regexpStart, '');
    resEnd = regexpEnd.exec(htmlWithNotes);
    htmlWithNotes = htmlWithNotes.replace(regexpEnd, '');
    notes.push({
      "note_id" : parseInt(resStart[1]),
      "ptr_start": resStart.index,
      "ptr_end": resEnd.index
    });
  }
  return notes;
}
const computeAlignmentPointers  = (htmlWithSegments) => {

  const reg = /<segment><\/segment>/gmi;
  const splitted  = htmlWithSegments.split(reg);
  console.log("computeAlignmentPointers", splitted);
  return splitted.map(seg => seg.length);
}

export default teiToQuill;
export {
  insertNotes,
  stripNotes,
  stripSegments,
  computeAlignmentPointers,
  computeNotesPointers,
};
