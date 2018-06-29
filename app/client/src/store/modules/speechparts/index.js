import axios from "axios/index";

const state = {

  notes: [],
  newSpeechpart: false,

};

const mutations = {

  UPDATE_ALL (state, notes) {
    console.log("UPDATE_SPEECHPARTS");
    state.notes = notes;
  },
  NEW (state, note) {
    state.newSpeechpart = note;
    state.notes.push(note);
    console.log("ADD_NEW_SPEECHPART", state.newSpeechpart);
  },
  UPDATE_ONE (state, note) {
    state.notes.push(note);
    console.log("UPDATE_SPEECHPART", note);
    let foundSpeechpart = state.notes.find(n => n.id === note.id);
    console.log('foundSpeechpart', foundSpeechpart)
  }

};

const actions = {

  fetch ({ commit, getters, rootGetters }, docId) {
    console.log('STORE ACTION notes/fetch')
    return axios.get(`/adele/api/1.0/documents/${docId}/notes`)
      .then( (response) => {
        commit('UPDATE_ALL', response.data.data)
      }).catch(function(error) {
        console.log(error);
      });
  },
  add ({ commit, getters, rootState }, newSpeechpart) {
    console.log("STORE ACTION addSpeechpart", newSpeechpart, rootState);
    const docId = rootState.document.document.id;
    const config = { auth: { username: rootState.user.authToken, password: undefined }};
    const newSpeechparts = {
      data: {
        username : rootState.user.currentUser.username,
        speech_parts : [{
          type_id : newSpeechpart.type_id,
          ptr_start: -1,
          ptr_end: -1,
          note: newSpeechpart.note,
        }]
      }
    };

    return axios.post(`/adele/api/1.0/documents/${docId}/transcriptions/alignments/discours`, newSpeechparts, config)
      .then( response => {
        const speechpart = response.data.data;
        console.log("STORE ACTION addSpeechpart saved", response)
        commit('NEW', speechpart);
      })
  },
  update ({ commit, getters, rootState }, note) {
    console.log("STORE ACTION updateSpeechpart", note);
    const config = { auth: { username: rootState.user.authToken, password: undefined }};
    const theSpeechpart = {
      data: [{
        "username": rootState.user.currentUser.username,
        "id": note.id,
        "type_id": note.type_id,
        "content": note.content
      }]
    };
    return axios.put(`/adele/api/1.0/notes`, theSpeechpart, config)
      .then( response => {
        console.log(response.data)
        const note = response.data.data;
        commit('UPDATE_ONE', note);
      })
  },
  delete ({ commit, getters, rootState }, note) {
    console.log("STORE ACTION updateSpeechpart", note);
    const config = { auth: { username: rootState.user.authToken, password: undefined }};
    const theSpeechpart = {
      data: [{
        "username": rootState.user.currentUser.username,
        "id": note.id,
        "type_id": note.type_id,
        "content": note.content
      }]
    };
    return axios.delete(`/adele/api/1.0/notes`, theSpeechpart, config)
      .then( response => {
        console.log(response.data)
        const note = response.data.data;
        commit('UPDATE_ONE', note);
      })
  }

};

const getters = {

  speechparts: state => state.speechparts,
  newSpeechpart: state => state.newSpeechpart,
  getSpeechpartById: (state) => (id) => {
    id = parseInt(id);
    return state.speechparts.find(speechpart => {
      return speechpart.id === id;
    });
  }

};

const speechpartsModule = {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}

export default speechpartsModule;
