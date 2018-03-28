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

    getDocument ({ commit }, id) {
      console.log("Store document getDocument", id)
        axios.get('/api/document/'+id).then( (response) => {
            commit('UPDATE_DOCUMENT', response.data)
        })
    }

};

const getters = {

    document: state => state.document,
    manifestURL: state => {
      console.log("manifest_url", state.document.images &&  state.document.images.length > 0 ? state.document.images[0].manifest_url : null)
      return state.document.images &&  state.document.images.length > 0 ? state.document.images[0].manifest_url : null
    }

};

const documentModule = {
    state,
    mutations,
    actions,
    getters
}

export default documentModule;
