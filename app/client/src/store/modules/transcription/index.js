import axios from 'axios';
import TEItoQuill,{insertNotes} from '../../../modules/quill/TEIConversion'

const state = {

  transcription: undefined,
  transcriptionFormatted: undefined,
  transcriptionSaved: false

};

const mutations = {

  UPDATE_TRANSCRIPTION (state, payload) {
    console.log("UPDATE_TRANSCRIPTION")
    state.transcription = payload.raw;
    state.transcriptionFormatted = payload.formatted;
    state.transcriptionSaved = true;
  },
  TRANSCRIPTION_CHANGED (state) {
    console.log("TRANSCRIPTION_CHANGED")
    state.transcriptionSaved = false;
  }

};

const actions = {

  getTranscription ({ commit, getters }) {
    const doc_id = getters.document.id;
    const user_id = getters.currentUser.id;

    this.dispatch('getNoteTypes').then(() => {
      return this.dispatch('getNotes', getters.document.id);
    }).then(() => {

      console.log('getTranscription', getters.document, getters.currentUser)
      // `/api/1.0/documents/${doc_id}/transcriptions/from/${user_id}`
      axios.get(`/api/1.0/documents/${doc_id}/transcriptions`).then( response => {

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

        const content = transcription.content;
        const notes = transcription.notes;
        const formatted = insertNotes(content, notes);

        //console.log('formatted', formatted)

        commit('UPDATE_TRANSCRIPTION', { raw: transcription, formatted: formatted });
      })


    });
  },
  transcriptionChanged ({ commit }) {
    commit('TRANSCRIPTION_CHANGED', false)
  },
  saveTranscription ({ commit }, newTranscription) {
    commit('UPDATE_TRANSCRIPTION', newTranscription)
  }

};

const getters = {
  transcription: state => {console.log("transcription"); return state.transcription},
  transcriptionFormatted: state => {console.log("transcription"); return state.transcriptionFormatted},
  transcriptionContent: state => !!state.transcription ? state.transcription.content : null,
  transcriptionIsSaved: state => state.transcriptionSaved
};

const transcriptionModule = {
  state,
  mutations,
  actions,
  getters
}

export default transcriptionModule;
