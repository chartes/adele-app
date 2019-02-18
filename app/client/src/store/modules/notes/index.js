import axios from "axios/index";

const state = {

  notes: [],
  newNote: false,

};

const mutations = {

  UPDATE_ALL (state, notes) {
    notes = Array.isArray(notes) ? notes : [notes];
    state.notes = notes;
  },
  NEW (state, note) {
    state.newNote = note;
    state.notes.push(note);
  },
  UPDATE_ONE (state, note) {
    state.notes = [...state.notes.filter(n => n.id !== note.id), note];
  }

};

const actions = {

  fetch ({ commit, rootState }, docId) {
    const config = { auth: { username: rootState.user.authToken, password: undefined }};
    const authorId = rootState.user.author.id;
    return axios.get(`/adele/api/1.0/documents/${docId}/notes/from-user/${authorId}`, config)
      .then( (response) => {
        commit('UPDATE_ALL', response.data.data)
      }).catch(function(error) {
        console.error('Error:', error)
      });
  },
  add ({ commit, getters, rootState }, newNote) {
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
        const note = response.data.data[0];
        commit('NEW', note);
      })
  },
  update ({ commit, getters, rootState }, note) {
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
        const note = response.data.data[0];
        commit('UPDATE_ONE', note);
      })
  },
  delete ({ commit, getters, rootState }, note) {
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
