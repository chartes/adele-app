import axios from "axios/index";

const state = {

  commentaries: [],
  hasCommentaryTypes: [],
  commentaryTypes: []

};

const mutations = {

  UPDATE_TYPES (state, payload) {
    state.commentaryTypes = payload;
  },
  UPDATE (state, { commentaries, hasTypes}) {
    state.commentaries = commentaries;
    state.hasCommentaryTypes = hasTypes;
  }

};

const actions = {

  fetchTypes ({ commit }) {
    axios.get(`/adele/api/1.0/commentary-types`).then( response => {
      const respData = response.data.data;
      const isArray = Array.isArray(respData);
      const commentaryTypes = isArray ? respData : [respData];
      commit('UPDATE_TYPES', commentaryTypes)
    });
  },

  fetch ({ commit }, {doc_id, user_id}) {
    axios.get(`/adele/api/1.0/documents/${ doc_id }/commentaries/from-user/${ user_id }`).then( response => {
      const respData = response.data.data;
      const isArray = Array.isArray(respData);
      const commentaries = isArray ? respData : [respData];
      let hasTypes = {};
      commentaries.forEach(comm => { hasTypes[comm.type.label] = true; });
      commit('UPDATE', { commentaries, hasTypes })
    });
  }

};

const getters = {
  missingCommentaryTypes (state) {
    console.log("missingCommentaryTypes")
    return state.commentaryTypes.filter(ct => {
      console.log(" ", ct.label, !state.hasCommentaryTypes[ct.label])
      return !state.hasCommentaryTypes[ct.label]
    }
    )
  }
};

const commentariesModule = {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}

export default commentariesModule;
