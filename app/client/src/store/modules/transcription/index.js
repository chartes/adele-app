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
  insertFacsimileZones,
  stripSegments,
  computeNotesPointers,
  computeAlignmentPointers,
  computeSpeechpartsPointers,
  computeImageAlignmentsPointers
} from '../../../modules/quill/MarkupUtils'
import {filterDeltaOperations} from '../../../modules/quill/DeltaUtils'


const transcriptionShadowQuillElement = document.createElement('div');
const notesShadowQuillElement = document.createElement('div');
const speechpartsShadowQuillElement = document.createElement('div');
const facsimileShadowQuillElement = document.createElement('div');
let transcriptionShadowQuill;
let notesShadowQuill;
let speechpartsShadowQuill;
let facsimileShadowQuill;

const state = {

  transcriptionLoading: true,
  transcription: false,
  transcriptionContent: false,
  transcriptionWithNotes: false,
  transcriptionWithSpeechparts: false,
  transcriptionWithFacsimile: false,
  transcriptionSaved: true,
  transcriptionError: false,
  transcriptionAlignments: [],
  referenceTranscription: false,
  savingStatus: 'uptodate'

};

const mutations = {


  INIT(state, payload) {

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

      facsimileShadowQuillElement.innerHTML = payload.withFacsimile || "";
      facsimileShadowQuill = new Quill(facsimileShadowQuillElement);
      state.transcriptionWithFacsimile = facsimileShadowQuillElement.children[0].innerHTML;

    }
  },
  RESET(state) {

    console.log("STORE MUTATION transcription/RESET")
    state.transcription = false;
    state.transcriptionAlignments = [];
    state.transcriptionContent = false;
    state.transcriptionWithNotes = false;
    state.transcriptionWithSpeechparts = false;
    state.transcriptionWithFacsimile = false;

    if (transcriptionShadowQuillElement && transcriptionShadowQuillElement.children[0]) transcriptionShadowQuillElement.children[0].innerHTML = "";
    if (notesShadowQuillElement && notesShadowQuillElement.children[0]) notesShadowQuillElement.children[0].innerHTML = "";
    if (speechpartsShadowQuillElement && speechpartsShadowQuillElement.children[0]) speechpartsShadowQuillElement.children[0].innerHTML = "";
    if (facsimileShadowQuillElement && facsimileShadowQuillElement.children[0]) facsimileShadowQuillElement.children[0].innerHTML = "";

  },
  LOADING_STATUS (state, payload) {
    state.transcriptionLoading = payload;
  },
  SAVING_STATUS (state, payload) {
    console.log("STORE MUTATION transcription/SAVING_STATUS", payload)
    state.savingStatus = payload;
  },
  ALIGNMENTS(state, payload) {
    state.transcriptionAlignments = payload;
  },
  UPDATE (state, payload) {
    console.log("STORE MUTATION transcription/UPDATE")
    state.transcription = payload.transcription;
    state.transcriptionWithNotes = payload.withNotes;
    state.transcriptionWithSpeechparts = payload.withSpeechparts;
    state.transcriptionWithFacsimile = payload.withFacsimile;
  },
  CHANGED (state) {
    // transcription changed and needs to be saved
    console.log("STORE MUTATION transcription/CHANGED")
    state.transcriptionSaved = false;
  },
  ADD_OPERATION (state, payload) {

    console.log("STORE MUTATION transcription/ADD_OPERATION", payload.ops)

    const deltaFilteredForContent = filterDeltaOperations(transcriptionShadowQuill, payload, 'content')
    const deltaFilteredForNotes = filterDeltaOperations(notesShadowQuill, payload, 'notes')
    const deltaFilteredForSpeechparts = filterDeltaOperations(speechpartsShadowQuill, payload, 'speechparts')
    const deltaFilteredForFacsimile = filterDeltaOperations(facsimileShadowQuill, payload, 'facsimile')

    transcriptionShadowQuill.updateContents(deltaFilteredForContent);
    notesShadowQuill.updateContents(deltaFilteredForNotes);
    speechpartsShadowQuill.updateContents(deltaFilteredForSpeechparts);
    facsimileShadowQuill.updateContents(deltaFilteredForFacsimile);

    state.transcriptionContent = transcriptionShadowQuillElement.children[0].innerHTML;
    state.transcriptionWithNotes = notesShadowQuillElement.children[0].innerHTML;
    state.transcriptionWithSpeechparts = speechpartsShadowQuillElement.children[0].innerHTML;
    state.transcriptionWithFacsimile = facsimileShadowQuillElement.children[0].innerHTML;

  },
  SAVED (state) {
    // transcription saved
    console.log("STORE MUTATION transcription/SAVED")
    state.transcriptionSaved = true;
  }

};

