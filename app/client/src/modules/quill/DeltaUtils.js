import Delta from 'quill-delta';

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
  removeNotesFromDelta
}