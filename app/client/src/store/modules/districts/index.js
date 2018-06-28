import axios from "axios/index";

const state = {

  districts: [],

};

const mutations = {

  UPDATE (state, payload) {
    state.districts = payload;
  }

};

const actions = {

  fetch ({ commit }) {
    axios.get(`/api/1.0/districts`).then( response => {
      const respData = response.data.data;
      const isArray = Array.isArray(respData);
      const districts = isArray ? respData : [respData];
      commit('UPDATE', districts)
    });
  }

};

const getters = {

};

const districtsModule = {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}

export default districtsModule;
