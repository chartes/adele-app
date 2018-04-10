import axios from "axios/index";

const state = {

  noteTypes: undefined

};

const mutations = {

  UPDATE_NOTE_TYPES (state, payload) {
    console.log("UPDATE_NOTE_TYPES", payload)
    state.noteTypes = payload;
  }

};

const actions = {

  getNoteTypes ({ commit }) {
    axios.get(`/api/1.0/note-types`).then( response => {

      const respData = response.data.data;

      const isArray = Array.isArray(respData);
      const noteTypes = isArray ? respData : [respData];

      console.log('noteTypes', noteTypes);
      commit('UPDATE_NOTE_TYPES', noteTypes)

    });
  }

};

const getters = {

  noteTypes: state => state.noteTypes

};

const noteTypesModule = {
  state,
  mutations,
  actions,
  getters
}

export default noteTypesModule;