const actions = {

  fetch ({ commit, rootState }) {

    commit('LOADING_STATUS', true);

    const doc_id = rootState.document.document.id;
    const user_id = rootState.user.author.id;
    console.log('STORE ACTION transcription/fetch', doc_id, user_id);

    this.dispatch('noteTypes/fetch')
      .then(() => this.dispatch('speechpartTypes/fetch', doc_id))
      .then(() => this.dispatch('commentaries/fetchTypes'))
      .then(() => this.dispatch('notes/fetch', doc_id))
      .then(() => this.dispatch('speechparts/fetch', { doc_id, user_id }))
      .then(() => this.dispatch('facsimile/fetchCanvasNames'))
      .then(() => this.dispatch('facsimile/fetchFragments'))
      .then(() => this.dispatch('facsimile/fetchAlignments'))
      .then(() => this.dispatch('transcription/fetchAlignments', { doc_id, user_id }))
      .then(() => this.dispatch('transcription/fetchTranscriptionFromUser', { doc_id, user_id }))
      .then(() => this.dispatch('translation/fetch', { doc_id, user_id }))
      .then(() => this.dispatch('commentaries/fetch', { doc_id, user_id }))
      .catch(err => {
        console.error("Une erreur est survenue", err)
      })

  },
  fetchTranscriptionFromUser ({commit, state, rootState}, {doc_id, user_id}) {
    return axios.get(`/adele/api/1.0/documents/${doc_id}/transcriptions/from-user/${user_id}`).then( response => {

      commit('LOADING_STATUS', false);

      if (response.data.errors && response.data.errors.status === 404) {
        console.warn("NO transcription found");
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
      const withFacsimile = insertFacsimileZones(quillContent, rootState.facsimile.alignments);

      const data = {
        transcription: transcription,
        content: convertLinebreakTEIToQuill(content),
        withNotes: convertLinebreakTEIToQuill(withNotes),
        withSpeechparts: convertLinebreakTEIToQuill(withSpeechparts),
        withFacsimile: convertLinebreakTEIToQuill(withFacsimile),
      }

      commit('INIT', data)
      commit('UPDATE', data);
    })
  },
  fetchAlignments ({commit}, {doc_id, user_id}) {
    return axios.get(`/adele/api/1.0/documents/${doc_id}/transcriptions/alignments/from-user/${user_id}`).then( response => {
      console.log("STORE ACTION transcription/fetchAlignments", response)
      if (response.data.errors) {
        commit('ALIGNMENTS', []);
        return;
      }
      const alignments = response.data.data && Array.isArray(response.data.data[0]) ? response.data.data : [response.data.data]
      commit('ALIGNMENTS', alignments);
    })
  },
  create ({ commit, rootState, rootGetters }) {
    const auth = rootGetters['user/authHeader'];
    const data = { data: [{
        "content" : '<p></p>',
        "username": rootState.user.currentUser.username
      }]};
    return new Promise( ( resolve, reject ) => {
      axios.post(`/adele/api/1.0/documents/${rootState.document.document.id}/transcriptions`, data, auth)
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
  save ({dispatch, commit, rootState}) {
    console.log('STORE ACTION transcription/save');

    commit('SAVING_STATUS', 'saving');

    return dispatch('saveContent')
      .then(response => {
        if (rootState.document.manifestUrl) {
          dispatch('saveImageAlignments')
        }
      })
      .then(reponse => {
        if (rootState.translation.translation.id) {
          // Saves alignment if translation exists
          return dispatch('saveAlignment')
        }
        return true;
      })
      .then(reponse => dispatch('saveSpeechparts'))
      .then(reponse => dispatch('saveNotes'))
      .then(reponse => {
        if (rootState.translation.translation) return dispatch('translation/save', null, {root:true})
        else return true;
      })
      .then(function(values) {
        console.log('all saved', values);
        commit('SAVED');
        commit('SAVING_STATUS', 'uptodate');
      })
      .catch( error => {
        console.log('something bad happened', error);
        commit('SAVING_STATUS', 'error');
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
  saveImageAlignments ({ commit, rootState, state, rootGetters }) {


    console.warn('STORE ACTION transcription/saveImageAlignments');

    // compute image alignments pointers
    let sanitizedWithFacsimile = stripSegments(state.transcriptionWithFacsimile);
    sanitizedWithFacsimile = convertLinebreakQuillToTEI(sanitizedWithFacsimile);
    const imageAlignments = computeImageAlignmentsPointers(sanitizedWithFacsimile);
    imageAlignments.forEach(ia => {
      let found = rootGetters['facsimile/getZoneById'](ia.zone_id);
      ia.canvas_idx = found.canvas_idx;
      ia.img_idx = found.img_idx;
    });

    const auth = rootGetters['user/authHeader'];
    const data = {
      username: rootState.user.author.username,
      alignments: imageAlignments
    }

    return new Promise( ( resolve, reject ) => {
      return axios.post(`/adele/api/1.0/documents/${rootState.document.document.id}/transcriptions/alignments/images`, { data: data }, auth)
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
    console.warn('STORE ACTION transcription/changed');
    commit('ADD_OPERATION', deltas)
    commit('CHANGED')
    commit('SAVING_STATUS', 'tobesaved')
  },
  translationChanged ({ commit }, deltas) {
    console.warn('STORE ACTION transcription/translationChanged');
    commit('CHANGED')
    commit('SAVING_STATUS', 'tobesaved')
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
