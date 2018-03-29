import axios from "axios/index";

const state = {

  currentUser: {
      "active": true,
      "confirmed_at": null,
      "email": "julien.pilla@enc-sorbonne.fr",
      "first_name": "Julien",
      "id": 1,
      "last_name": "Pilla",
      "roles": [
          "admin",
          "student",
          "teacher"
      ],
      "username": "jpilla"
  },

};

const mutations = {

  UPDATE_CURRENT_USER (state, payload) {
    state.currentUser = payload;
  }

};

const actions = {

  getCurrentUser ({ commit }) {
    axios.get('/api/user').then( (response) => {
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
