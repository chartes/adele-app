import axios from "axios/index";

const state = {

  speechparts: [],
  newSpeechpart: false,
  mouseOver: false,
  mouseOverY: 0,

};

const mutations = {

  UPDATE_ALL (state, speechparts) {
    state.speechparts = speechparts;
  },
  NEW (state, speechpart) {
    state.newSpeechpart = speechpart;
    state.speechparts.push(speechpart);
  },
  MOUSE_OVER (state, { speechpart, posY}) {
    state.mouseOver = speechpart;
    state.mouseOverY = posY;
  },
  UPDATE_ONE (state, speechpart) {
    state.speechparts = [...state.speechparts.filter(sp => sp.id !== speechpart.id), speechpart];
  }

};

const actions = {

  fetch ({ commit, getters, rootGetters }, { doc_id, user_id }) {
    return axios.get(`/adele/api/1.0/documents/${doc_id}/transcriptions/alignments/discours/from-user/${user_id}`)
      .then( (response) => {
        commit('UPDATE_ALL', response.data.data)
      }).catch(function(error) {
        console.log(error);
      });
  },
  add ({ commit, getters, rootState }, newSpeechpart) {
    commit('NEW', newSpeechpart);
  },
  mouseover ({ commit, getters, rootState }, { speechpart, posY} ) {
    commit('MOUSE_OVER', { speechpart, posY });
  },

  update ({ commit, getters, rootState }, speechpart) {
    return commit('UPDATE_ONE', speechpart);
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
        const speechpart = response.data.data;
        commit('UPDATE_ONE', speechpart);
        return speechpart;
      })
  },
  delete ({ commit, getters, rootState }, speechpart) {
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
