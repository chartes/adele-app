import axios from 'axios';

const state = {

  transcription: undefined,
  transcriptionSaved: false

};

const mutations = {

  UPDATE_TRANSCRIPTION (state, payload) {
    state.transcription = payload;
    state.transcriptionSaved = true;
  }

};

const actions = {

  getTranscription ({ commit }, id) {
    console.log("Store transcription getDocument", id)
    axios.get('/api/transcription/'+id).then( (response) => {
      commit('UPDATE_TRANSCRIPTION', response.data)
  })
  }

};

const getters = {

    transcription: state => state.transcription,
  isTranscriptionSaved: state => state.transcriptionSaved
};

const transcriptionModule = {
  state,
  mutations,
  actions,
  getters
}

export default transcriptionModule;
