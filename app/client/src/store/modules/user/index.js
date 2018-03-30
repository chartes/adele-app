import axios from "axios/index";

const state = {

  currentUser: undefined,

};

const mutations = {

  UPDATE_CURRENT_USER (state, payload) {
    state.currentUser = payload;
  }

};

const actions = {

  getCurrentUser ({ commit }) {
    return axios.get('/api/user').then( (response) => {
      commit('UPDATE_CURRENT_USER', response.data)
    })
  }

};

const checkRole = (user, role) => {
  user && user.role === role
};

const getters = {

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
