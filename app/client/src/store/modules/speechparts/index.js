import axios from "axios/index";

const state = {

  speechparts: [],
  newSpeechpart: false,

};

const mutations = {

  UPDATE_ALL (state, speechparts) {
    console.log("speechpart UPDATE_ALL");
    state.speechparts = speechparts;
  },
  NEW (state, speechpart) {
    state.newSpeechpart = speechpart;
    state.speechparts.push(speechpart);
    console.log("speechpart NEW", state.newSpeechpart);
  },
  UPDATE_ONE (state, speechpart) {
    state.speechparts.push(speechpart);
    console.log("speechpart UPDATE_ONE", speechpart);
    let foundSpeechpart = state.speechparts.find(n => n.id === speechpart.id);
    console.log('speechpart foundSpeechpart', foundSpeechpart)
  }

};

const actions = {

  fetch ({ commit, getters, rootGetters }, docId) {
    console.log('STORE ACTION speechparts/fetch')
    return axios.get(`/adele/api/1.0/documents/${docId}/speechparts`)
      .then( (response) => {
        commit('UPDATE_ALL', response.data.data)
      }).catch(function(error) {
        console.log(error);
      });
  },
  add ({ commit, getters, rootState }, newSpeechpart) {
    console.log("STORE ACTION speechparts/add", newSpeechpart, rootState);
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
        console.log("STORE ACTION speechparts/add saved", response)
        commit('NEW', speechpart);
      })
  },
  update ({ commit, getters, rootState }, speechpart) {
    console.log("STORE ACTION speechparts/update", speechpart);
    const config = { auth: { username: rootState.user.authToken, password: undefined }};
    const theSpeechpart = {
      data: [{
        "username": rootState.user.currentUser.username,
        "id": speechpart.id,
        "type_id": speechpart.type_id,
        "content": speechpart.content
      }]
    };
    return axios.put(`/adele/api/1.0/speechparts`, theSpeechpart, config)
      .then( response => {
        console.log(response.data)
        const speechpart = response.data.data;
        commit('UPDATE_ONE', speechpart);
      })
  },
  delete ({ commit, getters, rootState }, speechpart) {
    console.log("STORE ACTION speechparts/delete", speechpart);
    const config = { auth: { username: rootState.user.authToken, password: undefined }};
    const theSpeechpart = {
      data: [{
        "username": rootState.user.currentUser.username,
        "id": speechpart.id,
        "type_id": speechpart.type_id,
        "content": speechpart.content
      }]
    };
    return axios.delete(`/adele/api/1.0/speechparts`, theSpeechpart, config)
      .then( response => {
        console.log(response.data)
        const speechpart = response.data.data;
        commit('UPDATE_ONE', speechpart);
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
