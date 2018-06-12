const parser = new DOMParser();

const teiToQuill = (teiString) => {

  const xmlDoc = parser.parseFromString(teiString,"text/xml");

  let newDoc = recurChange(xmlDoc.documentElement.firstChild, "");

}

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

function recurChange (node) {
  let newNode;
  if (node.nodeType == 3) {
    return document.createTextNode(node.nodeValue);
  }
  if (node.nodeName === 'hi') {
    newNode = document.createElement('test');
  } else {
    newNode = document.createElement(node.nodeName);
  }
  copyEltAttributes(node, newNode);
  if (node.hasChildNodes()) {
    for (let i = 0; i < node.childNodes.length ;i++) {
      var child = node.childNodes[i];
      newNode.appendChild(recurChange(child));
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
