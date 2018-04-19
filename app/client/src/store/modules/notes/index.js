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
    return axios.get(`/api/1.0/documents/${docId}/notes/from-user/${getters.currentUser.id}`)
      .then( (response) => {
        commit('UPDATE_NOTES', response.data.data.notes)
      })
  },
  addNote ({ commit, getters }, newNote) {
    console.log("addNote", newNote);
    return axios.post(`/api/1.0/notes`, newNote)
      .then( (response) => {
        console.log(response)
        //commit('UPDATE_NOTES', response.data.data.notes)
      })
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
