import axios from 'axios';
import Quill from '../../../modules/quill/AdeleQuill';
import TEItoQuill, {insertNotes, computeNotesPointers} from '../../../modules/quill/MarkupUtils'

const state = {

  translation: undefined,
  translationWithNotes: undefined,
  translationSaved: false,
  translationHtml: null,
  shadowQuillElement: document.createElement('div',{ class: 'phantom-quill-translation'}),
  shadowQuill: null

};

const mutations = {

  INIT(state, payload) {
    if (!state.shadowQuill) {
      state.shadowQuillElement.innerHTML = payload;
      state.shadowQuill = new Quill(state.shadowQuillElement);
      state.translationHtml = payload;
    }
  },

  UPDATE (state, payload) {
    //console.log("STORE MUTATION translation/UPDATE")
    state.translation = payload.raw;
    state.translationWithNotes = payload.formatted;
    state.translationSaved = true;
  },
  CHANGED (state) {
    // translation changed and needs to be saved
    //console.log("STORE MUTATION translation/CHANGED")
    state.translationSaved = false;
  },
  ADD_OPERATION (state, payload) {
    state.shadowQuill.updateContents(payload);
    //console.log("STORE MUTATION translation/ADD_OPERATION", payload)
    state.translationHtml = state.shadowQuillElement.children[0].innerHTML;
  },
  SAVED (state) {
    // translation changed and needs to be saved
    //console.log("STORE MUTATION translation/SAVED", payload);
    state.translationSaved = false;
  }

};

const actions = {

  fetch ({ commit, rootGetters }) {

    const doc_id = rootGetters['document/document'].id;
    const user_id = rootGetters['user/currentUser'].id;

    console.log('STORE ACTION translation/fetch')

    axios.get(`/api/1.0/documents/${doc_id}/translations/from-user/${user_id}`).then( response => {


      let translation = {content : " ", notes: []};

      if (response.data.data && response.data.data.length !== 0) {
        translation = response.data.data;
      }

      const content = translation.content;
      const notes = translation.notes;
      const formatted = insertNotes(content, notes);

      commit('INIT', content)
      commit('UPDATE', { raw: translation, formatted: formatted });
    });

  },
  save ({ commit, dispatch, getters, rootState }, translationWithNotes) {

    console.log('STORE ACTION translation/save', translationWithNotes);

    return dispatch('saveContent')
      .then(reponse => dispatch('saveNotes', transcriptionWithNotes))
      .then(function(values) {
        console.log('all saved', values);
      })

  },
  saveContent ({ state, rootGetters }) {
    console.log('STORE ACTION translation/saveContent');
    const auth = {}//rootGetters['user/authHeader'];
    const data = { data: [{
        "content" :  state.translationHtml,
        "username": rootGetters['user/currentUser'].username
      }]};


    return new Promise( ( resolve, reject ) => {
      axios.put(`/api/1.0/documents/${state.transcription.doc_id}/translations`, data, auth)
        .then( response => {
          if (response.data.errors) reject(response.data.errors);
          else resolve( response.data )
        })
        .catch( error => {
          reject( error )
        });
    } );
  },
  saveNotes ({ commit, rootGetters, state, rootState }, transcriptionWithNotes) {

    // compute notes pointers
    const sanitizedTranscriptionWithNotes = stripSegments(transcriptionWithNotes);
    const notes = computeNotesPointers(sanitizedTranscriptionWithNotes);
    notes.forEach(note => {
      let found = rootState.notes.notes.find((element) => {
        return element.id === note.note_id;
      });
      note.content = found.content;
    });
    console.log('STORE ACTION transcription/saveNotes', notes);

    const auth = rootGetters['user/authHeader'];

    return new Promise( ( resolve, reject ) => {
      axios.put(`/api/1.0/documents/${state.transcription.doc_id}/transcriptions/notes`, { data: notes }, auth)
        .then( response => {
          resolve( response.data )
        } )
        .catch( error => {
          reject( error )
          //dispatch( 'error', { error } )
        } );
    } );
  },
  changed ({ commit }, deltas) {
    commit('ADD_OPERATION', deltas)
    commit('SAVED', false)
  }

};

const getters = {
  translation: state => state.translation,
  translationWithNotes: state => state.translationWithNotes,
  translationContent: state => !!state.translation ? state.translation.content : null,
  translationIsSaved: state => state.translationSaved,
  translationHTML: state => state.translationHtml,
  //translationWithNotes: state =>
};

const translationModule = {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}

export default translationModule;
