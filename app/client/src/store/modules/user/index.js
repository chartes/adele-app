import axios from "axios/index";

const state = {

  currentUser: undefined,
  authToken: undefined,
  author: undefined,

};

const mutations = {

  UPDATE_CURRENT_USER (state, payload) {
    state.currentUser = payload;
    state.author = payload;
  },
  UPDATE_AUTH_TOKEN (state, payload) {
    state.authToken = payload;
  }

};

const actions = {

  getCurrentUser ({ commit }) {
    return axios.get('/adele/api/1.0/user').then( (response) => {
      commit('UPDATE_CURRENT_USER', response.data.data)
    })
  },
  setAuthToken ({ commit }, token) {
    commit('UPDATE_AUTH_TOKEN', token)
  },
  setAuthor({ commit }, authorId) {

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
  currentUserIsTeacher: state => {
    return checkRole(state.currentUser, 'teacher')
  },
  currentUserIsStudentstate: state => {
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
