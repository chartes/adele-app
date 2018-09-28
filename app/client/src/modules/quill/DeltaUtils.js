import _omit from 'lodash/omit';
import _isEmpty from 'lodash/isEmpty';
import _pick from 'lodash/pick';
import _values from 'lodash/values';
import Delta from 'quill-delta';


const globalFilters = {
  removeAttributes: ['color','background'],
  keepFormats: ['bold', 'italic', 'smallcaps', 'underline', 'del', 'expan', 'superscript', 'location', 'person']
}
const deltaOperationsFilters = {
  content: {
    removeAttributes: ['note','speechpart', 'zone'].concat(globalFilters.removeAttributes),
    keepFormats: [].concat(globalFilters.keepFormats),
  },
  notes: {
    removeAttributes: ['segment','speechpart', 'zone'].concat(globalFilters.removeAttributes),
    keepFormats: ['note'].concat(globalFilters.keepFormats),
  },
  speechparts: {
    removeAttributes: ['segment', 'note', 'zone'].concat(globalFilters.removeAttributes),
    keepFormats: ['speechpart'].concat(globalFilters.keepFormats),
  },
  facsimile: {
    removeAttributes: ['note', 'segment','speechpart'].concat(globalFilters.removeAttributes),
    keepFormats: ['zone'].concat(globalFilters.keepFormats),
  }
}

//function get
const getNewDelta = () => new Delta();


const filterDeltaForSpeechParts = (delta) => {
  // TODO: cette fonction est chelou
  let filteredDelta = new Delta();
  delta.forEach(function(op) {
    if (op.retain) {
      filteredDelta.retain(op.retain);
    }
    else if (op.insert) {
      filteredDelta.insert(op.insert);
    }
    else if (op.delete) {
      filteredDelta.delete(op.delete);
    }
  });
  return filteredDelta;
}
const filterDeltaOperations = (quillInstance, delta, mode) => {

  console.log("filterDeltaOperations", mode, delta, delta.ops)

  // Renvoie un nouveau delta filtré selon arrAttributesToRemove

  let filteredDelta = new Delta();
  let insertionIndex = 0;

  let firstOperation = Object.assign({}, delta.ops[0]);
  if (firstOperation.retain) {
    insertionIndex = firstOperation.retain;
  }
  firstOperation = filterOperation(quillInstance, firstOperation, mode, 0);
  filteredDelta.ops.push(firstOperation);
  let restOperations = _values(_omit(delta.ops, [0]))

  if (restOperations.length > 0) {

    restOperations.forEach(function (op) {

      filteredDelta.ops.push(filterOperation(quillInstance, op, mode, insertionIndex));

    });

  }
  return filteredDelta;

}
const filterOperation = (quillInstance, operation, mode, insertionIndex) => {
  const filters = deltaOperationsFilters[mode]
  let newOp = {};
  let type = getOperationType(operation)

  // Copie le type d'operation
  if (operation[type] !== null && typeof operation[type] === 'object') {
    newOp[type] = Object.assign({}, operation[type]);
  } else {
    newOp[type] = operation[type];
  }

  // Copie les formats de l'instance quill au point d'insertion
  let formats = quillInstance.getFormat(insertionIndex);
  if (type !== 'delete') {
    formats = _pick(formats, filters.keepFormats);
    if (!_isEmpty(formats)) newOp.attributes = formats;
  }

  // Copie les attributs (styles) si existent
  if (operation.attributes) {
    let attr = Object.assign({}, _omit(operation.attributes, filters.removeAttributes));
    newOp.attributes = Object.assign(formats, attr);
  }
  return newOp;
}
const getOperationType = (operation) => {
  if (operation.retain) {
    return 'retain';
  } else if (operation.insert) {
    return 'insert';
  } else if (operation.delete) {
    return 'delete';
  }
}

const removeNotesFromDelta = (delta) => {
  let filteredDelta = new Delta();
  delta.ops.forEach(function (op) {
    if (op.attributes && op.attributes.note) delete op.attributes.note;
    filteredDelta.ops.push(op);
  })
  return filteredDelta;
}

export {
  getNewDelta,
  filterDeltaForSpeechParts,
  filterDeltaOperations,
  removeNotesFromDelta
}