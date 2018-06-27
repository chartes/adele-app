import axios from 'axios';

const state = {

  document: undefined

};

const mutations = {

  UPDATE_DOCUMENT (state, payload) {
    state.document = payload;
  }

};

const actions = {

  fetch ({ commit }, id) {
    return axios.get(`/adele/api/1.0/documents/${id}`).then( (response) => {
      commit('UPDATE_DOCUMENT', response.data.data)
    })
  }

};

const getters = {

  document: state => state.document,
  manifestURL: state => {
    return state.document && state.document.images &&  state.document.images.length > 0 ? state.document.images[0].manifest_url : null
  }

};

const documentModule = {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}

export default documentModule;
