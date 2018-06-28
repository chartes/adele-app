import axios from "axios/index";

const state = {

  speechpartTypes: undefined

};

const mutations = {

  UPDATE (state, payload) {
    state.speechpartTypes = payload;
  }

};

const actions = {

  fetch ({ commit }) {
    axios.get(`/adele/api/1.0/speech-part-types`).then( response => {
      const respData = response.data.data;
      const isArray = Array.isArray(respData);
      const speechpartTypes = isArray ? respData : [respData];
      commit('UPDATE', speechpartTypes);
    });
  }

};

const getters = {

  speechpartTypes: state => state.speechpartTypes

};

const speechpartTypesModule = {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}

export default speechpartTypesModule;
