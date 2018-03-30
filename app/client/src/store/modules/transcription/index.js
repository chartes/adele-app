import axios from 'axios';
import TEItoQuill from '../../../modules/quill/TEIConversion'

const state = {

  transcription: undefined, /*{
    content: '<p>Om<abbr>n</abbr>ib<abbr>us</abbr> presentes litteras inspecturis, . . officialis Belvacensis, salutem in Domino.<br>Noverint universi quod in nostra constituti presentia Ricardus dictus de Gres de Sancto Felice et Aya ejus uxor et Eufemia eorum filia recognoverunt se imperpetuum vendidisse pro communi eorum utilitate ac necessitate abbati et conventui Sancti Geremari Flaviacensis quamdam peciam terre sementis quam habebant ex caduco Asceline de Amuchi, matertere dicti Ricardi, circiter sex minas continentem, sitam ante mesum de Amuchi, dictorum abbatis et conventus, quam ab eisdem abbate et conventu tenebant ad campipartem,'
  },*/
  transcriptionSaved: false

};

const mutations = {

  UPDATE_TRANSCRIPTION (state, payload) {
    state.transcription = payload;
    state.transcriptionSaved = true;
  }

};

const actions = {

  getTranscription ({ commit, getters }) {
    console.log('getTranscription', getters.document, getters.currentUser)
    const doc_id = getters.document.id;
    const user_id = getters.currentUser.id;
    axios.get(`/api/1.0/document/${doc_id}/transcription/from/${user_id}`).then( (response) => {

      /*response.data = {
      content: '<p>Om<ex>n</ex>ib<abbr>us</abbr> presentes <strong>litteras inspecturis</strong>, . . officialis Belvacensis, salutem in Domino.<br>Noverint universi quod in nostra constituti presentia Ricardus dictus de Gres de Sancto Felice et Aya ejus uxor et Eufemia eorum filia recognoverunt se imperpetuum vendidisse pro communi eorum utilitate ac necessitate abbati et conventui Sancti Geremari Flaviacensis quamdam peciam terre sementis quam habebant ex caduco Asceline de Amuchi, matertere dicti Ricardi, circiter sex minas continentem, sitam ante mesum de Amuchi, dictorum abbatis et conventus, quam ab eisdem abbate et conventu tenebant ad campipartem,'
      }*/


      commit('UPDATE_TRANSCRIPTION', response.data.data)


    });
  }

};

const getters = {

  transcription: state => state.transcription,
  transcriptionContent: state => state.transcription.content,
  transcriptionIsSaved: state => state.transcriptionSaved
};

const transcriptionModule = {
  state,
  mutations,
  actions,
  getters
}

export default transcriptionModule;
