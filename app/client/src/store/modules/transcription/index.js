import axios from 'axios';
import Quill from '../../../modules/quill/AdeleQuill';
import TEItoQuill, {
  insertNotes, stripSegments, computeNotesPointers, computeAlignmentPointers, stripNotes
} from '../../../modules/quill/MarkupUtils'
import {removeNotesFromDelta} from '../../../modules/quill/DeltaUtils'

const state = {

  transcription: undefined,
  transcriptionWithNotes: undefined,
  transcriptionSaved: false,
  transcriptionHtml: null,
  shadowQuillElement: document.createElement('div',{ class: 'shadow-quill-transcription'}),
  shadowQuill: null,
  transcriptionError: false,

};

const mutations = {

  TRANSCRIPTION_INIT(state, payload) {
    if (!state.shadowQuill) {
      state.shadowQuillElement.innerHTML = payload;
      state.shadowQuill = new Quill(state.shadowQuillElement);
      state.transcriptionHtml = payload;
    }
  },

  UPDATE_TRANSCRIPTION (state, payload) {
    console.log("UPDATE_TRANSCRIPTION")
    state.transcription = payload.raw;
    state.transcriptionWithNotes = payload.formatted;
    state.transcriptionSaved = true;
  },
  TRANSCRIPTION_CHANGED (state) {
    // transcription changed and needs to be saved
    console.log("TRANSCRIPTION_CHANGED")
    state.transcriptionSaved = false;
  },
  TRANSCRIPTION_ADD_OPERATION (state, payload) {
    const filteredDelta = removeNotesFromDelta(payload)
    state.shadowQuill.updateContents(payload);
    state.transcriptionHtml = state.shadowQuillElement.children[0].innerHTML;
    console.log("TRANSCRIPTION_ADD_OPERATION")
  },
  TRANSCRIPTION_SAVED (state) {
    // transcription changed and needs to be saved
    console.log("TRANSCRIPTION_CHANGED")
    state.transcriptionSaved = false;
  }

};

const actions = {

  fetchTranscription ({ commit, rootGetters }) {

    console.log('STORE ACTION fetchTranscription')

    const doc_id = rootGetters['document/document'].id;
    const user_id = rootGetters['user/currentUser'].id;


    this.dispatch('noteTypes/fetchNoteTypes').then(() => {
      return this.dispatch('notes/fetchNotes', doc_id);
    }).then(() => {

      axios.get(`/api/1.0/documents/${doc_id}/transcriptions/from-user/${user_id}`).then( response => {

        let transcription = {content : " ", notes: []};

        if (response.data.data && response.data.data.length !== 0) {
          transcription = response.data.data;
        }

        console.log("FETCHED TRANSCRIPTION", transcription);

        const content = transcription.content;
        const notes = transcription.notes;
        const formatted = insertNotes(content, notes);

        commit('TRANSCRIPTION_INIT', content)
        commit('UPDATE_TRANSCRIPTION', { raw: transcription, formatted: formatted });
      })

    });
  },
  /*saveTranscription ({ commit, getters, state, rootState }, transcriptionWithNotes) {

    console.log('STORE ACTION saveTranscription');

    // compute notes pointers
    const sanitizedTranscriptionWithNotes = stripSegments(transcriptionWithNotes);
    console.log('sanitizedTranscriptionWithNotes', sanitizedTranscriptionWithNotes, '\n')
    const notes = computeNotesPointers(sanitizedTranscriptionWithNotes);
    notes.forEach(note => {
      let found = rootState.notes.notes.find((element) => {
        return element.id === note.note_id;
      });
      note.content = found.content;
    });
    console.log(notes);

    // Compute alignment pointers
    const sanitizedTranscriptionWithSegments = stripNotes(transcriptionWithNotes);
    const alignPointers = computeAlignmentPointers(sanitizedTranscriptionWithSegments);
    console.log('alignPointers', alignPointers);

    // Save transcription content without notes
    const data = { data: [
      {
        "content" :  state.transcriptionHtml,
        "username": rootState.user.currentUser.username
      }
    ]};
    console.log('rootState.user', rootState.user)
    const headerConfig = { auth: { username: rootState.user.authToken, password: undefined }};
    console.log('headerConfig', headerConfig)
    axios.put(`/api/1.0/documents/${state.transcription.doc_id}/transcriptions`, data, headerConfig)
      .then( (response) => {
        console.log('   transcription saved', response);

        return axios.put(`/api/1.0/documents/${state.transcription.doc_id}/transcriptions/notes`, { data: notes }, headerConfig)

        //commit('UPDATE_NOTES', response.data.data)
      }).then((response) => {
        console.log('   notes saved', response)
      })
      .catch(function(error) {
        console.log(error);
      });

    // remove notes


  },
  */
  saveTranscription ({ commit, rootGetters, state, rootState }) {
    console.log('saveTranscription');
    const headerConfig = rootGetters['user/authHeader'];
    const data = { data: [{
          "content" :  state.transcriptionHtml,
          "username": rootState.user.currentUser.username
        }]};
    return axios.put(`/api/1.0/documents/${state.transcription.doc_id}/transcriptions`, data, headerConfig)
      .then( response => {
        console.log('   transcription saved', response);

      })
      .catch(error => {
        console.log(error);
      });
  },
  transcriptionChanged ({ commit }, deltas) {
    commit('TRANSCRIPTION_ADD_OPERATION', deltas)
    commit('TRANSCRIPTION_SAVED', false)
  }

};

const getters = {
  transcription: state => state.transcription,
  transcriptionWithNotes: state => state.transcriptionWithNotes,
  transcriptionContent: state => !!state.transcription ? state.transcription.content : null,
  transcriptionIsSaved: state => state.transcriptionSaved,
  transcriptionHTML: state => state.transcriptionHtml,
  //transcriptionWithNotes: state =>
};

const transcriptionModule = {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}

export default transcriptionModule;
