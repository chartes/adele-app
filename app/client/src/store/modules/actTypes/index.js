import axios from "axios/index";

const state = {

  actTypes: []

};

const mutations = {

  UPDATE (state, payload) {
    state.actTypes = payload;
  }

};

const actions = {

  fetch ({ commit }) {
    axios.get(`/api/1.0/acte-types`).then( response => {
      const respData = response.data.data;
      const isArray = Array.isArray(respData);
      const actTypes = isArray ? respData : [respData];
      commit('UPDATE', actTypes)
    });
  }

};

const getters = {

};

const actTypesModule = {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}

export default actTypesModule;
