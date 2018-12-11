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
  //'br': { tag: 'lb'},
  'i': { tag: 'hi', attr: 'rend', attrValue:'i'},
  'strong': { tag: 'hi', attr: 'rend', attrValue:'b'},
  'sup': { tag: 'hi', attr: 'rend', attrValue:'sup'},
  'smallcaps': { tag: 'hi', attr: 'rend', attrValue:'sc'},
  'u': { tag: 'hi', attr: 'rend', attrValue:'u'},
  // TODO couleur	hi[@style="$color"]	?
  'blockquote': { tag: 'quote', attr: 'rend', attrValue:'block'},
  'q': { tag: 'quote', attr: 'rend', attrValue:'inline'},
  'cite': { tag: 'title', attr: 'ref'},
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
  //'lb': { tag: 'br'},
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
  'title': { tag: 'cite'},
  'persName': { tag: 'persname'},
  'placeName': { tag: 'placename'},
};

const TEIToQuill = (teiString) => {

  const xmlDoc = parser.parseFromString('<doc>'+teiString+'</doc>',"text/xml");
  let newDoc;
  newDoc = recurChange(xmlDoc.documentElement, MAPPING_TEI_TO_QUILL);
  let str = xmlSerializer.serializeToString(newDoc);
  str = str.replace(/<lb><\/lb>/gi, '<lb/>');
  str = str.replace(/<\/?doc([^>]*)>/gi, '');
  //str = convertLinebreakTEIToQuill(str);
  return str;

};

