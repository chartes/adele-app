import axios from "axios/index";

const editorsById = {};

const state = {

  editors: [],

};

const mutations = {

  UPDATE (state, payload) {
    state.editors = payload;
  }

};

const actions = {

  fetch ({ commit }) {
    axios.get(`/api/1.0/editors`).then( response => {
      const respData = response.data.data;
      const isArray = Array.isArray(respData);
      const editors = isArray ? respData : [respData];
      commit('UPDATE', editors)
    });
  }

};

const getters = {

};

const editorsModule = {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}

export default editorsModule;
