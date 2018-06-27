import axios from "axios/index";

const state = {

  notes: [],
  newNote: false,

};

const mutations = {

  UPDATE_ALL (state, notes) {
    console.log("UPDATE_NOTES");
    state.notes = notes;
  },
  NEW (state, note) {
    state.newNote = note;
    state.notes.push(note);
    console.log("ADD_NEW_NOTE", state.newNote);
  },
  UPDATE_ONE (state, note) {
    state.notes.push(note);
    console.log("UPDATE_NOTE", note);
    let foundNote = state.notes.find(n => n.id === note.id);
    console.log('foundNote', foundNote)
  }

};

const actions = {

  fetch ({ commit, getters, rootGetters }, docId) {
    console.log('STORE ACTION notes/fetch')
    return axios.get(`/adele/api/1.0/documents/${docId}/notes`)
      .then( (response) => {
        commit('UPDATE_ALL', response.data.data)
      }).catch(function(error) {
        console.log(error);
      });
  },
  add ({ commit, getters, rootState }, newNote) {
    console.log("STORE ACTION addNote", newNote);
    const config = { auth: { username: rootState.user.authToken, password: undefined }};
    const newNotes = {
      data: [{
        "username": rootState.user.currentUser.username,
        "type_id": newNote.type_id,
        "content": newNote.content
      }]
    };
    return axios.post(`/adele/api/1.0/notes`, newNotes, config)
      .then( response => {
        const note = response.data.data;
        commit('NEW', note);
      })
  },
  update ({ commit, getters, rootState }, note) {
    console.log("STORE ACTION updateNote", note);
    const config = { auth: { username: rootState.user.authToken, password: undefined }};
    const theNote = {
      data: [{
        "username": rootState.user.currentUser.username,
        "id": note.id,
        "type_id": note.type_id,
        "content": note.content
      }]
    };
    return axios.put(`/adele/api/1.0/notes`, theNote, config)
      .then( response => {
        console.log(response.data)
        const note = response.data.data;
        commit('UPDATE_ONE', note);
      })
  },
  delete ({ commit, getters, rootState }, note) {
    console.log("STORE ACTION updateNote", note);
    const config = { auth: { username: rootState.user.authToken, password: undefined }};
    const theNote = {
      data: [{
        "username": rootState.user.currentUser.username,
        "id": note.id,
        "type_id": note.type_id,
        "content": note.content
      }]
    };
    return axios.delete(`/adele/api/1.0/notes`, theNote, config)
      .then( response => {
        console.log(response.data)
        const note = response.data.data;
        commit('UPDATE_ONE', note);
      })
  }

};

const getters = {

  notes: state => state.notes,
  newNote: state => state.newNote,
  getNoteById: (state) => (id) => {
    id = parseInt(id);
    return state.notes.find(note => {
      return note.id === id;
    });
  }

};

const notesModule = {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}

export default notesModule;
