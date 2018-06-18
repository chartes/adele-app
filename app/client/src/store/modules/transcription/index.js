import axios from 'axios';
import Quill from '../../../modules/quill/AdeleQuill';
import {
  TEIToQuill,
  quillToTEI,
  convertLinebreakTEIToQuill,
  convertLinebreakQuillToTEI,
  insertSegments,
  insertNotesAndSegments,
  stripSegments,
  computeNotesPointers,
  computeAlignmentPointers,
  stripNotes
} from '../../../modules/quill/MarkupUtils'
import {removeFromDelta} from '../../../modules/quill/DeltaUtils'


const transcriptionShadowQuillElement = document.createElement('div');
const notesShadowQuillElement = document.createElement('div');
const speechpartsShadowQuillElement = document.createElement('div');
let transcriptionShadowQuill;
let notesShadowQuill;
let speechpartsShadowQuill;

const state = {

  transcription: undefined,
  transcriptionContent: undefined,
  transcriptionWithNotes: undefined,
  transcriptionSaved: false,
  transcriptionError: false,
  transcriptionAlignments: []

};

const mutations = {

  INIT(state, payload) {
    if (!transcriptionShadowQuill) {

      transcriptionShadowQuillElement.innerHTML = payload.content;
      transcriptionShadowQuill = new Quill(transcriptionShadowQuillElement);
      state.transcriptionContent = transcriptionShadowQuillElement.children[0].innerHTML;

      notesShadowQuillElement.innerHTML = payload.withNotes;
      notesShadowQuill = new Quill(notesShadowQuillElement);
      state.transcriptionWithNotes = notesShadowQuillElement.children[0].innerHTML;

    }
  },
  ALIGNMENTS(state, payload) {
    state.transcriptionAlignments = payload;
  },
  UPDATE (state, payload) {
    console.log("STORE MUTATION transcription/UPDATE")
    state.transcription = payload.transcription;
    state.transcriptionWithNotes = payload.withNotes;
    state.transcriptionSaved = true;
  },
  CHANGED (state) {
    // transcription changed and needs to be saved
    console.log("STORE MUTATION transcription/CHANGED")
    state.transcriptionSaved = false;
  },
  ADD_OPERATION (state, payload) {

    console.log("STORE MUTATION transcription/ADD_OPERATION")

    const deltaFilteredForContent = removeFromDelta(payload, ['note','speechpart']);
    const deltaFilteredForNotes = removeFromDelta(payload, ['segment','speechpart']);
    const deltaFilteredForSpeechparts = removeFromDelta(payload, ['note','segment']);

    transcriptionShadowQuill.updateContents(deltaFilteredForContent);
    notesShadowQuill.updateContents(deltaFilteredForNotes);

    state.transcriptionContent = transcriptionShadowQuillElement.children[0].innerHTML;
    state.transcriptionWithNotes = notesShadowQuillElement.children[0].innerHTML;

  },
  SAVED (state) {
    // transcription changed and needs to be saved
    console.log("STORE MUTATION transcription/SAVED")
    state.transcriptionSaved = false;
  }

};

