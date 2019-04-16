import axios from 'axios';

const state = {

  document: undefined,
  documents: [],

};

const mutations = {

  UPDATE_DOCUMENT (state, payload) {
    state.document = payload;
  },
  UPDATE_ALL (state, payload) {
    state.documents = payload;
  },
  PARTIAL_UPDATE_DOCUMENT(state, payload) {
    state.document =  {
      ...state.document,
      ...payload
    };
  },
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
  setValidationStage ({ commit }, {validationStage, validationStageLabel}) {
    commit('PARTIAL_UPDATE_DOCUMENT', {validation_stage: validationStage, validation_stage_label: validationStageLabel})
  },
};

const getters = {

  document: state => state.document,
  manifestURL: state => {
    const manifest_url = `/adele/api/1.0/documents/${state.document.id}/manifest`;
    return state.document && state.document.images &&  state.document.images.length > 0 ? manifest_url : null
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
