import axios from "axios/index";

const state = {

  languages: [],

};

const mutations = {

  UPDATE (state, payload) {
    state.languages = payload;
  }

};

const actions = {

  fetch ({ commit }) {
    axios.get(`/adele/api/1.0/languages`).then( response => {
      const respData = response.data.data;
      const isArray = Array.isArray(respData);
      const languages = isArray ? respData : [respData];
      commit('UPDATE', languages)
    });
  }

};

const getters = {

};

const languagesModule = {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}

export default languagesModule;