const actions = {

  fetch ({ commit, rootGetters }) {

    console.log('STORE ACTION transcription/fetch')

    const doc_id = rootGetters['document/document'].id;
    const user_id = rootGetters['user/currentUser'].id;


    this.dispatch('noteTypes/fetch').then(() => {
      return this.dispatch('notes/fetch', doc_id);
    })
    .then(() => {
      return this.dispatch('transcription/fetchAlignments', { doc_id, user_id });
    })
    .then(() => {

      return axios.get(`/api/1.0/documents/${doc_id}/transcriptions/from-user/${user_id}`).then( response => {

        let transcription = {content : " ", notes: []};

        if (response.data.data && response.data.data.length !== 0) {
          transcription = response.data.data;
        }

        let quillContent = TEIToQuill(transcription.content);
        let content = insertSegments(quillContent, state.transcriptionAlignments, 'transcription');
        const withNotes = insertNotesAndSegments(quillContent, transcription.notes, state.transcriptionAlignments, 'transcription');

        const data = {
          transcription: transcription,
          content: convertLinebreakTEIToQuill(content),
          withNotes: convertLinebreakTEIToQuill(withNotes),
        }

        commit('INIT', data)
        commit('UPDATE', data);
      })

    })
      .then(() => {
        return this.dispatch('translation/fetch', { doc_id, user_id });
      });
  },
  fetchAlignments ({commit}, {doc_id, user_id}) {
    return axios.get(`/api/1.0/documents/${doc_id}/transcriptions/alignments/from-user/${user_id}`).then( response => {
      // Check if response is 1 alignment or more
      const alignments = response.data.data && Array.isArray(response.data.data[0]) ? response.data.data : [response.data.data]
      commit('ALIGNMENTS', alignments);
    })

  },
  save ({dispatch}, transcriptionWithNotes) {
    console.log('STORE ACTION transcription/save');

    return dispatch('saveContent')
      .then(reponse => dispatch('saveAlignment'))
      .then(reponse => dispatch('saveNotes'))
      .then(reponse => dispatch('translation/save', null, {root:true}))
      .then(function(values) {
        console.log('all saved', values);
      })
      .catch( error => {
        console.log('something bad happened', error);
        //dispatch( 'error', { error } )
      });

  },
  saveContent ({ state, rootGetters }) {
    console.log('STORE ACTION transcription/saveContent');
    const auth = rootGetters['user/authHeader'];
    const tei = quillToTEI(state.transcriptionContent);
    const sanitized = stripSegments(tei);
    const data = { data: [{
        "content" : sanitized,
        "username": rootGetters['user/currentUser'].username
      }]};
    return new Promise( ( resolve, reject ) => {
      axios.put(`/api/1.0/documents/${state.transcription.doc_id}/transcriptions`, data, auth)
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


    console.warn('STORE ACTION transcription/saveNotes');

    // compute notes pointers
    let sanitizedWithNotes = stripSegments(state.transcriptionWithNotes);
    sanitizedWithNotes = convertLinebreakQuillToTEI(sanitizedWithNotes);
    const notes = computeNotesPointers(sanitizedWithNotes);
    notes.forEach(note => {
      let found = rootState.notes.notes.find((element) => {
        return element.id === note.note_id;
      });
      note.content = found.content;
    });

    const auth = rootGetters['user/authHeader'];

    return new Promise( ( resolve, reject ) => {
      axios.put(`/api/1.0/documents/${state.transcription.doc_id}/transcriptions/notes`, { data: notes }, auth)
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
  saveAlignment ({rootState, rootGetters}) {
    console.warn('STORE ACTION transcription/saveAlignment');
    const transcriptionTEI = quillToTEI(state.transcriptionContent);
    const translationTEI = quillToTEI(rootState.translation.translationContent);
    const transcriptionPointers = computeAlignmentPointers(transcriptionTEI);
    const translationPointers = computeAlignmentPointers(translationTEI);
    let pointers = [];
    for (let i = 0; i < Math.max(transcriptionPointers.length, translationPointers.length); ++i) {
      pointers.push([
        ...(transcriptionPointers[i] ? transcriptionPointers[i] : [0,0]),
        ...(translationPointers[i] ? translationPointers[i] : [0,0])
      ]);
    }
    const auth = rootGetters['user/authHeader'];
    const data = { data: {
        username: rootGetters['user/currentUser'].username,
        ptr_list : pointers,
      }};
    return new Promise( ( resolve, reject ) => {
      axios.post(`/api/1.0/documents/${state.transcription.doc_id}/transcriptions/alignments`, data, auth)
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
  changed ({ commit }, deltas) {
    commit('ADD_OPERATION', deltas)
    commit('SAVED', false)
  }

};

const getters = {
  transcription: state => state.transcription,
  transcriptionContent: state => state.transcriptionContent,
  transcriptionWithNotes: state => state.transcriptionWithNotes,
  transcriptionWithSegments: state => state.transcriptionWithSegments,
  transcriptionIsSaved: state => state.transcriptionSaved,
};

const transcriptionModule = {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}

export default transcriptionModule;
