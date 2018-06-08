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

  fetchNotes ({ commit, getters }, docId) {
    console.log('fetchNotes', docId, getters.currentUser.id)
    return axios.get(`/api/1.0/documents/${docId}/notes`)
      .then( (response) => {
        console.log(response)
        commit('UPDATE_NOTES', response.data.data)
      }).catch(function(error) {
        console.log(error);
      });
  },
  addNote ({ commit, getters, rootState }, newNote) {
    console.log("addNote", newNote, rootState);

    /**
     { "data": [
          {
            "username": "Eleve1",
            "transcription_username" : "AdminJulien",
            "note_type": 0,
            "content": "My first transcription note",
            "ptr_start": 20,
            "ptr_end": 80
          }
        ] }
     */

    const config = { auth: { username: rootState.user.authToken, password: undefined }};
    console.log("auth", config.auth)
    const newNotes = {
      data: [{ "username": rootState.user.currentUser.username,
        "transcription_username" : rootState.user.currentUser.username,
        "note_type": newNote.type_id,
        "content": newNote.content,
        "ptr_start": -1,
        "ptr_end": -1 }]
    }
    console.log("new nore", newNotes)

    return axios.post(`/api/1.0/documents/20/transcriptions/notes`, newNotes, config)
      .then( (response) => {
        console.log('new note added', response.data)
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
