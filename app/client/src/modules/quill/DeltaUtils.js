import omit from 'lodash/omit';
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
const removeFromDelta = (delta, arrAttributesToRemove) => {
  let filteredDelta = new Delta();




  delta.forEach(function (op) {
    let newOp = {};
    let type;
    if (op.retain) {
      type = 'retain';
    } else if (op.insert) {
      type = 'insert';
    } else if (op.delete) {
      type = 'delete';
    }
    if (op[type] !== null && typeof op[type] === 'object') {
      let obj = Object.assign({}, op[type]);
      arrAttributesToRemove.forEach(attr => {
        delete obj[attr];
      });
      newOp[type] = obj;
    } else {
      newOp[type] = op[type];
    }

    if (op.attributes) {
      let attribs = Object.assign({}, op.attributes);
      arrAttributesToRemove.forEach(attr => {
        delete attribs[attr];
      });
      newOp.attributes = attribs;
    }

    //console.log('newOp', newOp);

    filteredDelta.ops.push(newOp);

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
  removeFromDelta,
  removeNotesFromDelta
}