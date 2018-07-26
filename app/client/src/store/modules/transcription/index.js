import axios from 'axios';
import Quill from '../../../modules/quill/AdeleQuill';
import {
  TEIToQuill,
  quillToTEI,
  convertLinebreakTEIToQuill,
  convertLinebreakQuillToTEI,
  insertSegments,
  insertNotesAndSegments,
  insertSpeechparts,
  stripSegments,
  computeNotesPointers,
  computeAlignmentPointers,
  computeSpeechpartsPointers
} from '../../../modules/quill/MarkupUtils'
import {removeFromDelta} from '../../../modules/quill/DeltaUtils'


const transcriptionShadowQuillElement = document.createElement('div');
const notesShadowQuillElement = document.createElement('div');
const speechpartsShadowQuillElement = document.createElement('div');
let transcriptionShadowQuill;
let notesShadowQuill;
let speechpartsShadowQuill;

const state = {

  transcriptionLoading: false,
  transcription: false,
  transcriptionContent: false,
  transcriptionWithNotes: false,
  transcriptionWithSpeechparts: false,
  transcriptionSaved: false,
  transcriptionError: false,
  transcriptionAlignments: []

};

const mutations = {


  INIT(state, payload) {

    console.log("INIT", payload)

    if (!transcriptionShadowQuill) {

      transcriptionShadowQuillElement.innerHTML = payload.content || "";
      transcriptionShadowQuill = new Quill(transcriptionShadowQuillElement);
      state.transcriptionContent = transcriptionShadowQuillElement.children[0].innerHTML;

      notesShadowQuillElement.innerHTML = payload.withNotes || "";
      notesShadowQuill = new Quill(notesShadowQuillElement);
      state.transcriptionWithNotes = notesShadowQuillElement.children[0].innerHTML;

      speechpartsShadowQuillElement.innerHTML = payload.withSpeechparts || "";
      speechpartsShadowQuill = new Quill(speechpartsShadowQuillElement);
      state.transcriptionWithSpeechparts = speechpartsShadowQuillElement.children[0].innerHTML;

    }
  },
  RESET(state) {

    console.log("STORE MUTATION transcription/RESET")
    state.transcription = false;
    state.transcriptionAlignments = [];
    state.transcriptionContent = false;
    state.transcriptionWithNotes = false;
    state.transcriptionWithSpeechparts = false;

    if (transcriptionShadowQuillElement) transcriptionShadowQuillElement.children[0].innerHTML = "";
    if (notesShadowQuillElement) notesShadowQuillElement.children[0].innerHTML = "";
    if (speechpartsShadowQuillElement) speechpartsShadowQuillElement.children[0].innerHTML = "";

  },
  LOADING_STATUS (state, payload) {
    state.transcriptionLoading = payload;
  },
  ALIGNMENTS(state, payload) {
    state.transcriptionAlignments = payload;
  },
  UPDATE (state, payload) {
    console.log("STORE MUTATION transcription/UPDATE")
    state.transcription = payload.transcription;
    state.transcriptionWithNotes = payload.withNotes;
    state.transcriptionWithSpeechparts = payload.withSpeechparts;
    state.transcriptionSaved = true;
  },
  CHANGED (state) {
    // transcription changed and needs to be saved
    console.log("STORE MUTATION transcription/CHANGED")
    state.transcriptionSaved = false;
  },
  ADD_OPERATION (state, payload) {

    console.log("STORE MUTATION transcription/ADD_OPERATION", payload)

    const deltaFilteredForContent = removeFromDelta(payload, ['note','speechpart']);
    const deltaFilteredForNotes = removeFromDelta(payload, ['segment','speechpart']);
    const deltaFilteredForSpeechparts = removeFromDelta(payload, ['note']);

    transcriptionShadowQuill.updateContents(deltaFilteredForContent);
    notesShadowQuill.updateContents(deltaFilteredForNotes);
    speechpartsShadowQuill.updateContents(deltaFilteredForSpeechparts);

    state.transcriptionContent = transcriptionShadowQuillElement.children[0].innerHTML;
    state.transcriptionWithNotes = notesShadowQuillElement.children[0].innerHTML;
    state.transcriptionWithSpeechparts = speechpartsShadowQuillElement.children[0].innerHTML;

  },
  SAVED (state) {
    // transcription changed and needs to be saved
    console.log("STORE MUTATION transcription/SAVED")
    state.transcriptionSaved = false;
  }

};

