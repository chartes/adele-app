import axios from "axios/index";

const state = {

  countries: [],

};

const mutations = {

  UPDATE (state, payload) {
    state.countries = payload;
  }

};

const actions = {

  fetch ({ commit }) {
    axios.get(`/api/1.0/countries`).then( response => {
      const respData = response.data.data;
      const isArray = Array.isArray(respData);
      const countries = isArray ? respData : [respData];
      commit('UPDATE', countries)
    });
  }

};

const getters = {

};

const countriesModule = {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}

export default countriesModule;
