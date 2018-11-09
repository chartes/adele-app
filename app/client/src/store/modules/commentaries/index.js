import axios from "axios/index";
import Quill from '../../../modules/quill/AdeleQuill';
import {
  insertNotes,
  quillToTEI,
  stripSegments,
  stripNotes,
  TEIToQuill,
  computeNotesPointers, convertLinebreakQuillToTEI
} from '../../../modules/quill/MarkupUtils';


const state = {

  commentaries: [],
  //commentariesWithNotes: {},
  hasCommentaryTypes: [],
  commentaryTypes: [],
  saved: true,

};

const mutations = {

  UPDATE_TYPES (state, payload) {
    state.commentaryTypes = payload
  },
  UPDATE (state, { commentaries, hasTypes}) {
    state.commentaries = commentaries;
    state.hasCommentaryTypes = hasTypes
  },
  UPDATE_COMMENTARY (state, {content, type}) {
    const comm = state.commentaries.find(c => c.type === type);
    comm.content = content
  },
  SAVED (state, payload) {
    state.saved = payload
  }

};

const actions = {

  fetchTypes ({ commit }) {
    axios.get(`/adele/api/1.0/commentary-types`).then( response => {
      const respData = response.data.data;
      const isArray = Array.isArray(respData);
      const commentaryTypes = isArray ? respData : [respData];
      commit('UPDATE_TYPES', commentaryTypes)
    });
  },

  fetch ({ commit }, {doc_id, user_id}) {
    axios.get(`/adele/api/1.0/documents/${ doc_id }/commentaries/from-user/${ user_id }`).then( response => {
      const respData = response.data.data;
      const isArray = Array.isArray(respData);
      const commentaries = isArray ? respData : [respData];
      let hasTypes = {};
      let commentariesFormatted = [];
      commentaries.forEach(comm => {
        let quillContent = TEIToQuill(comm.content);
        let withNotes = insertNotes(quillContent, comm.notes);
        commentariesFormatted.push({
          type: comm.type.id,
          typeLabel: comm.type.label,
          content: withNotes,
          notes: comm.notes
        });
        hasTypes[comm.type.label] = true
      });

      commit('UPDATE', { commentaries: commentariesFormatted, hasTypes })
    });
  },

  changed ({ commit, dispatch }, {content, type}) {
    commit('UPDATE_COMMENTARY', {content, type});
    commit('SAVED', false);
    //dispatch('transcription/translationChanged', null, {root:true})
  },

  add ({ commit, rootState }, typeId) {
    const config = { auth: { username: rootState.user.authToken, password: undefined }};
    const doc_id = rootState.document.document.id
    const newCommentaryData = {
      "data": {
        "doc_id": doc_id,
        "type_id": typeId,
        "user_id": rootState.user.currentUser.id,
        "content": "<p></p>"
      }
    }

    return axios.post(`/adele/api/1.0/documents/${ doc_id }/commentaries`, newCommentaryData, config).then( response => {
      const respData = response.data.data;
      const isArray = Array.isArray(respData)

      const commentaries = isArray ? respData : [respData];
      let hasTypes = {};

      let commentariesFormatted = [];
      commentaries.forEach(comm => {
        let quillContent = TEIToQuill(comm.content);
        let withNotes = insertNotes(quillContent, comm.notes);
        commentariesFormatted.push({
          type: comm.type.id,
          typeLabel: comm.type.label,
          content: withNotes,
          notes: comm.notes
        });
        hasTypes[comm.type.label] = true;
      });
      console.log(commentariesFormatted);
      commit('UPDATE', { commentaries: commentariesFormatted, hasTypes })
    });
  },

  save ({ commit, dispatch }, typeId) {
    console.log('STORE ACTION commentaries/save', typeId);

    return dispatch('saveContent', typeId)
      .then(reponse => dispatch('saveNotes', typeId))
      .then(function(values) {
        console.log('commentary saved', values);
      })
  },
  saveContent ({ commit, rootState, rootGetters }, typeId) {

    const auth = rootGetters['user/authHeader'];
    const comm = state.commentaries.find(c => c.type === typeId)
    const tei = quillToTEI(comm.content);
    let sanitized = stripSegments(tei);
    sanitized = stripNotes(sanitized);
    const commData = {
      "data": {
        "doc_id": rootState.document.document.id,
        "type_id": typeId,
        "user_id": rootState.user.currentUser.id,
        "content": sanitized
      }
    }

    return new Promise( ( resolve, reject ) => {
      axios.put(`/adele/api/1.0/documents/${rootState.document.document.id}/commentaries`, commData, auth)
        .then( response => {
          if (response.data.errors) {
            console.error("error", response.data.errors);
            reject(response.data.errors);
          }
          else resolve( response.data )
        })
        .catch( error => {
          console.error("error", error)
          reject( error )
        });
    } );


  },
  saveNotes ({ commit, rootState, rootGetters }, typeId) {
    console.log('STORE ACTION commentaries/saveContent', typeId);
    const auth = rootGetters['user/authHeader'];
    const comm = state.commentaries.find(c => c.type === typeId)
    let sanitizedWithNotes = stripSegments(comm.content);
    sanitizedWithNotes = convertLinebreakQuillToTEI(sanitizedWithNotes);
    const notes = computeNotesPointers(sanitizedWithNotes);
    notes.forEach(note => {
      let found = rootState.notes.notes.find(element => {
        return element.id === note.note_id;
      });
      note.content = found.content;
      note.commentary_username = rootState.user.author.username;
      note.note_type = found.note_type.id;
    });

    return new Promise((resolve, reject) => {
      axios.put(`/adele/api/1.0/documents/${rootState.document.document.id}/commentaries/notes`, {data: notes}, auth)
        .then(response => {
          if (response.data.errors) {
            console.error("error", response.data.errors);
            reject(response.data.errors);
          }
          else {
            resolve(response.data);
          }
        });
    })
  }


};

const getters = {
  missingCommentaryTypes (state) {
    return state.commentaryTypes.filter(ct => {
      return !state.hasCommentaryTypes[ct.label]
    }
    )
  }
};

const commentariesModule = {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}

export default commentariesModule;
