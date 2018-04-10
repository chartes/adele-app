import axios from "axios/index";

const state = {

  notes: undefined,

};

const mutations = {

  UPDATE_NOTES (state, payload) {
    console.log("UPDATE_NOTES")
    state.notes = payload;
  }

};

const actions = {

  getNotes ({ commit, getters }, docId) {
    console.log('getNotes', docId, getters.currentUser.id)
    return axios.get(`/api/1.0/documents/${docId}/annotations/from/${getters.currentUser.id}`).then( (response) => {
      commit('UPDATE_NOTES', response.data.data.notes)
    })
  },
  addNote ({ commit, getters }) {

  }

};

const getters = {

  notes: state => state.notes,
  getNoteById: (state) => (id) => {
    id = parseInt(id);
    return state.notes.find(note => {
      return note.id === id;
    });
  }

};

const notesModule = {
  state,
  mutations,
  actions,
  getters
}

export default notesModule;
