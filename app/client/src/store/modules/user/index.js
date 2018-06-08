import axios from "axios/index";

const state = {

  currentUser: undefined,
  authToken: undefined

};

const mutations = {

  UPDATE_CURRENT_USER (state, payload) {
    state.currentUser = payload;
  },
  UPDATE_AUTH_TOKEN (state, payload) {
    state.authToken = payload;
  }

};

const actions = {

  getCurrentUser ({ commit }) {
    return axios.get('/api/1.0/user').then( (response) => {
      commit('UPDATE_CURRENT_USER', response.data.data)
    })
  },
  setAuthToken ({ commit }, token) {
    commit('UPDATE_AUTH_TOKEN', token)
  }

};

const checkRole = (user, role) => {
  user && user.role === role
};

const getters = {

  authToken: state => state.authToken,
  authHeader: state => { return { auth: { username: state.authToken, password: undefined }}},
  currentUser: state => state.currentUser,
  currentUserIsAdmin: state => {
    return checkRole(state.currentUser, 'admin')
  },
  currentUserIsProfessor: state => {
    return checkRole(state.currentUser, 'professor')
  },
  currentUserIsStudentstate: state => {
    return checkRole(state.currentUser, 'student')
  }
};

const userModule = {
  state,
  mutations,
  actions,
  getters
}

export default userModule;