const quillToTEI = quillString => {

  quillString = quillString.replace(/&nbsp;/gi, '&#160;');
  quillString = quillString.replace(/<br>/gi, '<br/>');

  const xmlDoc = parser.parseFromString('<doc>'+quillString+'</doc>',"text/xml");
  let newDoc;
  newDoc = recurChange(xmlDoc.documentElement, MAPPING_QUILL_TO_TEI);
  let str = xmlSerializer.serializeToString(newDoc);
  str = convertLinebreakQuillToTEI(str);
  str = str.replace(/<(\/?)persname( ref="[^"]*")?>/gmi, '<$1persName$2>');
  str = str.replace(/<(\/?)placename( ref="[^"]*")?>/gmi, '<$1placeName$2>');
  str = str.replace(/<\/?doc([^>]*)>/gi, '');
  return str;
};

const convertLinebreakTEIToQuill = str => {
  return str.replace(/<lb\/?>(<\/lb>)?/gi, '<lb><span class="br"></span><span class="segment-bullet"></span></lb>');
}
const convertLinebreakQuillToTEI = str => {
  return str.replace(/<lb><span class="br"><\/span><span class="segment-bullet"><\/span><\/lb>/gi, '<lb/>');
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
const insertFacsimileZones = (text, zones) => {
  let result = text;
  let indexCorrection = 0;
  let count = 0;
  zones.forEach(zone => {
    let opening = `<zone id="${zone.zone_id}">`;
    let closing = '</zone>'
    result = result.insert(zone.ptr_start + indexCorrection, opening);
    indexCorrection += opening.length;
    result = result.insert(zone.ptr_end + indexCorrection, closing);
    indexCorrection += closing.length;
    count++
  })
  return result;
};
const insertSegments = (text, segments, translationOrTranscription) => {
  const index = translationOrTranscription === 'transcription' ? 0 : 2;
  const tag = `<segment></segment>`;
  const tagLength = tag.length;
  let result = text;
  let indexCorrection = 0;
  segments.forEach(segment => {
    let strAtInsertPoint = result.substr(segment[index] + indexCorrection, 3);
    if (segment[index] + indexCorrection > 0 && strAtInsertPoint !== '<p>' && strAtInsertPoint !== '<l>' && strAtInsertPoint !== '<lb>') {
      result = result.insert(segment[index] + indexCorrection, tag);
      indexCorrection += tagLength;
    }
  });
  return result;
};
const insertNotesAndSegments  = (text, notes, segments, translationOrTranscription) => {

  const index = translationOrTranscription === 'transcription' ? 0 : 2;
  let insertions = [];
  notes.forEach(note => {
    insertions.push({index: note.ptr_start, type: 'note_start', note: note});
    insertions.push({index: note.ptr_end, type: 'note_end'});
  });
  //console.log(insertions.length, "insertions after", notes.length,"notes")
  segments.forEach(segment => {
    if (segment[index]) insertions.push({index: segment[index], type: 'segment'});
  });
  insertions.sort((a, b) => { return a.index - b.index; });

  //console.log('')
  //console.log('insertNotesAndSegments', translationOrTranscription)
  //console.log('notes', notes)
  //console.log('segments', segments)
  //console.log(insertions)
  //console.log('')

  let result = text;
  let indexCorrection = 0;

  insertions.forEach(ins => {
    let insertTag = '';
    let inserted = false;
    switch (ins.type) {
      case 'segment':
        let strAtInsertPoint = result.substr(ins.index + indexCorrection, 3);
        inserted = (ins.index + indexCorrection > 0 && strAtInsertPoint !== '<p>' && strAtInsertPoint !== '<l>' && strAtInsertPoint !== '<lb');
        if (ins.index + indexCorrection > 0 && strAtInsertPoint !== '<p>' && strAtInsertPoint !== '<l>' && strAtInsertPoint !== '<lb') {
          insertTag = '<segment></segment>';
        }
        //console.log(" insert ", ins.type, "@ "+ins.index, `(${ins.index} + ${indexCorrection})`, insertTag, strAtInsertPoint, inserted ? 'OUI' : 'NON');
        break;
      case 'note_start':
        insertTag = `<note id="${ins.note.id}">`;
        //console.log(" insert ", ins.type, "@ "+ins.index, `(${ins.index} + ${indexCorrection})`, insertTag);
        inserted = true;
        break;
      case 'note_end':
        insertTag = `</note>`;
        //console.log(" insert ", ins.type, "@ "+ins.index, `(${ins.index} + ${indexCorrection})`, insertTag);
        inserted = true;
        break;
    }
    result = result.insert(ins.index + indexCorrection, insertTag);
    if (inserted) //console.log(" =>", result)
    indexCorrection += insertTag.length;
  });

  return result
}
const insertSpeechparts = (text, speechparts) => {
  let insertions = [];
  speechparts.forEach((note, index) => {
    insertions.push({index: note.ptr_start, type: 'sp_start', note: note, fakeId: index});
    insertions.push({index: note.ptr_end, type: 'sp_end'});
  });
  insertions.sort((a, b) => { return a.index - b.index; });

  let result = text;
  let indexCorrection = 0;

  insertions.forEach(ins => {
    let insertTag = '';
    let inserted = false;
    switch (ins.type) {
      case 'sp_start':
        insertTag = `<speechpart id="${ins.fakeId}">`;
        inserted = true;
        break;
      case 'sp_end':
        insertTag = `</speechpart>`;
        inserted = true;
        break;
    }
    result = result.insert(ins.index + indexCorrection, insertTag);
    if (inserted) //console.log(" =>", result)
      indexCorrection += insertTag.length;
  });

  return result
};

const stripNotes  = text => text.replace(/<\/?note( id="\d+")?>/gmi, '');
const stripSegments  = text => text.replace(/<\/?segment>/gmi, '');
const stripSpeechparts  = text => text.replace(/<\/?speechpart( id="\d+")?>/gmi, '');

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
  let splitted  = htmlWithSegments.split(reg);
  let positions = [];
  ////console.log("computeAlignmentPointers");
  ////console.log(htmlWithSegments);
  ////console.log("   splitted", splitted.length, splitted);
  let acc = 0;
  for (let i = 0; i < splitted.length; ++i) {
    acc += splitted[i].length;
    positions.push(acc);
  }
  ////console.log("   segments positions", positions);

  const htmlWithoutSegments = htmlWithSegments.replace(reg, '');
  ////console.log('htmlWithoutSegments', htmlWithoutSegments);
  let regexp = /<(p|lb?)\/?>/gmi;
  let res;
  while ((res = regexp.exec(htmlWithoutSegments)) !== null) {
    ////console.log("BR @", res.index)
    positions.push(res.index);
  }
  positions.sort((a, b) => {
    return a - b;
  });
  let pointers = [];
  for (let i = 1; i < positions.length; ++i) {
    pointers.push([positions[i-1], positions[i]])
  }
  return pointers;
}

const computeSpeechpartsPointers  = (htmlWithSpeechparts) => {

  //console.log("computeSpeechpartsPointers", htmlWithSpeechparts)

  const regexpStart = /<speechpart id="((\d+)|temp)">/;
  const regexpEnd = /<\/speechpart>/;
  let resStart, resEnd;
  const speechparts = [];
  while((resStart = regexpStart.exec(htmlWithSpeechparts)) !== null) {
    htmlWithSpeechparts = htmlWithSpeechparts.replace(regexpStart, '');
    resEnd = regexpEnd.exec(htmlWithSpeechparts);
    console.log(" ", resStart, resEnd)
    htmlWithSpeechparts = htmlWithSpeechparts.replace(regexpEnd, '');
    speechparts.push({
      "index" : parseInt(resStart[1]),
      "ptr_start": resStart.index,
      "ptr_end": resEnd.index
    });
  }
  //console.log("speechparts pointers", speechparts)
  return speechparts;
}
const computeImageAlignmentsPointers  = (htmlWithFacsimile) => {

  const regexpStart = /<zone id="((\d+)|temp)">/;
  const regexpEnd = /<\/zone>/;
  let resStart, resEnd;
  const alignments = [];
  while((resStart = regexpStart.exec(htmlWithFacsimile)) !== null) {
    htmlWithFacsimile = htmlWithFacsimile.replace(regexpStart, '');
    resEnd = regexpEnd.exec(htmlWithFacsimile);
    htmlWithFacsimile = htmlWithFacsimile.replace(regexpEnd, '');
    alignments.push({
      "zone_id" : parseInt(resStart[1]),
      "ptr_start": resStart.index,
      "ptr_end": resEnd.index
    });
  }
  return alignments;
}


export {
  quillToTEI,
  TEIToQuill,
  convertLinebreakTEIToQuill,
  convertLinebreakQuillToTEI,
  insertFacsimileZones,
  insertNotesAndSegments,
  insertNotes,
  insertSegments,
  insertSpeechparts,
  stripNotes,
  stripSegments,
  computeAlignmentPointers,
  computeNotesPointers,
  computeSpeechpartsPointers,
  computeImageAlignmentsPointers
};
