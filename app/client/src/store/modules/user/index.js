import axios from "axios/index";

const state = {

  currentUser: undefined,
  authToken: undefined,
  author: undefined,

};

const mutations = {

  UPDATE_CURRENT_USER (state, payload) {
    state.currentUser = payload;
    console.log('STORE MUTATION user/UPDATE_CURRENT_USER')
  },
  UPDATE_AUTHOR (state, payload) {
    state.author = payload;
    console.log('STORE MUTATION user/UPDATE_AUTHOR', state.author.id, state.author)
  },
  UPDATE_AUTH_TOKEN (state, payload) {
    state.authToken = payload;
  }

};

const actions = {

  getCurrentUser ({ commit, rootGetters }) {
    const auth = rootGetters['user/authHeader'];
    return axios.get('/adele/api/1.0/user', auth).then( (response) => {
      commit('UPDATE_CURRENT_USER', response.data.data)
      commit('UPDATE_AUTHOR', response.data.data)
    })
  },
  setAuthToken ({ commit }, token) {
    commit('UPDATE_AUTH_TOKEN', token)
  },
  setAuthor({ commit }, author) {
    console.log('STORE ACTION user/setAuthor', author.id, author)
    commit('UPDATE_AUTHOR', author)
  }

};

const checkRole = (user, role) => {
  return user && user.roles.indexOf(role) > -1;
};

const getters = {

  authToken: state => state.authToken,
  authHeader: state => { return { auth: { username: state.authToken, password: undefined }}},
  currentUser: state => state.currentUser,
  currentUserIsAdmin: state => {
    return checkRole(state.currentUser, 'admin')
  },
  currentUserIsAuthor: state => {
    return state.currentUser.id === state.author.id;
  },
  currentUserIsTeacher: state => {
    return checkRole(state.currentUser, 'teacher')
  },
  currentUserIsStudent: state => {
    return checkRole(state.currentUser, 'student')
  },

};

const userModule = {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}

export default userModule;
