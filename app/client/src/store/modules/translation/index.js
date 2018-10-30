import axios from 'axios';
import Quill from '../../../modules/quill/AdeleQuill';
import TEItoQuill, {
  insertNotes, computeNotesPointers, TEIToQuill,
  insertSegments, stripSegments, quillToTEI, convertLinebreakTEIToQuill, insertNotesAndSegments,
  convertLinebreakQuillToTEI
} from '../../../modules/quill/MarkupUtils'
import {filterDeltaOperations} from "../../../modules/quill/DeltaUtils";

const translationShadowQuillElement = document.createElement('div');
const notesShadowQuillElement = document.createElement('div');
let translationShadowQuill;
let notesShadowQuill;

const state = {
  translationLoading: true,
  translation: false,
  translationContent: false,
  translationWithNotes: false,
  translationSaved: true,
  translationError: false,
  translationAlignments: [],
  referenceTranslation: false
};

const mutations = {

  INIT(state, payload) {
    if (!state.shadowQuill) {
      translationShadowQuillElement.innerHTML = payload.content;
      translationShadowQuill = new Quill(translationShadowQuillElement);
      state.translationContent = translationShadowQuillElement.children[0].innerHTML;
      console.log('STORE ACTION translation/INIT')

      notesShadowQuillElement.innerHTML = payload.withNotes;
      notesShadowQuill = new Quill(notesShadowQuillElement);
      state.translationWithNotes = notesShadowQuillElement.children[0].innerHTML;

    }
  },
  RESET (state) {
    console.log("STORE MUTATION translation/RESET")
    state.translation = false;
    state.translationAlignments = [];
    state.translationContent = false;
    state.translationWithNotes = false;
    state.translationWithSpeechparts = false;

    if (translationShadowQuillElement) translationShadowQuillElement.innerHTML = "";
    if (notesShadowQuillElement) notesShadowQuillElement.innerHTML = "";
  },
  REFERENCE(state, payload) {
    state.referenceTranslation = payload
  },
  LOADING_STATUS (state, payload) {
    state.translationLoading = payload;
  },
  ALIGNMENTS(state, payload) {
    state.translationAlignments = payload;
  },
  UPDATE (state, payload) {
    state.translation = payload.translation;
    state.translationWithNotes = payload.withNotes;
    state.translationSaved = true;
  },
  CHANGED (state) {
    // translation changed and needs to be saved
    state.translationSaved = false;
  },
  ADD_OPERATION (state, payload) {

    console.log("STORE MUTATION translation/ADD_OPERATION")

    const deltaFilteredForContent = filterDeltaOperations(translationShadowQuill, payload, 'content');
    const deltaFilteredForNotes = filterDeltaOperations(notesShadowQuill, payload, 'notes');

    translationShadowQuill.updateContents(deltaFilteredForContent);
    notesShadowQuill.updateContents(deltaFilteredForNotes);

    state.translationContent = translationShadowQuillElement.children[0].innerHTML;
    state.translationWithNotes = notesShadowQuillElement.children[0].innerHTML;

  },
  SAVED (state) {
    // translation changed and needs to be saved
    console.log("STORE MUTATION translation/SAVED");
    state.translationSaved = true;
  }

};

const actions = {

  fetch ({ commit, rootGetters, rootState }) {

    commit('LOADING_STATUS', true);

    const doc_id = rootState.document.document.id;
    const user_id = rootState.user.author.id;
    const alignments = rootState.transcription.transcriptionAlignments;

    console.log('STORE ACTION translation/fetch',rootState)

    return axios.get(`/adele/api/1.0/documents/${doc_id}/translations/from-user/${user_id}`).then( response => {

      commit('LOADING_STATUS', false);

      if (response.data.errors && response.data.errors.status === 404) {
        console.log("NO translation found");
        return;
      }

      let translation = {content : " ", notes: []};

      if (response.data.data && response.data.data.length !== 0) {
        translation = response.data.data[0];
      }
      let quillContent = TEIToQuill(translation.content);
      let content = insertSegments(quillContent, alignments, 'translation');
      const withNotes = insertNotesAndSegments(quillContent, translation.notes, alignments, 'translation');

      const data = {
        translation: translation,
        content: convertLinebreakTEIToQuill(content),
        withNotes: convertLinebreakTEIToQuill(withNotes),
      }

      commit('INIT', data)
      commit('UPDATE', data);
    });

  },
  fetchReference ({commit}, {doc_id}) {

    console.log('STORE ACTION translation/fetchReference', doc_id);

    return axios.get(`/adele/api/1.0/documents/${doc_id}/translations/reference`).then( response => {

      commit('LOADING_STATUS', false);


      if (response.data.errors && response.data.errors.status === 404) {
        console.warn("NO reference translation found");
        return;
      }
      let translation = false;

      if (response.data.data) {
        translation = response.data.data;
      }

      if (!translation) return commit('REFERENCE', false);

      let quillContent = TEIToQuill(translation.content);
      const withNotes = insertNotesAndSegments(quillContent, translation.notes, [], 'translation');
      translation.content = withNotes

      commit('REFERENCE', translation)
    })
  },
  save ({ commit, dispatch }) {

    console.log('STORE ACTION translation/save');

    return dispatch('saveContent')
      .then(reponse => dispatch('saveNotes'))
      .then(function(values) {
        console.log('all saved', values);
      })

  },
  saveContent ({ state, rootState, rootGetters }) {
    console.log('STORE ACTION translation/saveContent');
    const auth = rootGetters['user/authHeader'];
    const tei = quillToTEI(state.translationContent);
    const sanitized = stripSegments(tei);
    const data = { data: [{
        "content" : sanitized,
        "username": rootState.user.author.username
      }]};

    return new Promise( ( resolve, reject ) => {
      axios.put(`/adele/api/1.0/documents/${state.translation.doc_id}/translations`, data, auth)
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
  saveNotes ({ commit, rootGetters, state, rootState }) {

    console.log('STORE ACTION translation/saveNotes');

    // compute notes pointers
    let sanitizedWithNotes = stripSegments(state.translationWithNotes);
    sanitizedWithNotes = convertLinebreakQuillToTEI(sanitizedWithNotes);
    const notes = computeNotesPointers(sanitizedWithNotes);
    notes.forEach(note => {
      let found = rootState.notes.notes.find((element) => {
        return element.id === note.note_id;
      });
      note.content = found.content;
      note.translation_username = rootState.user.author.username;
      note.note_type = found.note_type.id;
    });

    const auth = rootGetters['user/authHeader'];

    return new Promise( ( resolve, reject ) => {
      axios.put(`/adele/api/1.0/documents/${state.translation.doc_id}/translations/notes`, { data: notes }, auth)
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
  changed ({ commit, dispatch }, deltas) {
    commit('ADD_OPERATION', deltas);
    commit('SAVED', false);
    dispatch('transcription/translationChanged', null, {root:true})
  },
  reset ({ commit }) {
    commit('RESET')
  },
  create ({ commit, rootState, rootGetters }) {
    const auth = rootGetters['user/authHeader'];
    const data = { data: [{
        "content" : '<p></p>',
        "username": rootState.user.currentUser.username
      }]};
    return new Promise( ( resolve, reject ) => {
      axios.post(`/adele/api/1.0/documents/${rootState.document.document.id}/translations`, data, auth)
        .then( response => {
          if (response.data.errors) {
            reject(response.data.errors);
          }
          else resolve( response.data )
        })
        .catch( error => {
          reject( error )
        });
    } );
  },

};

const getters = {
};

const translationModule = {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}

export default translationModule;
