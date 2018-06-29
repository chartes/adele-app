import axios from 'axios';

const state = {

  document: undefined,
  documents: [],

};

const mutations = {

  UPDATE_DOCUMENT (state, payload) {
    console.log('UPDATE_DOCUMENT', payload);
    state.document = payload;
  },
  UPDATE_ALL (state, payload) {
    state.documents = payload;
  }

};

const actions = {

  fetch ({ commit }, id) {
    return axios.get(`/adele/api/1.0/documents/${id}`).then( (response) => {
      commit('UPDATE_DOCUMENT', response.data.data)
    })
  },
  save ({ commit, rootGetters }, data) {

    const auth = rootGetters['user/authHeader'];

    return new Promise( ( resolve, reject ) => {
      axios.put(`/adele/api/1.0/documents`, { data: data }, auth)
        .then(response => {
          if (response.data.errors) {
            console.error("error", response.data.errors);
            reject(response.data.errors);
          } else {
            commit('UPDATE_DOCUMENT', response.data.data)
            resolve(response.data)
          }
        })
        .catch(error => {
          console.error("error", error)
          reject(error)
        });
    })
  },
  fetchAll ({ commit }, id) {
    return axios.get(`/adele/api/1.0/documents`).then( (response) => {
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
