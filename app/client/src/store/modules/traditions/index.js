import axios from "axios/index";

const state = {

  traditions: [],

};

const mutations = {

  UPDATE (state, payload) {
    state.traditions = payload;
  }

};

const actions = {

  fetch ({ commit }) {
    axios.get(`/adele/api/1.0/traditions`).then( response => {
      const respData = response.data.data;
      const isArray = Array.isArray(respData);
      const traditions = isArray ? respData : [respData];
      commit('UPDATE', traditions)
    });
  }

};

const getters = {

};

const traditionsModule = {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}

export default traditionsModule;
