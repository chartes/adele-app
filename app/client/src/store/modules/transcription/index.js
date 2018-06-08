import axios from 'axios';
import Quill from '../../../modules/quill/AdeleQuill';
import TEItoQuill, {insertNotes, computeNotesPointers} from '../../../modules/quill/TEIConversion'
import {removeNotesFromDelta} from '../../../modules/quill/DeltaUtils'

const state = {

  transcription: undefined,
  transcriptionWithNotes: undefined,
  transcriptionSaved: false,
  transcriptionHtml: null,
  shadowQuillElement: document.createElement('div',{ class: 'phantom-quill-transcription'}),
  shadowQuill: null

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
    console.log("TRANSCRIPTION_ADD_OPERATION", filteredDelta, state.shadowQuillElement.innerHTML, state.transcriptionHtml)
  },
  TRANSCRIPTION_SAVED (state) {
    // transcription changed and needs to be saved
    console.log("TRANSCRIPTION_CHANGED")
    state.transcriptionSaved = false;
  }

};

const actions = {

  fetchTranscription ({ commit, getters, rootState }) {
    const doc_id = getters.document.id;
    const user_id = getters.currentUser.id;

    console.log('STORE ACTION fetchTranscription')

    this.dispatch('fetchNoteTypes').then(() => {
      console.log('   dispatch fetchNoteTypes')
      return this.dispatch('fetchNotes', getters.document.id);
    }).then(() => {

      axios.get(`/api/1.0/documents/${doc_id}/transcriptions/from-user/${rootState.user.currentUser.id}`).then( response => {

        /*const data = {
          "data": {
            "content": "Om<ex>n</ex>ib<ex>us</ex> p<ex>re</ex>sentes litt<ex>er</ex>as insp<ex>e</ex>cturis,. . offic<ex>ialis</ex> Belvacen<ex>sis</ex>, sal<ex>u</ex>t<ex>em</ex> in D<ex>om</ex>in<ex>o</ex>.Nov<ex>er</ex>int univ<ex>er</ex>si q<ex>uo</ex>d i<ex>n</ex> n<ex>ost</ex>ra constituti p<ex>re</ex>sentia.",
            "doc_id": 20,
            "id": 20,
            "notes": [
              {
                "content": "Juge en mati\u00e8re contentieuse et gracieuse, d\u00e9l\u00e9gu\u00e9 de l\u2019\u00e9v\u00eaque.",
                "id": 33,
                "note_type": {
                  "id": 0,
                  "label": "TERM"
                },
                "ptr_end": 107,
                "ptr_start": 88,
                "user_id": "jpilla"
              }
            ]
          }
        }
        const transcription = data.data;
        */


        let transcription = {content : " ", notes: []};

        if (response.data.data && response.data.data.length !== 0) {
          transcription = response.data.data;
        }

        console.log("FETCHED TRANSCRIPTION", transcription);

        const content = transcription.content;
        const notes = transcription.notes;
        const formatted = insertNotes(content, notes);

        //console.log('formatted', formatted)

        commit('TRANSCRIPTION_INIT', content)
        commit('UPDATE_TRANSCRIPTION', { raw: transcription, formatted: formatted });
      })

    });
  },
  saveTranscription ({ commit, getters, state, rootState }, transcriptionWithNotes) {

    console.log('STORE ACTION saveTranscription', state.transcriptionWithNotes, state.transcriptionHtml);



    // count notes pointers
    const notes = computeNotesPointers(transcriptionWithNotes);
    notes.forEach((note) => {
      let found = rootState.notes.notes.find((element) => {
        return element.id === note.note_id;
      });
      note.content = found.content;
    });
    console.log(notes);

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
  state,
  mutations,
  actions,
  getters
}

export default transcriptionModule;
