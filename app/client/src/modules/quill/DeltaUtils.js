import Delta from 'quill-delta';

//function get


export function filterDeltaForSpeechParts (delta) {
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
