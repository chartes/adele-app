import axios from 'axios';

const state = {

  canvasNames: [],
  currentCanvas: 0,
  fragments: [],
  textZones: [],
  loading: false,
  newFacsimileZone: false

};

const mutations = {


  INIT (state, payload) {

    state.canvasNames = payload;
    state.currentCanvas = 0;

  },

  LOADING (state, payload) {
    state.loading = payload;
  },

  UPDATE_ANNOTATIONS (state, payload) {
    state.loading = payload;
  },


};

const actions = {

  fetchCanvasNames ({ commit, dispatch, rootState }) {

    commit('LOADING', true);

    return axios.get(`/adele/api/1.0/documents/${rootState.document.document.id}/first-sequence`).then( response => {
      let data = response.data.data;
      console.log("STORE ACTION facsimile/fetchCanvasNames")
      if (!data || !data.canvases) return;
      let canvasNames = data.canvases.map((canvas) => {
        let idParts = canvas['@id'].split('/');
        return idParts[idParts.length - 1];
      });
      commit('INIT', canvasNames);
      return true;

    })
    .then(reponse => dispatch('fetchAnnotations'))

  },
  fetchAnnotations ({ commit, rootState, state }) {

    commit('LOADING', true);


    const doc_id = rootState.document.document.id;
    const user_id = rootState.user.author.id;
    const canvas = state.canvasNames[state.currentCanvas];

    return axios.get(`/adele/api/1.0/documents/${doc_id}/annotations/${canvas}/fragments/from-user/${user_id}`).then( response => {
      let data = response.data.data;
      console.log("STORE ACTION facsimile/fetchAnnotations", response.data);
      //commit('UPDATE_ANNOTATIONS', annotations);
      commit('LOADING', false);

    });

  },

};

const getters = {};

const facsimileModule = {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}

export default facsimileModule;
