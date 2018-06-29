import axios from "axios/index";

const state = {

  institutions: []

};

const mutations = {

  UPDATE (state, payload) {
    state.institutions = payload;
  }

};

const actions = {

  fetch ({ commit }) {
    axios.get(`/adele/api/1.0/institutions`).then( response => {
      const respData = response.data.data;
      const isArray = Array.isArray(respData);
      const institutions = isArray ? respData : [respData];
      commit('UPDATE', institutions)
    });
  }

};

const getters = {

  institutionsSelect: state => {
    const options = state.institutions.map(i =>  ({ id: i.id, label: i.name }))
    options.unshift({ id: null, label: 'Non définie' });
    return options;
  }

};

const institutionsModule = {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}

export default institutionsModule;