const actions = {

  fetch ({ commit, rootState }) {

    console.log('STORE ACTION transcription/fetch', rootState)

    commit('LOADING_STATUS', true);

    const doc_id = rootState.document.document.id;
    const user_id = rootState.user.author.id;


    this.dispatch('noteTypes/fetch').then(() => {
      return this.dispatch('speechpartTypes/fetch', doc_id);
    }).then(() => {
      return this.dispatch('notes/fetch', doc_id);
    }).then(() => {
      return this.dispatch('speechparts/fetch', { doc_id, user_id });
    })
    .then(() => {
      return this.dispatch('transcription/fetchAlignments', { doc_id, user_id });
    })
    .then(() => {

      return axios.get(`/adele/api/1.0/documents/${doc_id}/transcriptions/from-user/${user_id}`).then( response => {

        console.log('TRANSCRIPTION', response);
        if (response.data.errors && response.data.errors.status === 404) {
          console.log("NO transcription found");
          const emptyData = {
            transcription: " ",
            content: " ",
            withNotes: " ",
            withSpeechparts: " ",
          };
          commit('INIT', emptyData);
          commit('UPDATE', emptyData);
          return;
        }
        let transcription = {content : " ", notes: []};

        if (response.data.data && response.data.data.length !== 0) {
          transcription = response.data.data[0];
        }

        let quillContent = TEIToQuill(transcription.content);
        let content = insertSegments(quillContent, state.transcriptionAlignments, 'transcription');
        const withNotes = insertNotesAndSegments(quillContent, transcription.notes, state.transcriptionAlignments, 'transcription');
        const withSpeechparts = insertSpeechparts(quillContent, rootState.speechparts.speechparts);

        const data = {
          transcription: transcription,
          content: convertLinebreakTEIToQuill(content),
          withNotes: convertLinebreakTEIToQuill(withNotes),
          withSpeechparts: convertLinebreakTEIToQuill(withSpeechparts),
        }
        console.warn("ne pas oublier de mettre les vraies parties")

        commit('INIT', data)
        commit('UPDATE', data);
        commit('LOADING_STATUS', false);
      })

    })
    .then(() => {
      return this.dispatch('translation/fetch', { doc_id, user_id });
    });
  },
  fetchAlignments ({commit}, {doc_id, user_id}) {
    return axios.get(`/adele/api/1.0/documents/${doc_id}/transcriptions/alignments/from-user/${user_id}`).then( response => {
      // Check if response is 1 alignment or more
      console.log("STORE ACTION transcription/fetchAlignments", response)
      if (response.data.errors) {
        commit('ALIGNMENTS', []);
        return;
      }
      const alignments = response.data.data && Array.isArray(response.data.data[0]) ? response.data.data : [response.data.data]
      commit('ALIGNMENTS', alignments);
    })
  },
  save ({dispatch, rootState}, transcriptionWithNotes) {
    console.log('STORE ACTION transcription/save');

    return dispatch('saveContent')
      .then(reponse => {
        if (rootState.translation.translation.id) {
          // Saves alignment if translation exists

          console.log('   => saves');
          return dispatch('saveAlignment')
        }
          console.log('   => bypass');
        return true;
      })
      .then(reponse => dispatch('saveSpeechparts'))
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
  saveContent ({ state, rootGetters, rootState }) {
    console.log('STORE ACTION transcription/saveContent', rootState);
    const auth = rootGetters['user/authHeader'];
    const tei = quillToTEI(state.transcriptionContent);
    const sanitized = stripSegments(tei);
    const data = { data: [{
        "content" : sanitized,
        "username": rootState.user.author.username
      }]};
    const method  = (state.transcription && state.transcription.doc_id) ? axios.put : axios.post;
    return new Promise( ( resolve, reject ) => {
      method(`/adele/api/1.0/documents/${rootState.document.document.id}/transcriptions`, data, auth)
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
  saveNotes ({ commit, rootState, state, rootGetters }) {

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
      axios.put(`/adele/api/1.0/documents/${rootState.document.document.id}/transcriptions/notes`, { data: notes }, auth)
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
  saveSpeechparts ({ commit, rootState, state, rootGetters }) {


    console.warn('STORE ACTION transcription/saveSpeechparts');

    // compute notes pointers
    let sanitizedWithSpeechparts = stripSegments(state.transcriptionWithSpeechparts);
    sanitizedWithSpeechparts = convertLinebreakQuillToTEI(sanitizedWithSpeechparts);
    const speechparts = computeSpeechpartsPointers(sanitizedWithSpeechparts);

    speechparts.forEach(sp => {
      let found = rootState.speechparts.speechparts[sp.index];
      sp.type_id = found.speech_part_type ? found.speech_part_type.id : found.type_id;
      if(found.note) sp.note = found.note;
    });

    const auth = rootGetters['user/authHeader'];
    const data = {
      username: rootState.user.author.username,
      speech_parts: speechparts
    }

    return new Promise( ( resolve, reject ) => {
      return axios.post(`/adele/api/1.0/documents/${rootState.document.document.id}/transcriptions/alignments/discours`, { data: data }, auth)
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
        username: rootState.user.author.username,
        ptr_list : pointers,
      }};
    return new Promise( ( resolve, reject ) => {
      axios.post(`/adele/api/1.0/documents/${rootState.document.document.id}/transcriptions/alignments`, data, auth)
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
  },
  reset({commit}) {
    commit('RESET')
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
